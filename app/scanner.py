"""Public-data cross-exchange spread scanner. Does not place orders."""
from __future__ import annotations
import asyncio
from typing import Any
import httpx
from app.config import settings

BINANCE = "https://api.binance.com/api/v3/ticker/bookTicker"
BYBIT = "https://api.bybit.com/v5/market/tickers"
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT", "ADAUSDT", "LINKUSDT"]

async def _binance(client: httpx.AsyncClient, symbol: str) -> dict[str, float]:
    r = await client.get(BINANCE, params={"symbol": symbol})
    r.raise_for_status()
    d = r.json()
    return {"bid": float(d["bidPrice"]), "ask": float(d["askPrice"]), "bid_qty": float(d["bidQty"]), "ask_qty": float(d["askQty"])}

async def _bybit(client: httpx.AsyncClient, symbol: str) -> dict[str, float]:
    r = await client.get(BYBIT, params={"category": "spot", "symbol": symbol})
    r.raise_for_status()
    payload = r.json()
    rows = payload.get("result", {}).get("list", [])
    if payload.get("retCode") != 0 or not rows:
        raise ValueError(f"Bybit não retornou cotação spot para {symbol}")
    d = rows[0]
    return {"bid": float(d["bid1Price"]), "ask": float(d["ask1Price"]), "bid_qty": float(d["bid1Size"]), "ask_qty": float(d["ask1Size"])}

def _opportunity(symbol: str, buy_exchange: str, buy: dict[str, float], sell_exchange: str, sell: dict[str, float], fee_rate: float) -> dict[str, Any] | None:
    buy_price, sell_price = buy["ask"], sell["bid"]
    if buy_price <= 0 or sell_price <= 0:
        return None
    gross_pct = (sell_price / buy_price - 1) * 100
    # Approximate round-trip fees; actual account tiers and execution costs may differ.
    fee_pct = fee_rate * 2 * 100
    net_pct = gross_pct - fee_pct
    trade_quote = min(1000.0, buy["ask_qty"] * buy_price, sell["bid_qty"] * sell_price)
    return {
        "symbol": symbol, "buy_exchange": buy_exchange, "sell_exchange": sell_exchange,
        "buy_price": buy_price, "sell_price": sell_price,
        "gross_spread_pct": round(gross_pct, 5), "estimated_fees_pct": round(fee_pct, 5),
        "estimated_net_pct": round(net_pct, 5), "estimated_net_usdt": round(trade_quote * net_pct / 100, 5),
        "estimated_quote_size_usdt": round(trade_quote, 4),
        "buy_top_liquidity_usdt": round(buy["ask_qty"] * buy_price, 4),
        "sell_top_liquidity_usdt": round(sell["bid_qty"] * sell_price, 4),
        "profitable_after_estimated_fees": net_pct >= settings.min_net_spread_pct,
        "warning": "Estimativa baseada no melhor bid/ask; não inclui slippage completo, transferências, latência ou fills parciais."
    }

async def scan_symbol(client: httpx.AsyncClient, symbol: str, fee_rate: float | None = None) -> list[dict[str, Any]]:
    fee = settings.default_fee_rate if fee_rate is None else fee_rate
    results: list[dict[str, Any]] = []
    async def safe_fetch(fn):
        try:
            return await fn(client, symbol), None
        except Exception as exc:
            return None, str(exc)
    (bn, bn_err), (bb, bb_err) = await asyncio.gather(safe_fetch(_binance), safe_fetch(_bybit))
    if bn and bb:
        a = _opportunity(symbol, "Binance", bn, "Bybit", bb, fee)
        b = _opportunity(symbol, "Bybit", bb, "Binance", bn, fee)
        if a: results.append(a)
        if b: results.append(b)
    if not results and (bn_err or bb_err):
        results.append({"symbol": symbol, "error": "; ".join(x for x in [f"Binance: {bn_err}" if bn_err else "", f"Bybit: {bb_err}" if bb_err else ""] if x)})
    return results

async def scan(symbols: list[str] | None = None, fee_rate: float | None = None) -> dict[str, Any]:
    symbols = symbols or DEFAULT_SYMBOLS
    if not 0 <= (settings.default_fee_rate if fee_rate is None else fee_rate) <= 0.02:
        raise ValueError("fee_rate deve estar entre 0 e 0.02 (0% a 2% por lado).")
    timeout = httpx.Timeout(settings.request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        chunks = await asyncio.gather(*(scan_symbol(client, s.upper(), fee_rate) for s in symbols))
    opportunities = [row for chunk in chunks for row in chunk]
    opportunities.sort(key=lambda x: x.get("estimated_net_pct", -999), reverse=True)
    return {"mode": "public-data / read-only", "symbols_checked": symbols, "opportunities": opportunities,
            "note": "Scanner informativo. Nenhuma ordem é enviada. Valores estimados não garantem lucro."}
