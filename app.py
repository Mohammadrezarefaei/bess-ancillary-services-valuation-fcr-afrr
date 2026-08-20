"""Streamlit Web App: BESS Ancillary Services Valuation & Revenue Stacking."""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.ancillary_engine import BatteryAncillaryEngine

st.set_page_config(
    page_title="BESS Ancillary Services & Revenue Stacking",
    page_icon="🔋",
    layout="wide"
)

st.title("🔋⚡ BESS Ancillary Services (FCR/aFRR) & Revenue Stacking Model")
st.markdown("Valuation model evaluating **Day-Ahead Wholesale Arbitrage** versus **German FCR / aFRR Reserve Power** auctions and multi-market stacking.")

# Sidebar Parameters
st.sidebar.header("⚙️ Battery Storage Specs")
power_mw = st.sidebar.slider("BESS Inverter Rating (MW)", 2.0, 50.0, 10.0, 2.0)
duration_h = st.sidebar.slider("Storage Duration (Hours)", 1.0, 4.0, 2.0, 0.5)
capacity_mwh = power_mw * duration_h
rte_pct = st.sidebar.slider("Round-Trip Efficiency (%)", 80.0, 95.0, 88.0, 1.0) / 100.0
deg_cost = st.sidebar.slider("Degradation Cost (€/MWh throughput)", 4.0, 15.0, 8.5, 0.5)

st.sidebar.header("📊 Market Price Conditions")
fcr_base_price = st.sidebar.slider("Average FCR Price (€/MW/h)", 10.0, 35.0, 20.0, 1.0)
afrr_base_price = st.sidebar.slider("Average aFRR Capacity Price (€/MW/h)", 5.0, 30.0, 15.0, 1.0)

# Synthetic 8,760h Market Profile Generation (Cached)
@st.cache_data
def get_synthetic_market_data(fcr_base, afrr_base):
    np.random.seed(42)
    hours = 8760
    h_arr = np.arange(hours)
    
    # Day-Ahead Spot
    base_spot = 50.0 + 30.0 * np.sin(2 * np.pi * (h_arr % 24 - 8) / 24)
    vol_spot = np.random.normal(0, 35.0, hours)
    solar_drop = np.where((h_arr % 24 >= 11) & (h_arr % 24 <= 15), -40.0, 0.0)
    spot = np.clip(base_spot + vol_spot + solar_drop, -25.0, 260.0).tolist()
    
    # FCR & aFRR Capacity
    fcr = np.clip(fcr_base + 6.0 * np.cos(2 * np.pi * (h_arr % 24) / 24) + np.random.normal(0, 4.0, hours), 4.0, 45.0).tolist()
    afrr = np.clip(afrr_base + np.random.normal(0, 4.0, hours), 2.0, 35.0).tolist()
    
    return spot, fcr, afrr

spot_prices, fcr_prices, afrr_prices = get_synthetic_market_data(fcr_base_price, afrr_base_price)

engine = BatteryAncillaryEngine(
    bess_power_mw=power_mw,
    bess_capacity_mwh=capacity_mwh,
    bess_rte=rte_pct,
    degradation_cost_eur_mwh=deg_cost
)

results = engine.simulate_market_strategies(spot_prices, fcr_prices, afrr_prices)

col1, col2 = st.columns([1.6, 1])

with col1:
    st.subheader("📊 Specific Revenue by Market Strategy (€k / MW-yr)")
    strategies = ["Pure Arbitrage", "Dedicated FCR", "Revenue Stacking\n(FCR + aFRR + Spot)"]
    rev_vals = [
        results["rev_per_mw_pure_arb"] / 1000.0,
        results["rev_per_mw_fcr"] / 1000.0,
        results["rev_per_mw_stacked"] / 1000.0
    ]
    colors = ["#64748B", "#3B82F6", "#10B981"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(strategies, rev_vals, color=colors, width=0.55, edgecolor="#0F172A", alpha=0.9)
    ax.set_ylabel("Revenue [k€ / MW-year]", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6, axis="y")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1.5, f"€{height:.1f}k/MW",
                ha='center', va='bottom', fontsize=9.5, fontweight="bold")

    st.pyplot(fig)

with col2:
    st.subheader("💶 Asset Performance Metrics")
    st.metric("Multi-Market Net Revenue", f"€{results['annual_stacked_net_eur']:,.2f} / yr")
    st.metric("Specific Stacked Revenue", f"€{results['rev_per_mw_stacked']:,.0f} / MW-yr")
    st.metric("Commercial Stacking Uplift", f"+{results['uplift_vs_arbitrage_pct']:.1f} %", delta=f"{results['uplift_vs_arbitrage_pct']:.1f}% vs Arbitrage")
    st.metric("Pure Arbitrage Baseline", f"€{results['rev_per_mw_pure_arb']:,.0f} / MW-yr")

st.markdown("---")
st.caption("Models German balancing energy market rules (Regelenergie) demonstrating capacity reservation advantages over single-cycle spot price arbitrage.")
