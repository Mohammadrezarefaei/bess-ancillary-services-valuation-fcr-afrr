"""
BESS Ancillary Services (FCR & aFRR) & Multi-Market Revenue Stacking Engine.
Simulates pure wholesale arbitrage vs. German primary/secondary reserve participation.
"""

from typing import Dict, List
import numpy as np


class BatteryAncillaryEngine:

  def __init__(
      self,
      bess_power_mw: float = 10.0,
      bess_capacity_mwh: float = 20.0,
      bess_rte: float = 0.88,
      degradation_cost_eur_mwh: float = 8.5,
  ):
    self.power_mw = bess_power_mw
    self.capacity_mwh = bess_capacity_mwh
    self.rte = bess_rte
    self.deg_cost = degradation_cost_eur_mwh

  def simulate_market_strategies(
      self,
      spot_prices: List[float],
      fcr_prices: List[float],
      afrr_cap_prices: List[float],
  ) -> Dict[str, float]:
    """Evaluates 8,760h revenues for: Pure Arbitrage, Dedicated FCR, and Multi-Market Stacking."""
    spot = np.array(spot_prices)
    fcr = np.array(fcr_prices)
    afrr_cap = np.array(afrr_cap_prices)

    total_days = len(spot) // 24

    # 1. Pure Day-Ahead Arbitrage Baseline (1 full cycle per day)
    arb_daily_net = []
    for d in range(total_days):
      day_slice = spot[d * 24 : (d + 1) * 24]
      charge_idx = np.argsort(day_slice)[:2]
      discharge_idx = np.argsort(day_slice)[-2:]

      cost = np.mean(day_slice[charge_idx]) * self.capacity_mwh
      rev = np.mean(day_slice[discharge_idx]) * (self.capacity_mwh * self.rte)
      cycling_deg = (
          self.capacity_mwh + self.capacity_mwh * self.rte
      ) * self.deg_cost
      arb_daily_net.append(max(0.0, rev - cost - cycling_deg))

    annual_pure_arb = float(np.sum(arb_daily_net))

    # 2. Dedicated FCR Symmetrical Reserve
    # Capacity reservation minus 6% state-of-charge (SOC) rebalancing friction
    fcr_gross = float(np.sum(self.power_mw * fcr))
    annual_fcr_net = fcr_gross * 0.94

    # 3. Optimized Multi-Market Revenue Stacking (50% FCR + 50% aFRR + Peak Arbitrage)
    stacked_fcr = float(np.sum((self.power_mw * 0.5) * fcr))
    stacked_afrr_cap = float(np.sum((self.power_mw * 0.5) * afrr_cap))
    stacked_afrr_energy = float(
        np.sum((self.power_mw * 0.5) * 0.08 * 65.0)
    )  # 8% activation margin
    stacked_arb = annual_pure_arb * 0.45

    stacked_gross = (
        stacked_fcr + stacked_afrr_cap + stacked_afrr_energy + stacked_arb
    )
    annual_stacked_net = (
        stacked_gross * 0.96
    )  # 4% non-availability / penalties buffer

    uplift_pct = (
        (annual_stacked_net - annual_pure_arb) / annual_pure_arb
    ) * 100.0

    return {
        "annual_pure_arb_eur": round(annual_pure_arb, 2),
        "rev_per_mw_pure_arb": round(annual_pure_arb / self.power_mw, 2),
        "annual_fcr_net_eur": round(annual_fcr_net, 2),
        "rev_per_mw_fcr": round(annual_fcr_net / self.power_mw, 2),
        "annual_stacked_net_eur": round(annual_stacked_net, 2),
        "rev_per_mw_stacked": round(annual_stacked_net / self.power_mw, 2),
        "uplift_vs_arbitrage_pct": round(uplift_pct, 1),
        "stacked_fcr_eur": round(stacked_fcr, 2),
        "stacked_afrr_eur": round(stacked_afrr_cap + stacked_afrr_energy, 2),
        "stacked_arb_eur": round(stacked_arb, 2),
    }
