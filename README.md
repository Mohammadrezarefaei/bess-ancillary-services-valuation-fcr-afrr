# 🔋⚡ BESS Ancillary Services (FCR & aFRR) Valuation & Revenue Stacking

[![CI Pipeline](https://img.shields.io/badge/CI%20Pipeline-passing-brightgreen?logo=github&style=flat-square)](https://github.com/Mohammadrezarefaei/bess-ancillary-services-valuation-fcr-afrr/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bess-ancillary-services-valuation-fcr-afrr-5o6bcphs5anjjvny6id.streamlit.app/)

A techno-economic valuation and multi-market revenue optimization framework for utility-scale **Battery Energy Storage Systems (BESS)**. Simulates and compares **Day-Ahead wholesale price arbitrage**, **Primary Reserve (FCR - Frequency Containment Reserve)**, and **Secondary Reserve (aFRR - automatic Frequency Restoration Reserve)** under German balancing power market rules (*Regelenergie*).

---

## 🚀 Live Interactive Demo
👉 **[Access the Live Streamlit Web App](https://bess-ancillary-services-valuation-fcr-afrr-5o6bcphs5anjjvny6id.streamlit.app/)**

---

## 📌 Revenue Stacking Architecture & Market Rules

Grid-scale batteries in European markets face diminishing marginal returns when relying solely on single-cycle daily spot arbitrage due to round-trip efficiency (RTE) losses and battery degradation. This framework models dynamic asset allocation across three revenue pillars:

1. **Wholesale Day-Ahead Arbitrage:**
   $$\text{Margin}_{\text{DA}} = \max \left( 0, P_{\text{discharge}} \cdot \eta_{\text{RTE}} - P_{\text{charge}} - C_{\text{deg}} \right)$$

2. **FCR (Primary Frequency Regulation):**
   * Symmetrical 4-hour capacity reservation product with 15-minute energy maintenance constraints and state-of-charge (SOC) balancing buffers.

3. **aFRR (Secondary Frequency Regulation):**
   * Asymmetric capacity reservation (positive/negative) coupled with dynamic activation probability calls and energy spread capture.

---

## 🔍 Key Empirical Insights

* **Revenue Uplift:** Co-optimizing capacity across FCR, aFRR, and high-spread wholesale arbitrage windows delivers a **40–60% revenue premium** over pure Day-Ahead cycling strategies.
* **Degradation Mitigation:** Frequency reserve products predominantly monetize capacity availability rather than heavy cycling throughput, substantially reducing battery cell aging and replacement provisions.
* **SOC Risk Provisioning:** Incorporates realistic penalties and rebalancing friction costs (4–6%) to maintain operational readiness and prevent non-availability charges.

---

## 🛠️ Software Architecture & Automated Testing
* **CI/CD Pipeline:** Fully automated testing via **GitHub Actions** (`pytest` validating multi-market revenue calculations, edge-case handling, and unit economics).
* **Modular Core Engine:** Implemented in `src/ancillary_engine.py`.
* **Tech Stack:** Python 3.11, NumPy, Pandas, Matplotlib, Streamlit, Pytest.
