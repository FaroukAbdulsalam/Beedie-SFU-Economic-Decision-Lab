import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from models import (CASE, value_per_case, threshold, aligned_penalty, default_margin, share_ci, diff_props, mde, did,
                    scale_decision, safety_stock_multiplier)
from ui import (header, lede, answer, flip_ruler, cslider, predict, fig, show, note, step, m, cad,
                RED, BLUE, SLATE, BLUSH, INK, GREEN)


def render():
    header("Module 5 · Behaviour, incentives & evidence",
           "How can managers use the levers they control to improve productivity and margins, and how do we know what worked?")
    st.page_link("pages/Module_5_Live_Experiments.py", label="Run the live experiments, then bring the class results here", icon="🧪")
    tabs = st.tabs(["Incentives", "Warranty default", "Colour", "Framing", "Counterfactuals", "Uncertainty & scaling"])

    # ------------------------------------------------------------------ incentives
    with tabs[0]:
        lede("Slides 8–9 and 12–13. Each service case is worth +10 if correct and −6 if wrong. An incentive is aligned when the "
             "agent's break-even accuracy equals the firm's.")
        c1, c2 = st.columns([1, 1.5])
        with c1:
            pr = cslider("Points per correct case", "m5_i_r", 0.0, 10.0, 2.0, 0.5)
            pl = cslider("Points lost per error", "m5_i_l", 0.0, 10.0, 2.0, 0.1)
            firm_t = threshold(CASE["v_correct"], CASE["v_incorrect"])
            agent_t = threshold(pr, pl) if pr + pl > 0 else 0.0
            st.metric("Firm's break-even accuracy", f"{firm_t:.1%}")
            st.metric("Agent's break-even accuracy", f"{agent_t:.1%}")
            st.metric("Aligned penalty for this reward", f"{aligned_penalty(pr):.2f} points")
        with c2:
            acc = np.linspace(0, 1, 101)
            f = fig(330, "Accuracy on a case", "Value of handling it")
            f.add_trace(go.Scatter(x=acc, y=[value_per_case(a) for a in acc], name="Firm (CAD-equivalent)", line=dict(color=RED, width=3)))
            f.add_trace(go.Scatter(x=acc, y=[pr * a - pl * (1 - a) for a in acc], name="Agent (points)", line=dict(color=BLUE, width=3)))
            f.add_hline(y=0, line_color=SLATE)
            f.add_vrect(x0=min(firm_t, agent_t), x1=max(firm_t, agent_t), fillcolor=BLUSH, opacity=0.6, line_width=0,
                        annotation_text="misaligned zone" if abs(firm_t - agent_t) > 0.005 else "", annotation_position="top left")
            show(f, "m5_i_fig")
        if abs(agent_t - firm_t) < 0.005:
            why = "The agent handles exactly the cases the firm wants handled."
        elif agent_t > firm_t:
            why = f"The agent avoids cases between {firm_t:.0%} and {agent_t:.0%} accuracy that the firm wants handled."
        else:
            why = f"The agent handles cases between {agent_t:.0%} and {firm_t:.0%} accuracy that lose the firm money."
        answer(f"Agent {agent_t:.0%} vs firm {firm_t:.0%}", why,
               "Align the ratio of penalty to reward with the firm's (6/10), and weight costly errors, like a missed safety escalation, more.")
        flip_ruler("Agent's break-even accuracy", agent_t * 100, firm_t * 100, 0, 100, fmt=lambda v: f"{v:.1f}%",
                   left="Handles money-losing cases", right="Avoids valuable cases")
        st.subheader("Enter the class results from Experiment 1")
        df = pd.DataFrame({"Arm": ["Control", "Quantity", "Balanced"], "Students": [10, 10, 10],
                           "Cases per person": [20.0, 30.0, 22.0], "Correct per person": [17.0, 21.0, 20.0]})
        ed = st.data_editor(df, key="m5_i_editor", hide_index=True, width="stretch", num_rows="fixed")
        ed = ed.copy()
        ed["Incorrect per person"] = ed["Cases per person"] - ed["Correct per person"]
        ed["Accuracy"] = ed["Correct per person"] / ed["Cases per person"].replace(0, np.nan)
        ed["Value per person"] = CASE["v_correct"] * ed["Correct per person"] - CASE["v_incorrect"] * ed["Incorrect per person"]
        ed["Effect vs control"] = ed["Value per person"] - float(ed.loc[0, "Value per person"])
        st.dataframe(ed.style.format({"Cases per person": "{:.1f}", "Correct per person": "{:.1f}", "Incorrect per person": "{:.1f}",
                                      "Accuracy": "{:.0%}", "Value per person": "{:.0f}", "Effect vs control": "{:+.0f}"}),
                     hide_index=True, width="stretch")
        top_cases = ed.loc[ed["Cases per person"].idxmax(), "Arm"]; top_value = ed.loc[ed["Value per person"].idxmax(), "Arm"]
        note(f"Most output: {top_cases}. Most value: {top_value}. Defaults shown are the illustrative slide numbers (152 / 156 / 188).")

    # ------------------------------------------------------------------ default
    with tabs[1]:
        lede("Slides 16–17 and 26. Turn the default effect into contribution, net of cancellations, and report the interval, not just the point.")
        c1, c2 = st.columns([1, 1.4])
        with c1:
            p_in = cslider("Opt-in adoption (%)", "m5_d_in", 0, 100, 30, 1) / 100
            p_out = cslider("Opt-out adoption (%)", "m5_d_out", 0, 100, 60, 1) / 100
            n = cslider("Students per arm", "m5_d_n", 5, 200, 30, 1)
            cancel = cslider("Default-induced buyers who cancel (%)", "m5_d_cancel", 0, 90, 30, 5) / 100
            handling = cslider("Cost to process a cancellation (CAD)", "m5_d_handle", 0, 50, 15, 1)
            impl = cslider("Cost to implement the default (CAD)", "m5_d_impl", 0, 100_000, 20_000, 5_000)
        dp = diff_props(p_out, n, p_in, n)
        lo, hi = max(dp["lo"], -1), min(dp["hi"], 1)
        mid = default_margin(dp["diff"], cancel_rate=cancel, handling=handling)
        low = default_margin(lo, cancel_rate=cancel, handling=handling)
        high = default_margin(hi, cancel_rate=cancel, handling=handling)
        with c2:
            f = fig(300, "", "CAD a year")
            f.add_trace(go.Bar(x=["Gross", "After cancellations"], y=[mid["gross"], mid["net"]], marker_color=["#C9CDD4", RED],
                               error_y=dict(type="data", symmetric=False, array=[high["gross"] - mid["gross"], high["net"] - mid["net"]],
                                            arrayminus=[mid["gross"] - low["gross"], mid["net"] - low["net"]], color=INK)))
            f.add_hline(y=impl, line_dash="dot", annotation_text="implementation cost")
            show(f, "m5_d_fig")
        dec = scale_decision(low["net"], high["net"], impl)
        answer(f"{dp['diff']*100:+.0f} pp, 95% CI {lo*100:+.0f} to {hi*100:+.0f} pp",
               f"Net contribution {cad(mid['net'])} (range {cad(low['net'])} to {cad(high['net'])}). "
               f"The default stops paying above {mid['breakeven_cancel']:.0%} cancellation.",
               f"{dec}. Check fairness ratings and legal review before any field rollout.")
        flip_ruler("Cancellation among default-induced buyers", cancel * 100, mid["breakeven_cancel"] * 100, 0, 100,
                   fmt=lambda v: f"{v:.0f}%", left="Default pays", right="Default loses money", good_side="left")
        note("The EU bans pre-ticked boxes for extra payments; Canada's Competition Act treats drip pricing as deceptive. "
             "A pre-checked paid plan is the kind of design these rules target.")

    # ------------------------------------------------------------------ colour
    with tabs[2]:
        lede("Slides 18–19. A preference test tells you what customers like, not what each option costs to offer.")
        c1, c2 = st.columns([1, 1.3])
        with c1:
            df = pd.DataFrame({"Colour": ["White", "Black", "Silver", "Navy Blue"], "Share (%)": [25.0, 40.0, 15.0, 20.0],
                               "Would pay CAD 50 more (%)": [10.0, 25.0, 10.0, 20.0]})
            ed = st.data_editor(df, key="m5_c_editor", hide_index=True, width="stretch", num_rows="fixed")
            n = cslider("Students", "m5_c_n", 10, 300, 60, 5)
        with c2:
            ed = ed.copy()
            ed["p"] = ed["Share (%)"] / 100
            ci = [share_ci(p, n) for p in ed["p"]]
            f = fig(300, "Share choosing", "")
            f.add_trace(go.Scatter(x=ed["p"] * 100, y=ed["Colour"], mode="markers", marker=dict(size=13, color=RED),
                                   error_x=dict(type="data", symmetric=False, array=[(h - p) * 100 for (l, h), p in zip(ci, ed["p"])],
                                                arrayminus=[(p - l) * 100 for (l, h), p in zip(ci, ed["p"])], color=INK), showlegend=False))
            f.update_xaxes(range=[0, 100], ticksuffix="%")
            show(f, "m5_c_fig")
        top = ed.loc[ed["p"].idxmax()]
        se = np.sqrt(top["p"] * (1 - top["p"]) / n) * 100
        st.subheader("What does variety cost?")
        c1, c2 = st.columns(2)
        with c1:
            skus = cslider("Colours offered", "m5_c_skus", 1, 6, 2, 1)
            ss1 = cslider("Safety stock with one colour (units)", "m5_c_ss", 50, 1000, 300, 25)
            cost1 = ss1 * CASE["mc"] * CASE["carry"]
            extra = cost1 * (safety_stock_multiplier(skus) - 1)
            st.metric("Extra carrying cost a year", cad(extra))
        with c2:
            prem_share = cslider("Buyers who pay CAD 50 more for a special finish (%)", "m5_c_prem", 0, 40, 10, 1) / 100
            prem = CASE["customers"] * prem_share * 50
            st.metric("Premium revenue a year", cad(prem))
        answer(f"{top['Colour']} leads at {top['p']:.0%} ± {1.96*se:.0f} pp",
               f"With {n} students, shares are only accurate to about ±{1.96*se:.0f} points; offering {skus} colours multiplies safety stock by {safety_stock_multiplier(skus):.2f}.",
               "Add a finish only if its premium beats its inventory cost, and discount stated willingness to pay before relying on it.")
        flip_ruler("Premium vs extra inventory cost", prem, extra, 0, max(prem, extra) * 2 + 1, fmt=cad,
                   left="Variety costs more than it earns", right="Variety pays")

    # ------------------------------------------------------------------ framing
    with tabs[3]:
        lede("Slides 20–21. Gain frame: 'Choose EcoSmart and save about CAD 180 a year.' Loss frame: 'Choose the standard model and you "
             "could lose about CAD 180 a year.' Same facts, different frame.")
        c1, c2 = st.columns([1, 1.3])
        with c1:
            g = cslider("EcoSmart share, gain frame (%)", "m5_f_g", 0, 100, 40, 1) / 100
            l = cslider("EcoSmart share, loss frame (%)", "m5_f_l", 0, 100, 50, 1) / 100
            n = cslider("Students per arm", "m5_f_n", 5, 200, 30, 1)
            dcm = cslider("Extra contribution per EcoSmart buyer (CAD)", "m5_f_dcm", 0, 120,
                          (CASE["eco_price"] - CASE["eco_unit_cost"]) - (CASE["std_price"] - CASE["mc"]), 1)
        dp = diff_props(l, n, g, n)
        val = dp["diff"] * CASE["customers"] * dcm
        with c2:
            f = fig(280, "Framing effect, pp", "")
            f.add_trace(go.Scatter(x=[dp["diff"] * 100], y=["Loss − gain"], mode="markers", marker=dict(size=14, color=RED),
                                   error_x=dict(type="data", symmetric=False, array=[(dp["hi"] - dp["diff"]) * 100],
                                                arrayminus=[(dp["diff"] - dp["lo"]) * 100], color=INK), showlegend=False))
            f.add_vline(x=0, line_color=SLATE)
            show(f, "m5_f_fig")
            st.metric("Value of the effect", cad(val) + " a year")
        payback = (CASE["eco_price"] - CASE["std_price"]) / CASE["eco_saving_per_year"]
        answer(f"{dp['diff']*100:+.0f} pp (95% CI {dp['lo']*100:+.0f} to {dp['hi']*100:+.0f})",
               f"Each switch to EcoSmart adds {cad(dcm)}; EcoSmart pays back its premium in {payback*12:.0f} months, so this nudge helps buyers too.",
               "Scale the message only if the CAD 180 saving is substantiated: environmental-benefit claims must be backed under the Competition Act.")

    # ------------------------------------------------------------------ counterfactuals
    with tabs[4]:
        lede("Slides 24–25. A causal effect compares what happened with what would have happened. When you cannot randomize, "
             "build the best comparison available.")
        c1, c2 = st.columns([1, 1.4])
        with c1:
            tb = cslider("BC sales before", "m5_dd_tb", 5000, 15000, 10000, 100)
            ta = cslider("BC sales after (new message)", "m5_dd_ta", 5000, 18000, 12000, 100)
            cb = cslider("Ontario sales before", "m5_dd_cb", 5000, 15000, 9000, 100)
            ca = cslider("Ontario sales after (old message)", "m5_dd_ca", 5000, 18000, 10350, 50)
            d = did(tb, ta, cb, ca)
        with c2:
            f = fig(320, "", "Units")
            f.add_trace(go.Scatter(x=["Before", "After"], y=[tb, ta], name="BC (treated)", line=dict(color=RED, width=3), mode="lines+markers"))
            f.add_trace(go.Scatter(x=["Before", "After"], y=[cb, ca], name="Ontario (comparison)", line=dict(color=BLUE, width=3), mode="lines+markers"))
            f.add_trace(go.Scatter(x=["Before", "After"], y=[tb, d["counterfactual"]], name="BC without the message",
                                   line=dict(color=RED, dash="dot"), mode="lines"))
            show(f, "m5_dd_fig")
        answer(f"Effect ≈ {d['effect']:,.0f} units, not {d['naive']:,.0f}",
               f"Ontario grew {d['comp_growth']:.1%}, so BC would have reached about {d['counterfactual']:,.0f} anyway (parallel trends).",
               f"Credit the message with {cad(d['effect'] * 400)} of contribution, not {cad(d['naive'] * 400)}. Check that the regions moved together beforehand.")

    # ------------------------------------------------------------------ uncertainty & scaling
    with tabs[5]:
        lede("Slides 26–28. A class-sized sample can only detect large effects. Report the interval in CAD, then decide.")
        c1, c2 = st.columns([1, 1.4])
        with c1:
            base = cslider("Baseline share (%)", "m5_u_base", 5, 95, 45, 1) / 100
            n = cslider("People per arm", "m5_u_n", 10, 2000, 30, 10)
            eff = cslider("Effect you hope to detect (pp)", "m5_u_eff", 1, 50, 10, 1)
            md = mde(base, n)
            st.metric("Smallest effect this sample can reliably detect", f"{md*100:.0f} pp")
        with c2:
            nn = np.unique(np.logspace(1, 3.5, 60).astype(int))
            f = fig(320, "People per arm", "Minimum detectable effect, pp")
            f.add_trace(go.Scatter(x=nn, y=[mde(base, int(x)) * 100 for x in nn], line=dict(color=RED, width=3), name="MDE"))
            f.add_hline(y=eff, line_dash="dot", annotation_text=f"target {eff} pp")
            f.update_xaxes(type="log")
            show(f, "m5_u_fig")
        n_needed = int(np.ceil(2 * base * (1 - base) * (2.8 / (eff / 100)) ** 2))
        answer(f"MDE {md*100:.0f} pp with {n} per arm",
               f"To detect {eff} pp reliably you need about {n_needed:,} per arm.",
               "Treat a classroom result as a reason to run a field test, not to scale. Keep a 5–10% holdout after scaling.")
        flip_ruler("People per arm", n, n_needed, 0, max(n_needed * 2, n * 1.2), fmt=lambda v: f"{v:,.0f}",
                   left="Underpowered", right="Can detect the target effect")
        st.subheader("Scale, revise, test, or stop")
        st.dataframe(pd.DataFrame([
            ("Lies entirely above the full cost", "Scale, keeping a holdout group"),
            ("Straddles the cost", "Test further: a larger or field pilot"),
            ("Positive, but trust or fairness ratings fall", "Revise the design"),
            ("Lies entirely below the cost", "Stop"),
        ], columns=["If the interval of net benefit…", "Then"]), hide_index=True, width="stretch")
        st.subheader("What a classroom experiment can and cannot tell us")
        c1, c2 = st.columns(2)
        with c1:
            step("<b>Does well:</b> a clean comparison within the class; shows that the mechanism exists; forces precise definitions.")
        with c2:
            step("<b>May not transfer:</b> students are not NorthStar's customers; choices are hypothetical; students may guess "
                 "the hypothesis; effects can fade at scale.")
