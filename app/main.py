from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.scanner import DEFAULT_SYMBOLS, scan

app = FastAPI(
    title="ArbFlow",
    version="0.2.0",
    description="Painel e scanner de arbitragem cripto. Monitoramento público; execução real desativada.",
)

DASHBOARD_PATH = Path(__file__).with_name("dashboard.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "application": "ArbFlow",
        "mode": "read-only",
        "live_trading_enabled": False,
    }


@app.get("/api/scan")
async def api_scan(
    symbols: str | None = Query(
        default=None,
        description="Símbolos separados por vírgula, ex.: BTCUSDT,ETHUSDT",
    ),
    fee_rate: float | None = Query(default=None, ge=0, le=0.02),
):
    selected = (
        [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if symbols
        else DEFAULT_SYMBOLS
    )
    if not selected or len(selected) > 30:
        raise HTTPException(status_code=400, detail="Informe de 1 a 30 símbolos.")
    if any(not s.isalnum() or len(s) > 20 for s in selected):
        raise HTTPException(status_code=400, detail="Símbolo inválido.")
    try:
        return await scan(selected, fee_rate)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def dashboard():
    if not DASHBOARD_PATH.is_file():
        raise HTTPException(status_code=500, detail="Arquivo do painel não encontrado.")
    return HTMLResponse(DASHBOARD_PATH.read_text(encoding="utf-8"))
