import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from models import (CASE, SCENARIOS, Scenario, capacity_check, monopoly_optimum, scaled_demand_outcome, general_inflation,
                    relative_shock_choice, npv, irr_annuity, annuity_factor, levy_incidence, rebate_capture,
                    ceiling_on_price_setter, exit_ceiling, scenario_outcome, option_value, demand_q, marginal_revenue)
from ui import (header, lede, answer, flip_ruler, cslider, predict, fig, show, note, step, m, cad,
                RED, BLUE, SLATE, BLUSH, INK, GREEN)

Y1 = CASE["cap_y1"]


def render():
    header("Module 4 · External shocks",
           "How can managers read the economic environment early and act before shocks fully reach the firm?")
    tabs = st.tabs(["Exposure map", "Inflation & rivals", "Rates & investment", "Taxes & subsidies", "Price controls",
                    "Standards & entry", "Scenarios & waiting", "Trigger plan"])

    base = capacity_check(Y1)["contribution"]

    # ------------------------------------------------------------------ exposure map
    with tabs[0]:
        lede("Slides 6 and 11. A headline matters only if it reaches NorthStar through a channel. Size each shock in CAD, "
             "then rank. Year-1 base contribution: " + m(base) + ".")
        c1, c2 = st.columns([1, 1.6])
        with c1:
            rec = cslider("Recession: demand fall (%)", "m4_x_rec", 0, 50, 30, 5) / 100
            slow = cslider("Housing slowdown: demand fall (%)", "m4_x_slow", 0, 40, 15, 5) / 100
            shock = cslider("Unit-cost shock (CAD)", "m4_x_cost", 0, 150, 50, 5)
            r_hi = cslider("Financing rate after a hike (%)", "m4_x_rate", 8, 18, 12, 1) / 100
            fx_hi = cslider("CAD per USD after a fall", "m4_x_fx", 1.40, 1.80, 1.50, 0.01)
        items = [
            ("Recession", "Volume", scaled_demand_outcome(1 - rec)["contribution"] - base),
            ("Housing slowdown", "Volume", scaled_demand_outcome(1 - slow)["contribution"] - base),
            ("Unit-cost shock", "Margin (no pass-through at capacity)", capacity_check(Y1, CASE["mc"] + shock)["contribution"] - base),
            ("Rate hike", "AI project NPV", npv(CASE["ai_saving"] * Y1, r_hi) - npv(CASE["ai_saving"] * Y1, CASE["rate"])),
            ("Weaker CAD", "Imported board cost", -(125 / CASE["fx"]) * (fx_hi - CASE["fx"]) * CASE["boards"]),
            ("Rate hike", "Inventory carrying cost",
             -7.0 * ((CASE["carry"] + (r_hi - CASE["rate"])) / CASE["carry"] - 1) * CASE["boards"]),
        ]
        items.sort(key=lambda x: x[2])
        with c2:
            f = fig(360, "Change in year-1 contribution (or NPV), CAD m", "")
            f.add_bar(y=[f"{a} · {b}" for a, b, _ in items], x=[v / 1e6 for _, _, v in items], orientation="h",
                      marker_color=[RED if v < -2e5 else "#D6A2AC" for _, _, v in items],
                      text=[f"{v/1e6:+.2f}m" for _, _, v in items], textposition="outside")
            f.update_yaxes(autorange="reversed")
            show(f, "m4_x_fig")
        answer(f"Largest exposure: {items[0][0].lower()} ({items[0][2]/1e6:+.2f}m)",
               "Demand shocks dwarf currency and inventory-financing effects for NorthStar.",
               "Watch the order book and housing data first, costs relative to rivals second, the CAD last.")
        st.subheader("Why a demand fall lowers the price only sometimes (slide 6)")
        s = 1 - slow
        r = scaled_demand_outcome(s)
        flip_ruler("Demand as a share of plan", s, 0.875, 0.5, 1.2, fmt=lambda v: f"{v:.2f}×",
                   left="Capacity slack: price 900", right="Capacity binds: price ≥ 950")
        note(f"At {s:.2f}× demand: price {r['p']:,.0f}, units {r['q']:,.0f}. With proportional demand the unconstrained price "
             "stays (1,300 + 500)/2 = 900: the price falls because capacity stops binding, not to stimulate demand.")

    # ------------------------------------------------------------------ inflation & rivals
    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("General inflation vs a cost shock (slide 7)")
            infl = cslider("General inflation (%)", "m4_i_gen", 0, 20, 10, 1) / 100
            cs = cslider("Cost shock on NorthStar only (CAD)", "m4_i_cs", 0, 150, 50, 5)
            gi = general_inflation(infl)
            sh = monopoly_optimum(CASE["mc"] + cs)
            st.dataframe(pd.DataFrame([
                {"Year 2 (spare capacity)": "Base", "Price": 900, "Units": 8000, "Real contribution": 3_200_000},
                {"Year 2 (spare capacity)": f"General inflation {infl:.0%}", "Price": gi["p"], "Units": gi["q"], "Real contribution": gi["real_contribution"]},
                {"Year 2 (spare capacity)": f"Cost shock +{cs}", "Price": sh["p"], "Units": sh["q"], "Real contribution": sh["contribution"]},
            ]).style.format({"Price": "{:,.0f}", "Units": "{:,.0f}", "Real contribution": "CAD {:,.0f}"}), hide_index=True, width="stretch")
            answer("Only relative shocks are real",
                   "General inflation scales prices, costs and willingness to pay together; a cost shock does not.",
                   "Respond to changes in relative prices, not to the headline rate.")
        with c2:
            st.subheader("When rivals are not hit (slide 8)")
            cc = cslider("NorthStar's cost increase (CAD)", "m4_r_cc", 0, 300, 50, 10)
            hit = st.toggle("NovaHome faces the same shock", key="m4_r_hit", value=False)
            rs = relative_shock_choice(cc, hit)
            f = fig(260, "", "NorthStar contribution, CAD m")
            f.add_bar(x=["Hold 900", "Raise to 950"], y=[rs["hold"] / 1e6, rs["raise"] / 1e6], marker_color=[BLUE, RED],
                      text=[f"{rs['hold']/1e6:.2f}", f"{rs['raise']/1e6:.2f}"], textposition="outside")
            show(f, "m4_r_fig")
            answer(rs["best"], "Raising alone loses share to NovaHome." if not hit else "If NovaHome raises too, matching recovers margin.",
                   "Pass costs through when rivals face them too; absorb a shock only you face.")
            if not hit:
                flip_ruler("NorthStar unit cost", CASE["mc"] + cc, rs["c_star"], 500, 800, fmt=lambda v: f"{v:,.0f}",
                           left="Absorb: hold 900", right="Raise alone")

    # ------------------------------------------------------------------ rates & investment
    with tabs[2]:
        lede("Slide 9. The AI project: CAD 2.4m upfront, five years, saving 100 per unit. Module 1's 600k a year is this cost annualized at 8%.")
        c1, c2 = st.columns([1, 1.5])
        with c1:
            rate = cslider("Financing rate (%)", "m4_n_rate", 0, 20, 8, 1) / 100
            units = cslider("Units a year", "m4_n_units", 3000, 9000, Y1, 100)
            save = cslider("Saving per unit (CAD)", "m4_n_save", 50, 150, CASE["ai_saving"], 5)
            v = npv(save * units, rate)
            irr = irr_annuity(save * units)
            predict("m4_n_pred", "the financing rate at which the AI project breaks even (%)?", irr * 100, tol=0.05,
                    fmt=lambda x: f"{x:.1f}")
            st.metric("NPV", m(v)); st.metric("Break-even rate", f"{irr:.1%}")
        with c2:
            rr = np.linspace(0, 0.25, 51)
            f = fig(320, "Financing rate", "NPV, CAD m")
            f.add_trace(go.Scatter(x=rr * 100, y=[npv(save * units, x) / 1e6 for x in rr], line=dict(color=RED, width=3), name="NPV"))
            f.add_hline(y=0, line_color=SLATE)
            f.add_vline(x=rate * 100, line_dash="dot", annotation_text=f"now {rate:.0%}")
            show(f, "m4_n_fig")
        answer(m(v), f"NPV = {save * units:,.0f} × {annuity_factor(rate, 5):.3f} − 2,400,000.",
               "Invest." if v > 0 else "Shelve or pilot: the project does not cover its cost of capital.")
        flip_ruler("Financing rate", rate * 100, irr * 100, 0, 25, fmt=lambda x: f"{x:.1f}%", left="NPV positive", right="NPV negative",
                   good_side="left")
        note("Other rate channels: inventory carrying cost (small: about 0.01m a year for a 4-point rise) and customers' "
             "financing of durable purchases (large: it moves demand).")

    # ------------------------------------------------------------------ taxes & subsidies
    with tabs[3]:
        lede("Slides 13–14. Who writes the cheque does not decide who bears a tax or captures a subsidy. Capacity and elasticity do.")
        binds = st.toggle("Capacity binds (year 1, 7,000 units)", key="m4_t_bind", value=False)
        cap = Y1 if binds else None
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("A per-unit eco-levy")
            levy = cslider("Levy per appliance (CAD)", "m4_t_levy", 0, 200, CASE["levy"], 5)
            lv = levy_incidence(levy, cap)
            f = fig(260, "", "CAD per unit")
            f.add_bar(x=["Buyers pay", "NorthStar bears"], y=[lv["buyer_share"], lv["firm_share"]], marker_color=[BLUE, RED])
            show(f, "m4_t_fig1")
            st.caption(f"Price {lv['p0']:,.0f} → {lv['p1']:,.0f}; contribution {m(lv['contrib0'])} → {m(lv['contrib1'])}.")
        with c2:
            st.subheader("A consumer rebate")
            reb = cslider("Rebate per appliance (CAD)", "m4_t_reb", 0, 500, CASE["rebate"], 10)
            rb = rebate_capture(reb, cap)
            f = fig(260, "", "CAD per unit")
            f.add_bar(x=["Buyers gain", "NorthStar gains"], y=[rb["buyer_gain"], rb["firm_gain_unit"]], marker_color=[BLUE, RED])
            show(f, "m4_t_fig2")
            st.caption(f"Sticker {rb['sticker0']:,.0f} → {rb['sticker1']:,.0f}; net price {rb['net_price']:,.0f}; units {rb['q0']:,.0f} → {rb['q1']:,.0f}.")
            if np.isfinite(rb["cost_per_extra"]):
                st.metric("Government cost per additional appliance", cad(rb["cost_per_extra"]))
        answer("Capacity decides the split",
               "With spare capacity, half of a levy or rebate passes through. With capacity binding, the price is already at "
               "the market-clearing level: the firm bears all of a levy and captures all of a rebate.",
               "Model incidence before a consultation; expect pressure if a rebate arrives while capacity binds.")

    # ------------------------------------------------------------------ price controls
    with tabs[4]:
        lede("Slides 15–16. A ceiling on a price-setter can raise output. Shortages come from binding capacity or from exit.")
        c1, c2 = st.columns([1, 1.6])
        with c1:
            ceil = cslider("Price ceiling (CAD)", "m4_c_ceil", 450, 1000, 850, 10)
            binds = st.toggle("Year 1: capacity 7,000", key="m4_c_bind", value=False)
            cp = ceiling_on_price_setter(ceil, Y1 if binds else None)
            ex = exit_ceiling()
            st.metric("Regime", cp["regime"]); st.metric("Units sold", f"{cp['q']:,.0f}")
            st.metric("Shortage", f"{cp['shortage']:,.0f}")
        with c2:
            a, b = CASE["a"], CASE["b"]
            q = np.linspace(0, a, 200)
            f = fig(380, "Quantity", "CAD per unit")
            f.add_trace(go.Scatter(x=q, y=(a - q) / b, name="Demand", line=dict(color=RED, width=3)))
            qq = np.linspace(0, a / 2, 100)
            f.add_trace(go.Scatter(x=qq, y=[marginal_revenue(x) for x in qq], name="MR", line=dict(color=INK, dash="dot")))
            f.add_trace(go.Scatter(x=[0, a], y=[CASE["mc"]] * 2, name="MC", line=dict(color=SLATE)))
            f.add_trace(go.Scatter(x=[0, a], y=[ceil] * 2, name="Ceiling", line=dict(color=BLUE, width=3)))
            if binds:
                f.add_vline(x=Y1, line_color=BLUE, line_dash="dash", annotation_text="capacity")
            f.update_yaxes(range=[0, 1400])
            show(f, "m4_c_fig")
        answer(cp["regime"], f"At a ceiling of {ceil:,.0f}, buyers want {cp['demand']:,.0f}; NorthStar sells {cp['q']:,.0f}.",
               "A ceiling does not remove scarcity; it changes who gets the product and whether the firm stays.")
        flip_ruler("Ceiling vs the exit point", ceil, ex, 450, 1000, left="NorthStar would not launch", right="NorthStar stays")
        with st.expander("Price floors (slide 16)"):
            fl = cslider("Price floor (CAD)", "m4_f_floor", 600, 1200, 1000, 10)
            free = monopoly_optimum()
            if fl <= free["p"]:
                st.write(f"Non-binding: NorthStar already charges {free['p']:,.0f}.")
            else:
                qf = demand_q(fl)
                st.write(f"Binding: NorthStar must charge {fl:,.0f} and sells {qf:,.0f}; contribution {m((fl - CASE['mc']) * qf)} "
                         f"vs {m(free['contribution'])}. A floor above the firm's chosen price hurts the firm too.")

    # ------------------------------------------------------------------ standards & entry
    with tabs[5]:
        lede("Slide 17. A rule that raises costs for everyone can still advantage the firm that already complies.")
        comp = cslider("Annual compliance cost for a non-compliant entrant (CAD)", "m4_s_cost", 0, 2_000_000, CASE["standard_cost"], 50_000)
        rival = (CASE["p_hold"] - CASE["mc"]) * CASE["q_both_hold"] - CASE["rival_fixed"] - comp
        st.metric("NovaHome's profit from entering and sharing the market", m(rival))
        answer("NovaHome stays out" if rival < 0 else "NovaHome enters",
               "Its 2.80m contribution must cover a 2.0m fixed cost plus compliance.",
               f"NorthStar keeps {m(monopoly_optimum()['contribution'] if rival < 0 else 2_800_000)}. "
               "Lobbying for standards that raise rivals' costs needs public-interest evidence to be credible.")
        flip_ruler("Compliance cost", comp, 800_000, 0, 2_000_000, fmt=m, left="Entry pays", right="Entry deterred")

    # ------------------------------------------------------------------ scenarios & waiting
    with tabs[6]:
        lede("Slides 19–21. Each scenario is a bundle of shocks. Edit the table: the outcomes, the AI NPV and the value of waiting update.")
        df = pd.DataFrame([{"Scenario": s.name, "Probability": s.prob, "Demand ×": s.demand_scale, "Unit cost": s.unit_cost,
                            "Rate": s.rate, "CAD per USD": s.fx, "AI saving / unit": s.ai_saving_per_unit} for s in SCENARIOS])
        ed = st.data_editor(df, key="m4_s_editor", hide_index=True, width="stretch", num_rows="fixed",
                            column_config={"Probability": st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.05),
                                           "Rate": st.column_config.NumberColumn(min_value=0.0, max_value=0.3, step=0.01)})
        scs = [Scenario(r["Scenario"], r["Probability"], r["Demand ×"], r["Unit cost"], r["Rate"], r["CAD per USD"],
                        r["AI saving / unit"]) for _, r in ed.iterrows()]
        outs = [scenario_outcome(s) for s in scs]
        st.dataframe(pd.DataFrame([{"Scenario": s.name, "Price": o["price"], "Units": o["units"], "Contribution": o["contribution"],
                                    "Operating profit": o["operating_profit"], "AI NPV": o["ai_npv"], "Asia's lead over Mexico": o["asia_lead"]}
                                   for s, o in zip(scs, outs)]).style.format(
            {"Price": "{:,.0f}", "Units": "{:,.0f}", "Contribution": "CAD {:,.0f}", "Operating profit": "CAD {:,.0f}",
             "AI NPV": "CAD {:,.0f}", "Asia's lead over Mexico": "{:.1f}"}), hide_index=True, width="stretch")
        psum = sum(s.prob for s in scs)
        if abs(psum - 1) > 1e-6:
            st.warning(f"Probabilities sum to {psum:.2f}; they should sum to 1.")
        ov = option_value([s.prob for s in scs], [o["ai_npv"] for o in outs], [s.rate for s in scs], [o["ai_npv"] > 0 for o in outs])
        c1, c2, c3 = st.columns(3)
        c1.metric("Invest now (expected NPV)", m(ov["now"])); c2.metric("Wait a year, invest only if good", m(ov["wait"]))
        c3.metric("Value of waiting", m(ov["value_of_waiting"]))
        answer(ov["best"], "Investing now commits 2.4m before NorthStar knows which future it is in; waiting forgoes a year.",
               "Pilot while the scenario is uncertain; commit when recession signals fade." if ov["best"].startswith("Wait")
               else "Invest now: the downside is unlikely enough that delay costs more than it saves.")
        st.subheader("How the choice depends on the recession probability")
        pr = np.linspace(0, 0.8, 41)
        nows, waits = [], []
        npv_s = [o["ai_npv"] for o in outs]
        for p in pr:
            rest = 1 - p
            w0 = scs[0].prob / (scs[0].prob + scs[1].prob) if scs[0].prob + scs[1].prob else 0.5
            probs = [rest * w0, rest * (1 - w0), p]
            o = option_value(probs, npv_s, [s.rate for s in scs], [v > 0 for v in npv_s])
            nows.append(o["now"] / 1e6); waits.append(o["wait"] / 1e6)
        f = fig(300, "Recession probability", "Expected NPV, CAD m")
        f.add_trace(go.Scatter(x=pr, y=nows, name="Invest now", line=dict(color=RED, width=3)))
        f.add_trace(go.Scatter(x=pr, y=waits, name="Wait, then decide", line=dict(color=BLUE, width=3)))
        f.add_vline(x=scs[2].prob, line_dash="dot", annotation_text="your table")
        show(f, "m4_ov_fig")

    # ------------------------------------------------------------------ trigger plan
    with tabs[7]:
        lede("Slide 22. A strong recommendation pairs an action with an indicator and a threshold. Every trigger below comes from the course numbers.")
        triggers = pd.DataFrame([
            ("Orders, housing starts", "Demand more than 12.5% below plan", "Capacity slack: price 950 → 900 (Module 1)"),
            ("Unit-cost index vs rivals", "Cost shock NovaHome does not face", "Absorb; do not raise alone"),
            ("Recession signals", "Recession probability falls", "Commit to AI; otherwise pilot"),
            ("Financing rate", "Above the AI break-even rate (≈14%)", "Shelve the AI project"),
            ("Tariff announcements", "≥ 8% on Asian boards", "Switch the board to Mexico (Module 3)"),
            ("Supplier disruption risk", "≥ 20%", "Move to 70/30 dual sourcing"),
            ("CAD per USD", "Beyond 1.62 / 1.78", "Revisit domestic sourcing"),
            ("Policy consultations", "Rebate or ceiling proposed", "Model incidence; engage with numbers"),
        ], columns=["Indicator", "Trigger", "Action"])
        st.dataframe(triggers, hide_index=True, width="stretch")
        st.subheader("Write your own")
        c1, c2, c3 = st.columns(3)
        ind = c1.text_input("Indicator", key="m4_p_ind", placeholder="e.g. housing starts")
        trig = c2.text_input("Trigger", key="m4_p_trig", placeholder="e.g. 3 months below plan by 15%")
        act = c3.text_input("Action", key="m4_p_act", placeholder="e.g. move the price to 900")
        if ind or trig or act:
            st.success(f"Monitor **{ind or '…'}**. If **{trig or '…'}**, then **{act or '…'}**.")
        note("Sources to monitor: Statistics Canada (CPI, GDP), Bank of Canada (policy rate, exchange rate), CMHC (housing starts).")
