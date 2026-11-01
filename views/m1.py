import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from models import (CASE, demand_q, inverse_p, marginal_revenue, point_elasticity, arc_elasticity, mr_table,
                    monopoly_optimum, capacity_check, price_cut_test, channel_cm, break_even, ai_value,
                    markup_price, pass_through, scaled_demand_outcome)
from ui import (header, lede, answer, flip_ruler, cslider, predict, fig, show, note, step, m, cad,
                RED, BLUE, SLATE, BLUSH, INK)

A, B = CASE["a"], CASE["b"]


def _demand_fig(a, b, height=400):
    f = fig(height, "Quantity (units a year)", "CAD per unit")
    q = np.linspace(0, a, 200)
    f.add_trace(go.Scatter(x=q, y=(a - q) / b, name="Demand", line=dict(color=RED, width=3)))
    return f


def render():
    header("Module 1 · Customers, costs & pricing",
           "What should NorthStar produce, how much, and at what price?")
    tabs = st.tabs(["Demand & elasticity", "Profit-maximizing price", "Capacity", "Revenue vs profit",
                    "Costs & channels", "Segments & price path", "Who gains & stress test"])

    # ------------------------------------------------------------------ demand
    with tabs[0]:
        lede("Slides 6–8 and 18. Demand is NorthStar's own: 26,000 potential buyers a year with reservation prices "
             "spread evenly from 0 to 1,300. A straight line has one slope but many elasticities.")
        c1, c2 = st.columns([1, 1.6])
        with c1:
            p = cslider("Price (CAD)", "m1_d_price", 300, 1250, 900, 10)
            s = cslider("Demand shift (income, reviews, rebates…)", "m1_d_shift", 0.6, 1.4, 1.0, 0.05,
                        fmt="%.2fx", help="Scales the whole curve: 1.10 means 10% more buyers at every price")
            a, b = A * s, B * s
            q = demand_q(p, a, b)
            e = point_elasticity(p, a, b)
            st.metric("Units demanded", f"{q:,.0f}")
            st.metric("Point elasticity", f"{e:.2f}", help="ε = (ΔQ/ΔP)·(P/Q) = −20·P/Q on the case curve")
            st.metric("Revenue", m(p * q))
        with c2:
            f = _demand_fig(a, b)
            f.add_vrect(x0=0, x1=a / 2, fillcolor=BLUSH, opacity=0.5, line_width=0, layer="below",
                        annotation_text="elastic half", annotation_position="top left")
            f.add_trace(go.Scatter(x=[q], y=[p], mode="markers+text", text=[f"  ε = {e:.2f}"], textposition="middle right",
                                   marker=dict(size=12, color=INK), name="Your price"))
            f.add_hline(y=650 * 1.0, line_dash="dot", line_color=SLATE, annotation_text="unit elastic at 650",
                        annotation_position="bottom right")
            show(f, "m1_d_fig")
        rows = [{"Price": pp, "Quantity": demand_q(pp), "Elasticity": point_elasticity(pp), "Revenue": pp * demand_q(pp)}
                for pp in (950, 900, 800, 650, 600)]
        st.dataframe(pd.DataFrame(rows).style.format({"Price": "{:,.0f}", "Quantity": "{:,.0f}", "Elasticity": "{:.2f}",
                                                      "Revenue": "CAD {:,.0f}"}), hide_index=True, width="stretch")
        note(f"Midpoint (arc) elasticity from 800 to 600: {arc_elasticity(800, 600):.2f}. It averages an elastic "
             "region and an inelastic one, which is why the point measure is more useful for pricing.")
        side = "elastic" if abs(e) > 1 else ("unit elastic" if abs(abs(e) - 1) < 0.01 else "inelastic")
        answer(f"ε = {e:.2f} at CAD {p:,.0f}",
               f"Demand is {side} here. Elasticity belongs to a price point, not to the product.",
               "Price in the elastic half. Revenue peaks at 650, but profit peaks higher because every unit costs 500.")
        flip_ruler("Elastic or inelastic?", abs(e), 1.0, 0, 4, fmt=lambda v: f"|ε| = {v:.2f}",
                   left="Inelastic: raise price", right="Elastic: a price cut raises revenue")

    # ------------------------------------------------------------------ MR = MC
    with tabs[1]:
        lede("Slides 19–20. Profit is TR − FC − VC(Q). The first-order condition gives MR = MC: expand while the next "
             "unit adds more revenue than cost.")
        c1, c2 = st.columns([1, 1.6])
        with c1:
            mc = cslider("Unit cost, MC (CAD)", "m1_p_mc", 300, 800, CASE["mc"], 10)
            s = cslider("Demand shift", "m1_p_shift", 0.6, 1.4, 1.0, 0.05, fmt="%.2fx")
            a, b = A * s, B * s
            opt = monopoly_optimum(mc, a, b)
            predict("m1_p_pred", "what price maximizes contribution?", opt["p"], unit="", tol=0.01)
            st.metric("Profit-maximizing price", cad(opt["p"]))
            st.metric("Units", f"{opt['q']:,.0f}")
            st.metric("Contribution", m(opt["contribution"]),
                      help=f"Operating profit after the CAD 2.0m fixed cost: {m(opt['contribution'] - CASE['fixed'])}")
        with c2:
            f = _demand_fig(a, b, 430)
            qq = np.linspace(0, a / 2, 100)
            f.add_trace(go.Scatter(x=qq, y=[marginal_revenue(x, a, b) for x in qq], name="MR", line=dict(color=INK, width=2)))
            f.add_trace(go.Scatter(x=[0, a], y=[mc, mc], name="MC", line=dict(color=SLATE, width=2)))
            tbl = [r for r in mr_table(2000, 10000, a, b) if r["MR per unit"] is not None]
            f.add_trace(go.Scatter(x=[r["MR at midpoint Q"] for r in tbl], y=[r["MR per unit"] for r in tbl], mode="markers",
                                   marker=dict(symbol="square", size=9, color=INK), name="MR from the table"))
            f.add_shape(type="rect", x0=0, x1=opt["q"], y0=mc, y1=opt["p"], fillcolor=BLUSH, opacity=0.7, line_width=0, layer="below")
            f.add_trace(go.Scatter(x=[opt["q"], opt["q"]], y=[0, opt["p"]], mode="lines", line=dict(dash="dot", color=SLATE),
                                   showlegend=False))
            f.add_trace(go.Scatter(x=[opt["q"]], y=[opt["p"]], mode="markers+text", marker=dict(size=12, color=RED),
                                   text=[f"  P* = {opt['p']:,.0f}"], textposition="middle right", name="Optimum"))
            f.update_yaxes(range=[0, a / b * 1.05])
            show(f, "m1_p_fig")
            note("Shaded: contribution (P* − MC) × Q*. Squares: MR read off the 2,000-unit table, plotted at each interval's midpoint.")
        with st.expander("The whiteboard table: building MR from revenue"):
            df = pd.DataFrame(mr_table(2000, 10000, a, b))
            st.dataframe(df.style.format({"Q": "{:,.0f}", "P": "{:,.0f}", "TR": "CAD {:,.0f}", "dTR": "CAD {:,.0f}",
                                          "MR per unit": "{:,.0f}", "MR at midpoint Q": "{:,.0f}"}, na_rep=""),
                         hide_index=True, width="stretch")
            q8 = opt["q"]
            step(f"One more unit at Q = {q8:,.0f}: gain the new unit's price ≈ {inverse_p(q8 + 1, a, b):,.2f}, "
                 f"lose {1/b:.2f} × {q8:,.0f} = {q8/b:,.0f} on earlier units, so MR ≈ {inverse_p(q8 + 1, a, b) - q8/b:,.0f}.")
        answer(f"CAD {opt['p']:,.0f} for {opt['q']:,.0f} units",
               f"MR = {a/b:,.0f} − {2/b:.2f}Q meets MC = {mc:,.0f} at Q = {opt['q']:,.0f}. Read the price off demand, not MR. "
               f"Markup check: (P − MC)/P = {opt['lerner']:.3f} = 1/|ε| with ε = {opt['elasticity']:.2f}.",
               "Fixed costs decide whether to launch, not what to charge. The price is set at the margin.")
        flip_ruler("Does the launch cover fixed cost?", opt["contribution"], CASE["fixed"], 0, 6e6, fmt=m,
                   left="Contribution below fixed cost: do not launch", right="Launch")

    # ------------------------------------------------------------------ capacity
    with tabs[2]:
        lede("Slide 21. If buyers want more than the factory can make, price to clear capacity rather than ration. "
             "MR at capacity minus MC is what one more unit of capacity is worth.")
        c1, c2 = st.columns([1, 1.6])
        with c1:
            capq = cslider("Capacity (units a year)", "m1_c_cap", 3000, 15000, CASE["cap_y1"], 500)
            mc = cslider("Unit cost (CAD)", "m1_c_mc", 300, 800, CASE["mc"], 10)
            s = cslider("Demand shift", "m1_c_shift", 0.6, 1.4, 1.0, 0.05, fmt="%.2fx")
            r = capacity_check(capq, mc, A * s, B * s)
            st.metric("Price", cad(r["p"]))
            st.metric("Shadow value of capacity", cad(r["shadow"]) + " a unit")
            st.metric("Contribution", m(r["contribution"]))
        with c2:
            a, b = A * s, B * s
            f = _demand_fig(a, b, 430)
            qq = np.linspace(0, a / 2, 100)
            f.add_trace(go.Scatter(x=qq, y=[marginal_revenue(x, a, b) for x in qq], name="MR", line=dict(color=INK, width=2)))
            f.add_trace(go.Scatter(x=[0, a], y=[mc, mc], name="MC", line=dict(color=SLATE)))
            f.add_vline(x=capq, line=dict(color=BLUE, width=3), annotation_text="capacity", annotation_position="top right")
            if r["binding"]:
                f.add_trace(go.Scatter(x=[capq, capq], y=[mc, marginal_revenue(capq, a, b)], mode="lines",
                                       line=dict(color=RED, width=6), name=f"Shadow value {r['shadow']:,.0f}"))
            f.add_trace(go.Scatter(x=[r["q"]], y=[r["p"]], mode="markers+text", marker=dict(size=12, color=RED),
                                   text=[f"  {r['p']:,.0f}"], textposition="middle right", name="Price"))
            f.update_yaxes(range=[0, a / b * 1.05])
            show(f, "m1_c_fig")
        if r["binding"]:
            answer(f"CAD {r['p']:,.0f}, sell {r['q']:,.0f}",
                   f"At the unconstrained price {r['unconstrained_p']:,.0f}, {r['unconstrained_q']:,.0f} want the product. "
                   f"Pricing there would turn away {r['rationed']:,.0f} buyers and leave {cad(r['left_on_table'])} on the table.",
                   f"Price to clear capacity. Expanding capacity is worth up to {cad(r['shadow'])} a unit a year.")
        else:
            answer(f"CAD {r['p']:,.0f}, sell {r['q']:,.0f}", "Capacity is not binding, so MR = MC sets the price.",
                   "Ignore capacity for pricing; its shadow value is zero.")
        flip_ruler("Does capacity bind?", r.get("unconstrained_q", r["q"]), capq, 0, 16000,
                   left="Unconstrained demand below capacity", right="Capacity binds: price to clear it")

    # ------------------------------------------------------------------ revenue vs profit
    with tabs[3]:
        lede("Slide 22. A price cut raises revenue when demand is elastic. The test is contribution: does the extra "
             "volume cover the margin given up on every unit?")
        c1, c2 = st.columns([1, 1.5])
        with c1:
            p0 = cslider("Current price (CAD)", "m1_r_p", 600, 1200, 900, 10)
            cut = cslider("Price cut (%)", "m1_r_cut", 1, 25, 10, 1)
            mc = cslider("Unit cost (CAD)", "m1_r_mc", 300, 800, CASE["mc"], 10)
            pc = price_cut_test(p0, cut, mc)
        with c2:
            f = fig(330, "", "CAD")
            f.add_bar(x=["Revenue", "Contribution"], y=[pc["tr0"], pc["contrib0"]], name=f"At {p0:,.0f}", marker_color="#C9CDD4")
            f.add_bar(x=["Revenue", "Contribution"], y=[pc["tr1"], pc["contrib1"]], name=f"At {pc['p1']:,.0f}", marker_color=RED)
            f.update_layout(barmode="group")
            show(f, "m1_r_fig")
        st.latex(r"\%\Delta Q_{\text{needed}}=\frac{|\Delta P|}{CM-|\Delta P|}"
                 f"=\\frac{{{p0-pc['p1']:,.0f}}}{{{p0-mc:,.0f}-{p0-pc['p1']:,.0f}}}={pc['rule_pct']:.1f}\\%")
        ok = pc["got_pct"] >= pc["req_pct"]
        answer(f"Need +{pc['req_pct']:.1f}%, demand gives +{pc['got_pct']:.1f}%",
               f"Revenue goes {m(pc['tr0'])} → {m(pc['tr1'])}; contribution goes {m(pc['contrib0'])} → {m(pc['contrib1'])}.",
               "Cut." if ok else "Do not cut: the cut raises revenue but lowers contribution.")
        flip_ruler("Volume the cut delivers vs volume it needs", pc["got_pct"], pc["req_pct"], 0, max(60, pc["req_pct"] * 1.5),
                   fmt=lambda v: f"+{v:.1f}%", left="Short: contribution falls", right="Enough: contribution rises")

    # ------------------------------------------------------------------ costs & channels
    with tabs[4]:
        lede("Slides 11–16. Relevant costs change with the decision; break-even is an incremental test.")
        t1, t2, t3 = st.tabs(["Direct vs retail", "Break-even", "AI investment"])
        with t1:
            c1, c2 = st.columns([1, 1.4])
            with c1:
                price = cslider("Price (CAD)", "m1_ch_p", 700, 1100, 900, 10)
                share = cslider("Retailer's share of price (%)", "m1_ch_share", 0, 40, 25, 1) / 100
                rcost = cslider("Retail unit cost (CAD)", "m1_ch_rc", 380, 520, CASE["retail_unit_cost"], 5)
                cann = cslider("Share of retail buyers who would buy direct anyway (%)", "m1_ch_cann", 0, 100, 40, 5) / 100
                ch = channel_cm(price, CASE["mc"], share, rcost)
            with c2:
                inc = ch["retail"] - cann * ch["direct"]
                f = fig(300, "", "CAD per retail unit")
                f.add_bar(x=["Direct CM", "Retail CM", "Lost direct CM", "Incremental retail CM"],
                          y=[ch["direct"], ch["retail"], -cann * ch["direct"], inc],
                          marker_color=[SLATE, BLUE, "#C9CDD4", RED if inc < 0 else "#2E7D4F"])
                show(f, "m1_ch_fig")
            answer(f"Retail adds {cad(inc)} a unit",
                   f"Retail CM {cad(ch['retail'])} minus {cann:.0%} × direct CM {cad(ch['direct'])}.",
                   "Keep retail only for buyers direct cannot reach. When capacity binds, every retail unit displaces a direct one.")
            flip_ruler("Cannibalization rate", cann * 100, ch["cannibal_threshold"] * 100, 0, 100,
                       fmt=lambda v: f"{v:.0f}%", left="Retail adds value", right="Retail destroys value", good_side="left")
        with t2:
            c1, c2 = st.columns(2)
            with c1:
                F = cslider("Campaign cost (CAD)", "m1_be_F", 200_000, 3_000_000, CASE["campaign"], 50_000)
                cm = cslider("Contribution per added sale (CAD)", "m1_be_cm", 100, 600, 400, 10)
                exp = cslider("Expected incremental units", "m1_be_q", 0, 10_000, 3_000, 250)
                be = break_even(F, cm)
            with c2:
                st.metric("Break-even incremental units", f"{be:,.0f}")
                st.metric("Net incremental benefit", cad(exp * cm - F))
                st.metric("Year 1 (capacity binds): price lift needed", cad(F / CASE["cap_y1"]),
                          help="With capacity full, a campaign cannot add units; it pays only by raising the clearing price")
            answer(f"{be:,.0f} incremental units", "Break-even gives the threshold, not the probability of reaching it.",
                   "Ask how credible the incremental volume is, and whether capacity lets it happen.")
            flip_ruler("Expected vs break-even volume", exp, be, 0, max(be * 2, 1), left="Below: loses money", right="Above: pays")
        with t3:
            c1, c2 = st.columns(2)
            with c1:
                fixed = cslider("AI annual cost (CAD)", "m1_ai_F", 100_000, 1_500_000, CASE["ai_annual"], 50_000)
                save = cslider("Saving per unit (CAD)", "m1_ai_s", 20, 200, CASE["ai_saving"], 5)
                units = cslider("Units a year", "m1_ai_q", 2000, 15000, CASE["cap_y1"], 500)
                v = ai_value(units, save, fixed)
            with c2:
                rows = []
                y1 = capacity_check(CASE["cap_y1"], CASE["mc"] - save)["contribution"] - capacity_check(CASE["cap_y1"])["contribution"]
                y2s = save * monopoly_optimum()["q"]
                y2r = monopoly_optimum(CASE["mc"] - save)["contribution"] - monopoly_optimum()["contribution"]
                for lbl, g in [("Year 1, capacity binds", y1), ("Year 2, price held at 900", y2s), ("Year 2, price re-optimized", y2r)]:
                    rows.append({"Scenario": lbl, "Gross gain": g, "Net of AI cost": g - fixed})
                st.dataframe(pd.DataFrame(rows).style.format({"Gross gain": "CAD {:,.0f}", "Net of AI cost": "CAD {:,.0f}"}),
                             hide_index=True, width="stretch")
            answer(f"Break-even {v['break_even']:,.0f} units", f"At {units:,.0f} units the net benefit is {cad(v['net'])}.",
                   "AI raises fixed cost and lowers marginal cost: its value grows with scale and with freedom to reprice.")
            flip_ruler("Units vs AI break-even", units, v["break_even"], 0, 16000, left="Below: AI loses money", right="Above: AI pays")

    # ------------------------------------------------------------------ segments & price path
    with tabs[5]:
        lede("Slides 23–24. The markup rule P = MC·|ε|/(|ε| − 1) gives a price for each segment. "
             "Capacity adds its shadow cost to MC.")
        seg = pd.DataFrame({"Segment": ["Emergency replacement (bundle)", "Eco-conscious homeowners", "Property managers"],
                            "Elasticity |ε|": [2.0, 2.25, 4.0], "Unit cost": [650.0, 500.0, 500.0]})
        ed = st.data_editor(seg, key="m1_seg_editor", hide_index=True, width="stretch", num_rows="fixed",
                            column_config={"Elasticity |ε|": st.column_config.NumberColumn(min_value=1.05, max_value=10, step=0.05)})
        shadow = cslider("Shadow cost of capacity added to MC (year 1)", "m1_seg_shadow", 0, 300, 100, 10)
        ed = ed.copy()
        ed["Price (capacity slack)"] = [markup_price(c, e) for c, e in zip(ed["Unit cost"], ed["Elasticity |ε|"])]
        ed["Price (capacity binds)"] = [markup_price(c + shadow, e) for c, e in zip(ed["Unit cost"], ed["Elasticity |ε|"])]
        st.dataframe(ed.style.format({"Elasticity |ε|": "{:.2f}", "Unit cost": "{:,.0f}", "Price (capacity slack)": "CAD {:,.0f}",
                                      "Price (capacity binds)": "CAD {:,.0f}"}), hide_index=True, width="stretch")
        answer("A price for each segment", "More price-sensitive segments get lower markups; binding capacity raises every price.",
               "Version the product and fence segments (proof of failure, business registration) so offers do not leak.")
        st.subheader("The price path")
        path = [("Year 1", capacity_check(CASE["cap_y1"])["p"]), ("Year 2", monopoly_optimum()["p"]),
                ("Year 2 with AI", monopoly_optimum(CASE["mc"] - CASE["ai_saving"])["p"])]
        f = fig(260, "", "CAD")
        f.add_trace(go.Scatter(x=[p[0] for p in path], y=[p[1] for p in path], mode="lines+markers+text",
                               text=[f"{p[1]:,.0f}" for p in path], textposition="top center", line=dict(color=RED, width=3)))
        f.update_yaxes(range=[800, 1000])
        show(f, "m1_path_fig")
        note("The decline comes from capacity and cost, not from using up high-value buyers: a fresh group arrives each year.")

    # ------------------------------------------------------------------ who gains + stress test
    with tabs[6]:
        lede("Slides 26–27. Who captures a cost cut depends on capacity and competition. The stress test asks how wrong "
             "the demand forecast can be before the plan changes.")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Who captures a cost cut?")
            cutv = cslider("Unit-cost cut (CAD)", "m1_g_cut", 0, 200, 100, 10)
            binding = st.toggle("Capacity binds (year 1)", key="m1_g_bind", value=False)
            ptr = pass_through(CASE["mc"], CASE["mc"] - cutv, cap=CASE["cap_y1"] if binding else None)
            f = fig(300, "", "Gain, CAD")
            f.add_bar(x=["NorthStar contribution", "Customer surplus"], y=[ptr["firm1"] - ptr["firm0"], ptr["cs1"] - ptr["cs0"]],
                      marker_color=[RED, BLUE])
            show(f, "m1_g_fig")
            pt = ptr["pass_through"] if cutv else 0
            answer(f"Price {ptr['p0']:,.0f} → {ptr['p1']:,.0f}",
                   f"Pass-through {pt:.0%}: " + ("capacity binds, so the price cannot fall." if binding else
                                                 "with linear demand a price-setter passes half of a cost change to price."),
                   "Under competition pass-through approaches 100%; with binding capacity it is zero.")
        with c2:
            st.subheader("Stress test: what if demand is different?")
            s = cslider("Demand as a share of forecast", "m1_s_s", 0.5, 1.4, 1.0, 0.05, fmt="%.2f")
            r = scaled_demand_outcome(s)
            st.metric("Price", cad(r["p"])); st.metric("Units", f"{r['q']:,.0f}")
            st.metric("Operating profit", m(r["operating_profit"]))
            flip_ruler("Does capacity still bind?", s, 0.875, 0.5, 1.4, fmt=lambda v: f"{v:.2f}×",
                       left="Slack: price falls to 900", right="Binds: price ≥ 950")
            flip_ruler("Does the launch cover fixed cost?", s, 0.625, 0.5, 1.4, fmt=lambda v: f"{v:.2f}×",
                       left="Loses money", right="Covers fixed cost")
