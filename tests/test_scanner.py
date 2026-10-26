from app.scanner import _opportunity

def test_net_spread_subtracts_two_sides_of_fees():
    buy = {"ask": 100.0, "ask_qty": 20.0, "bid": 99.0, "bid_qty": 20.0}
    sell = {"bid": 101.0, "bid_qty": 20.0, "ask": 102.0, "ask_qty": 20.0}
    row = _opportunity("TESTUSDT", "A", buy, "B", sell, 0.001)
    assert row is not None
    assert row["gross_spread_pct"] == 1.0
    assert row["estimated_fees_pct"] == 0.2
    assert round(row["estimated_net_pct"], 5) == 0.8
    assert row["estimated_net_usdt"] > 0

def test_negative_spread_is_not_marked_profitable():
    buy = {"ask": 102.0, "ask_qty": 10.0, "bid": 101.0, "bid_qty": 10.0}
    sell = {"bid": 100.0, "bid_qty": 10.0, "ask": 103.0, "ask_qty": 10.0}
    row = _opportunity("TESTUSDT", "A", buy, "B", sell, 0.001)
    assert row is not None
    assert row["estimated_net_pct"] < 0
    assert row["profitable_after_estimated_fees"] is False
