import pandas as pd
import streamlit as st

from models import CASE, monopoly_optimum, capacity_check, price_game, case_rounded_costs, default_margin
from ui import header, lede, note


def render():
    header("NorthStar Appliances",
           "One company, five decisions. Each module changes what NorthStar knows, and each answer comes with the condition that would change it.")

    opt, cap, g, rr = monopoly_optimum(), capacity_check(CASE["cap_y1"]), price_game(), case_rounded_costs()
    chain = [
        ("1", "Price the launch", "What should NorthStar produce, how much, and at what price?",
         f"CAD {cap['p']:,.0f} for {cap['q']:,.0f} units in year 1; CAD {opt['p']:,.0f} once capacity expands."),
        ("2", "Face a rival", "How should NorthStar act when NovaHome, HomeHub and a provider respond?",
         f"Hold CAD 900: a price war cuts each firm from {g['C']/1e6:.2f}m to {g['P']/1e6:.2f}m."),
        ("3", "Source the board", "Where should the control board come from?",
         f"Asia at CAD {rr['Asia']['risk_adjusted']:.0f} risk-adjusted, 10 below Mexico. Flips at an 8% tariff."),
        ("4", "Absorb shocks", "Which shocks matter, and when should NorthStar act?",
         "Demand is the big exposure: a recession costs 0.91m. Pilot AI rather than commit."),
        ("5", "Prove it worked", "Which interventions create value, and how do we know?",
         f"Pay for value, not activity. The warranty default nets about CAD {default_margin(0.20)['net']:,.0f}, if it survives a field test."),
    ]
    st.markdown(
        '<div class="ns-chain">' + "".join(
            f'<div><div class="n">{n}</div><div class="t">{t}</div><div class="q">{q}</div><div class="a">{a}</div></div>'
            for n, t, q, a in chain) + "</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.subheader("How to use the lab")
        lede("Pick a module in the sidebar. Every tool starts at the numbers on the slides, so what you see matches "
             "the lecture. Then work through three moves:")
        st.markdown(
            "1. **Change an assumption.** Each slider shows its case value in the help text.\n"
            "2. **Read the answer.** Every tool ends with an answer, the reason, and what NorthStar should do.\n"
            "3. **Find what flips it.** The ruler under each answer shows how far you are from the point where the "
            "recommendation reverses.")
        lede("Some tools ask you to predict before you look. Commit to a number first: the gap between your "
             "prediction and the model is where the learning is.")
        st.page_link("pages/Module_5_Live_Experiments.py", label="Open the live classroom experiments", icon="🧪")
    with c2:
        st.subheader("Case fact sheet")
        rows = [
            ("Demand (per year)", "Q = 26,000 − 20P (a fresh group of buyers each year)"),
            ("Unit cost, direct", "CAD 500 = manufacturing 430 + fulfilment 45 + payment 25"),
            ("Fixed operating cost", "CAD 2.0m a year"),
            ("Capacity", "7,000 units in year 1; 15,000 in year 2"),
            ("Retail channel", "HomeHub keeps 25%; retail unit cost CAD 455"),
            ("AI system", "CAD 2.4m upfront (600k a year at 8%), saves CAD 100 a unit"),
            ("Rival (year 2)", "NovaHome, same costs; both at 900 sell 7,000 each"),
            ("Control board", "Canada 185 · Mexico 150 · Asia 125 (quotes, CAD)"),
            ("Exchange rate", "1.40 CAD per USD"),
        ]
        st.dataframe(pd.DataFrame(rows, columns=["Parameter", "Value"]), hide_index=True, width="stretch")
        note("Numbers are illustrative and consistent across all five modules and the slides.")
