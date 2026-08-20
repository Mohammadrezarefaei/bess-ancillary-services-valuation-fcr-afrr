"""Automated Pytest Suite for BESS Ancillary Services Engine."""

import pytest
from src.ancillary_engine import BatteryAncillaryEngine


def test_ancillary_valuation_coherence():
  engine = BatteryAncillaryEngine(
      bess_power_mw=10.0,
      bess_capacity_mwh=20.0,
      bess_rte=0.88,
  )
  # 8,760 hours of synthetic market prices
  spot = [
      40.0 if (i % 24 >= 11 and i % 24 <= 14) else 110.0 for i in range(8760)
  ]
  fcr = [22.0] * 8760
  afrr = [18.0] * 8760

  res = engine.simulate_market_strategies(spot, fcr, afrr)

  assert res["annual_pure_arb_eur"] > 0.0
  assert res["annual_fcr_net_eur"] > 0.0
  assert res["annual_stacked_net_eur"] > 0.0
  # Revenue per MW check
  assert res["rev_per_mw_stacked"] == round(
      res["annual_stacked_net_eur"] / 10.0, 2
  )
  assert res["uplift_vs_arbitrage_pct"] > 0.0


def test_zero_capacity_behavior():
  engine = BatteryAncillaryEngine(
      bess_power_mw=0.0,
      bess_capacity_mwh=0.0,
  )
  res = engine.simulate_market_strategies([50.0] * 24, [10.0] * 24, [10.0] * 24)

  assert res["annual_pure_arb_eur"] == 0.0
  assert res["annual_fcr_net_eur"] == 0.0
  assert res["annual_stacked_net_eur"] == 0.0
