import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from models import (CASE, price_game, repeated_threshold, delta_from, detection_lag_threshold, credibility,
                    first_mover, lemons, signalling, pilot_value, ai_screen, contract_design, homehub_bargain,
                    retail_contract_forms, monopoly_optimum)
from ui import (header, lede, answer, flip_ruler, cslider, predict, fig, show, note, step, m, cad,
                RED, BLUE, SLATE, BLUSH, INK, GREEN)


def _matrix_html(g):
    mtx = g["matrix"]
    def cell(r, c):
        rp, cp = mtx[(r, c)]
        rbest = (c == "Hold" and r == g["br_if_hold"]) or (c == "Cut" and r == g["br_if_cut"])
        cbest = (r == "Hold" and c == g["br_if_hold"]) or (r == "Cut" and c == g["br_if_cut"])
        a = f'<span class="br">{rp/1e6:.2f}</span>' if rbest else f"{rp/1e6:.2f}"
        b = f'<span class="br">{cp/1e6:.2f}</span>' if cbest else f"{cp/1e6:.2f}"
        cls = ' class="ne"' if (r, c) in g["nash"] else ""
        return f"<td{cls}>{a}, {b}</td>"
    return ('<table class="ns-matrix"><tr><th></th><th>NovaHome holds 900</th><th>NovaHome cuts to 850</th></tr>'
            f'<tr><th>NorthStar holds 900</th>{cell("Hold","Hold")}{cell("Hold","Cut")}</tr>'
            f'<tr><th>NorthStar cuts to 850</th>{cell("Cut","Hold")}{cell("Cut","Cut")}</tr></table>')


def render():
    header("Module 2 · Competition & information",
           "How should NorthStar act when others respond strategically, or know something it does not?")
    tabs = st.tabs(["Price game", "Repeated game", "Pricing algorithms", "Credible threats", "Early launch & networks",
                    "Hidden quality", "Contract design", "HomeHub bargaining"])

    # ------------------------------------------------------------------ price game
    with tabs[0]:
        lede("Slide 7. Year 2: NovaHome has entered. Payoffs are contribution in CAD millions, (NorthStar, NovaHome). "
             "Underlined: each firm's best response. Shaded: Nash equilibrium.")
        c1, c2 = st.columns([1, 1.4])
        with c1:
            hold = cslider("Units each, both hold 900", "m2_g_hh", 5000, 9000, CASE["q_both_hold"], 100)
            alone = cslider("Units for the firm that cuts alone", "m2_g_alone", 6000, 11000, CASE["q_cut_alone"], 100,
                            help="Try 8,000: does cutting stay dominant?")
            held = cslider("Units for the firm that holds while the other cuts", "m2_g_held", 3000, 8000, CASE["q_held_vs_cut"], 100)
            both = cslider("Units each, both cut to 850", "m2_g_cc", 5000, 9000, CASE["q_both_cut"], 50)
            mc = cslider("Unit cost (CAD)", "m2_g_mc", 300, 700, CASE["mc"], 10)
            g = price_game(hold, alone, held, both, mc=mc)
        with c2:
            st.markdown(_matrix_html(g), unsafe_allow_html=True)
            predict("m2_g_pred", "NorthStar's contribution in the Nash equilibrium (CAD)?",
                    g["matrix"][g["nash"][0]][0] if g["nash"] else 0, tol=0.01)
            e_alone = ((alone - hold) / ((alone + hold) / 2)) / (-50 / 875)
            e_match = ((both - hold) / ((both + hold) / 2)) / (-50 / 875)
            note(f"Elasticity NorthStar faces: cut alone {e_alone:.2f}; cut matched {e_match:.2f}. "
                 "The rival's response decides how elastic demand is.")
        ne = ", ".join(f"({r}, {c})" for r, c in g["nash"]) or "none in pure strategies"
        dom = g["dominant"] or "none"
        answer(f"Nash equilibrium: {ne}",
               f"Dominant strategy: {dom}. " + ("Both firms cut and each earns less than if both held: a prisoner's dilemma."
                                                 if g["dilemma"] else "No dilemma under these volumes."),
               "Do not judge a price cut alone: compare it with the response it triggers. Compete on service and versions instead.")
        flip_ruler("Gain from cutting alone (T − C)", (g["T"] - g["C"]) / 1e6, 0, -0.5, 0.5, fmt=lambda v: f"{v:+.2f}m",
                   left="Holding is a best response", right="Cutting tempts")

    # ------------------------------------------------------------------ repeated game
    with tabs[1]:
        lede("Slide 9. Rivals meet every year. Holding 900 beats a one-time cut when the weight on the future, δ, "
             "exceeds (T − C)/(T − P).")
        g = price_game()
        c1, c2 = st.columns([1, 1.5])
        with c1:
            cont = cslider("Chance the rivalry continues next year (%)", "m2_r_cont", 0, 100, 80, 5) / 100
            r = cslider("Discount rate (%)", "m2_r_rate", 0, 30, 10, 1) / 100
            lag = cslider("Years before a cut is detected", "m2_r_lag", 1, 5, 1, 1)
            d = delta_from(cont, r)
            thr = repeated_threshold(g["C"], g["T"], g["P"])
            thr_lag = detection_lag_threshold(g["C"], g["T"], g["P"], lag)
            st.latex(r"\delta \ge \frac{T-C}{T-P}=\frac{%.2f-%.2f}{%.2f-%.2f}=%.2f" % (g["T"]/1e6, g["C"]/1e6, g["T"]/1e6, g["P"]/1e6, thr))
            st.metric("Your δ", f"{d:.2f}")
            if lag > 1:
                st.metric(f"Threshold with a {lag}-year lag", f"{thr_lag:.2f}", help="Hold if δ^k ≥ (T − C)/(T − P)")
        with c2:
            dd = np.linspace(0, 1, 101)
            f = fig(360, "δ (weight on next year)", "Value per year, CAD m")
            f.add_trace(go.Scatter(x=dd, y=[g["C"] / 1e6] * len(dd), name="Hold 900", line=dict(color=BLUE, width=3)))
            f.add_trace(go.Scatter(x=dd, y=[(g["T"] - (g["T"] - g["P"]) * x) / 1e6 for x in dd], name="Cut once, then price war",
                                   line=dict(color=RED, width=3)))
            f.add_vline(x=thr, line_dash="dot", annotation_text=f"δ* = {thr:.2f}")
            f.add_vline(x=d, line_color=INK, annotation_text=f"your δ = {d:.2f}", annotation_position="bottom right")
            show(f, "m2_r_fig")
        need = thr_lag if lag > 1 else thr
        holds = d >= need
        answer(f"δ = {d:.2f} vs threshold {need:.2f}",
               "Cutting gains T − C once and loses C − P every year after; patience makes the loss count.",
               ("Holding 900 is rational without any agreement." if holds else "A one-time cut pays: expect price pressure.") +
               " Agreeing on prices with a rival is illegal (Competition Act s.45).")
        flip_ruler("Weight on the future", d, need, 0, 1, fmt=lambda v: f"{v:.2f}", left="Cut pays", right="Holding pays")

    # ------------------------------------------------------------------ algorithms
    with tabs[2]:
        lede("Slide 10. Fast matching removes the gain from undercutting; undercut rules create spirals. Neither is neutral.")
        c1, c2 = st.columns([1, 1.6])
        with c1:
            rule = st.radio("Both firms' pricing rule", ["Match the rival within hours", "Undercut the rival by a fixed amount"],
                            key="m2_a_rule")
            step_ = cslider("Undercut step (CAD)", "m2_a_step", 5, 50, 20, 5)
            floor = cslider("Programmed price floor (CAD)", "m2_a_floor", 500, 850, 600, 10)
            rounds = cslider("Rounds", "m2_a_rounds", 4, 30, 16, 1)
        nova, ns = [900.0], [900.0]
        for i in range(rounds):
            if rule.startswith("Match"):
                nova.append(nova[-1]); ns.append(ns[-1])
            else:
                if i % 2 == 0:
                    nova.append(max(floor, ns[-1] - step_)); ns.append(ns[-1])
                else:
                    ns.append(max(floor, nova[-1] - step_)); nova.append(nova[-1])
        with c2:
            f = fig(330, "Round", "Price, CAD")
            f.add_trace(go.Scatter(y=nova, name="NovaHome", line=dict(color=BLUE, width=2, shape="hv")))
            f.add_trace(go.Scatter(y=ns, name="NorthStar", line=dict(color=RED, width=3, shape="hv")))
            f.update_yaxes(range=[min(floor, 900) - 30, 930])
            show(f, "m2_a_fig")
        cm_end = ns[-1] - CASE["mc"]
        answer(f"NorthStar ends at {cad(ns[-1])} (CM {cad(cm_end)})",
               "Under matching, a cut wins almost nothing, so neither firm cuts." if rule.startswith("Match")
               else "Undercut rules ratchet prices down to the floor: faster, not wiser.",
               "No undercut rules without a floor; no tools that pool rivals' non-public data; legal review of any pricing vendor.")
        note("Canada's Competition Bureau published a discussion paper on algorithmic pricing (2025) and a What We Heard report "
             "(January 2026). Independent pricing is lawful; agreements on price are criminal under s.45.")

    # ------------------------------------------------------------------ credible threats
    with tabs[3]:
        lede("Slide 11. A threat changes a rival's behaviour only if carrying it out would be rational when the moment comes.")
        c1, c2 = st.columns([1, 1.4])
        with c1:
            built = st.toggle("Build year-2 capacity before NovaHome decides", value=False, key="m2_t_built")
            units = cslider("Buyers a price war can serve", f"m2_t_units_{int(built)}", 5000, 12000,
                            CASE["fight_units_spare"] if built else CASE["cap_y1"], 100)
            fp = cslider("Price-war price (CAD)", "m2_t_price", 650, 880, CASE["fight_price"], 10)
            cr = credibility(units, fp)
        with c2:
            f = fig(300, "", "NorthStar contribution if NovaHome enters, CAD m")
            f.add_bar(x=["Share the market at 900", f"Price war at {fp}"], y=[cr["accommodate"] / 1e6, cr["fight"] / 1e6],
                      marker_color=[BLUE, RED], text=[f"{cr['accommodate']/1e6:.2f}", f"{cr['fight']/1e6:.2f}"], textposition="outside")
            show(f, "m2_t_fig")
        answer("Credible threat" if cr["credible"] else "Empty threat",
               f"Price war earns {m(cr['fight'])} vs {m(cr['accommodate'])} sharing. "
               + ("NovaHome expects to lose money and stays out." if not cr["rival_enters"] else "NovaHome enters anyway."),
               f"NorthStar keeps {m(cr['northstar'])}. Commit first, with moves that are hard to reverse; announcing is not enough.")
        flip_ruler("Buyers the price war can serve", units, cr["units_needed"], 5000, 12000,
                   left="Threat is empty", right="Threat is credible")

    # ------------------------------------------------------------------ first mover + networks
    with tabs[4]:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Is launching early worth it?")
            lede("Slide 12. Count only incremental customers, then value the strategic benefits explicitly.")
            cost = cslider("Cost of launching three months early (CAD)", "m2_f_cost", 200_000, 1_500_000, 700_000, 50_000)
            ts = cslider("Share of early buyers who would have bought later anyway (%)", "m2_f_ts", 0, 60, 0, 5) / 100
            fm = first_mover(cost, 1_750, 450, ts)
            st.metric("Net value", cad(fm["net"]))
            flip_ruler("Time-shifted buyers", ts * 100, fm["max_time_shift"] * 100, 0, 60, fmt=lambda v: f"{v:.0f}%",
                       left="Early launch pays", right="Early launch loses money", good_side="left")
        with c2:
            st.subheader("Penetration pricing for network effects")
            lede("Slide 13. Pricing at 850 instead of 900 costs little near the optimum. It pays only if the network is NorthStar's own.")
            disc = cslider("Discount below 900 (CAD)", "m2_n_disc", 0, 150, 50, 10)
            wtp = cslider("Added WTP per 1,000 extra users (CAD)", "m2_n_wtp", 0.0, 5.0, 1.5, 0.1)
            proprietary = st.toggle("The network is NorthStar's own (not an open standard)", value=True, key="m2_n_prop")
            base = monopoly_optimum()
            p = 900 - disc
            q = max(0, CASE["a"] - CASE["b"] * p)
            cost_now = base["contribution"] - (p - CASE["mc"]) * q
            extra_users = q - base["q"]
            delta = wtp * extra_users / 1000 if proprietary else 0
            gain_yr = 5 * ((800 + delta) ** 2 - 800 ** 2)
            st.metric("Cost this year", cad(cost_now)); st.metric("Contribution gain each later year", cad(gain_yr))
            payback = cost_now / gain_yr if gain_yr > 0 else float("inf")
            answer(f"Payback {payback:.1f} years" if gain_yr > 0 else "Never pays back",
                   "Profit is flat near the optimum, so a modest discount is cheap; the benefit depends on who owns the network.",
                   "Use penetration pricing only for a proprietary network, and only if payback beats the product's life.")

    # ------------------------------------------------------------------ hidden quality
    with tabs[5]:
        lede("Slides 15–19. Before signing, the provider knows its type. Average pricing drives good providers out; "
             "signals and screens can bring them back.")
        t1, t2, t3, t4 = st.tabs(["Lemons", "Signalling", "Pilot screen", "AI score"])
        with t1:
            c1, c2 = st.columns([1, 1.4])
            with c1:
                ph = cslider("Share of high-quality providers (%)", "m2_l_ph", 0, 100, 50, 5) / 100
                inh = cslider("NorthStar's in-house cost per unit (CAD)", "m2_l_inh", 110, 200, CASE["inhouse_cost"], 5)
                lm = lemons(p_high=ph, inhouse=inh)
            with c2:
                f = fig(220, "Fee per unit, CAD", "")
                pts = [(60, "low min", SLATE), (lm["max_low"], "low max", SLATE), (lm["avg_offer"], "average offer", BLUE),
                       (110, "high min", RED), (lm["max_high"], "high max", RED)]
                f.add_trace(go.Scatter(x=[p[0] for p in pts], y=[0] * 5, mode="markers+text", text=[f"{p[1]}<br>{p[0]:.1f}" for p in pts],
                                       textposition=["bottom center", "top center", "bottom center", "top center", "bottom center"],
                                       marker=dict(size=14, color=[p[2] for p in pts]), showlegend=False))
                f.update_yaxes(visible=False, range=[-1, 1]); f.update_xaxes(range=[50, 150])
                show(f, "m2_l_fig")
            answer("High-quality providers exit" if lm["high_exits"] else "Both types trade",
                   f"NorthStar pays at most the average, {lm['avg_offer']:.1f}, against the high type's minimum 110.",
                   f"Signal or screen: the market loses {cad(lm['lost_trade'])} a year of trade with good providers otherwise.")
            flip_ruler("Average offer vs high type's minimum fee", lm["avg_offer"], 110, 60, 150, fmt=lambda v: f"{v:.1f}",
                       left="Good providers leave", right="Good providers stay")
        with t2:
            cov = cslider("Share of repeat repairs the guarantee covers (%)", "m2_s_cov", 10, 100, 100, 5) / 100
            sg = signalling(cov)
            f = fig(200, "CAD per unit", "")
            f.add_trace(go.Scatter(x=[sg["cost_h"], sg["reward"], sg["cost_l"]], y=[0, 0, 0], mode="markers+text",
                                   text=[f"cost, high<br>{sg['cost_h']:.1f}", f"reward<br>{sg['reward']:.0f}", f"cost, low<br>{sg['cost_l']:.1f}"],
                                   textposition=["bottom center", "top center", "bottom center"],
                                   marker=dict(size=16, color=[BLUE, INK, RED]), showlegend=False))
            f.update_yaxes(visible=False, range=[-1, 1]); f.update_xaxes(range=[0, 60])
            show(f, "m2_s_fig")
            answer("Separating" if sg["separating"] else "Pooling: the signal says nothing",
                   f"Separation needs cost_high < reward < cost_low: {sg['cost_h']:.1f} < {sg['reward']:.0f} < {sg['cost_l']:.1f}.",
                   f"Require a guarantee covering at least {sg['min_coverage']:.0%} of repeat repairs.")
            flip_ruler("Coverage", cov * 100, sg["min_coverage"] * 100, 0, 100, fmt=lambda v: f"{v:.0f}%",
                       left="Low types copy it", right="Credible signal")
        with t3:
            c1, c2 = st.columns(2)
            with c1:
                prior = cslider("Prior chance the provider is low quality (%)", "m2_p_prior", 0, 100, 50, 5) / 100
                det = cslider("Pilot detects a low type (%)", "m2_p_det", 0, 100, 70, 5) / 100
                loss = cslider("Loss avoided if detected (CAD)", "m2_p_loss", 50_000, 600_000, 300_000, 10_000)
                cost = cslider("Pilot cost (CAD)", "m2_p_cost", 0, 200_000, CASE["pilot_cost"], 5_000)
                pv = pilot_value(prior, det, loss, cost)
            with c2:
                st.metric("Expected benefit", cad(pv["benefit"])); st.metric("Net value", cad(pv["net"]))
                st.metric("Value of perfect information", cad(pv["perfect_info"]))
            answer(f"Net {cad(pv['net'])}", f"Prior × detection × loss avoided = {prior:.0%} × {det:.0%} × {cad(loss)}.",
                   "Run the pilot." if pv["net"] > 0 else "Skip the pilot; use cheaper screens.")
            flip_ruler("Detection rate", det * 100, pv["break_even_detect"] * 100, 0, 100, fmt=lambda v: f"{v:.0f}%",
                       left="Pilot loses money", right="Pilot pays")
        with t4:
            c1, c2 = st.columns(2)
            with c1:
                flagged = cslider("Providers the AI flags as high quality", "m2_ai_f", 5, 100, 30, 1)
                true_h = cslider("Of those, truly high quality", "m2_ai_t", 0, 100, 18, 1)
                base = cslider("Base rate of high quality (%)", "m2_ai_b", 10, 90, 50, 5) / 100
                ai = ai_screen(flagged, min(true_h, flagged), base)
            with c2:
                st.metric("Precision", f"{ai['precision']:.0%}"); st.metric("Lift over base rate", f"{ai['lift_pp']:+.0f} pp")
                st.metric("Value per hire", cad(ai["value_per_hire"]))
            answer(f"Precision {ai['precision']:.0%}", "An AI score is worth only its lift over the base rate.",
                   "Use it as a first filter, then pilot. Pilot alone leaves 95k of expected cost; combined, 86k.")

    # ------------------------------------------------------------------ contract design
    with tabs[6]:
        lede("Slides 21–24. After signing, effort is hidden. Size the bonus from the incentive constraint; the base buys participation.")
        c1, c2 = st.columns([1, 1.4])
        with c1:
            ph = cslider("Chance of hitting the target with high effort (%)", "m2_c_ph", 50, 100, 85, 1) / 100
            pl = cslider("…with low effort (%)", "m2_c_pl", 0, 80, 25, 1) / 100
            ec = cslider("Provider's cost of high effort (CAD)", "m2_c_ec", 20_000, 300_000, CASE["effort_cost"], 10_000)
            bonus = cslider("Bonus offered (CAD)", "m2_c_b", 0, 600_000, 200_000, 10_000)
            cd = contract_design(ph, pl, ec, bonus=bonus)
        with c2:
            bb = np.linspace(0, 600_000, 61)
            f = fig(330, "Bonus, CAD", "CAD")
            f.add_trace(go.Scatter(x=bb, y=(ph - pl) * bb, name="Provider's gain from effort", line=dict(color=BLUE, width=3)))
            f.add_trace(go.Scatter(x=bb, y=[ec] * len(bb), name="Effort cost", line=dict(color=RED, width=3)))
            f.add_trace(go.Scatter(x=[bonus], y=[(ph - pl) * bonus], mode="markers", marker=dict(size=13, color=INK), name="Your bonus"))
            show(f, "m2_c_fig")
        answer(f"Minimum bonus {cad(cd['bonus_min'])}" if np.isfinite(cd["bonus_min"]) else "No bonus works",
               f"Incentive: ({ph:.2f} − {pl:.2f}) × B ≥ {cad(ec)}. Participation then sets the base at {cad(cd['base'])}.",
               ("Your bonus induces effort. " if cd["induces_effort"] else "Your bonus is too small: the provider takes the base and shirks. ")
               + f"NorthStar saves {cad(cd['saving'])} a year vs a flat fee ({cad(cd['saving_after_monitoring'])} after monitoring).")
        flip_ruler("Bonus offered", bonus, cd["bonus_min"], 0, 600_000, fmt=cad, left="Shirking", right="High effort")
        with st.expander("The wrong metric can backfire (slide 22)"):
            step("A CAD 100,000 bonus for response time under 24 hours raises repeat repairs from 5% to 9%: "
                 "0.04 × 10,000 × 300 = 120,000 of extra repairs, so the bonus costs NorthStar 220,000. "
                 "People optimize what the contract measures.")

    # ------------------------------------------------------------------ HomeHub
    with tabs[7]:
        lede("Slides 25–26. Each side's outside option sets its floor; the deal splits the surplus above both floors.")
        c1, c2 = st.columns([1, 1.5])
        with c1:
            hh_out = cslider("HomeHub's outside option (CAD)", "m2_h_out", 0, 800_000, CASE["hh_outside_after"], 25_000,
                             help="0.25m before NovaHome entered; 0.45m after")
            cann = cslider("HomeHub buyers who would buy direct anyway (%)", "m2_h_cann", 0, 90, 40, 5) / 100
            share = cslider("NorthStar's share of the surplus (%)", "m2_h_share", 0, 100, 50, 5) / 100
            ask = cslider("HomeHub's demanded margin (%)", "m2_h_ask", 15, 40, 30, 1) / 100
            hb = homehub_bargain(hh_out, cann, share_ns=share, ask_margin=ask)
        with c2:
            f = fig(220, "CAD m", "")
            for lbl, val, col in [("NorthStar floor", hb["d_ns"], "#C9CDD4"), ("Surplus", max(hb["surplus"], 0), BLUSH),
                                  ("HomeHub floor", hb["d_hh"], "#E7B9C1")]:
                f.add_bar(y=["Joint value"], x=[val / 1e6], name=lbl, orientation="h", marker_color=col,
                          text=[f"{lbl} {val/1e6:.3f}"], textposition="inside")
            f.update_layout(barmode="stack", showlegend=False)
            show(f, "m2_h_fig")
        answer(f"Fair margin {hb['fair_margin']:.1%}; walk away above {hb['walkaway_margin']:.1%}",
               f"Joint value {m(hb['V'])}; surplus {m(hb['surplus'])}. At {ask:.0%}, NorthStar keeps {m(hb['ns_at_ask'])} vs its floor {m(hb['ns_floor'])}.",
               "Counter near the fair margin; improve the direct channel (raises NorthStar's floor) before the meeting.")
        flip_ruler("HomeHub's demanded margin", ask * 100, hb["walkaway_margin"] * 100, 15, 40, fmt=lambda v: f"{v:.1f}%",
                   left="Better than walking away", right="Walk away", good_side="left")
        st.subheader("Contract form matters")
        rows = retail_contract_forms()
        st.dataframe(pd.DataFrame(rows).style.format({"Shelf price": "CAD {:,.1f}", "Units": "{:,.0f}", "Joint margin": "CAD {:,.0f}",
                                                      "NorthStar": "CAD {:,.0f}"}, na_rep="–"), hide_index=True, width="stretch")
        note("Double marginalization: under a wholesale price HomeHub adds its own markup, the shelf price rises and NorthStar "
             "earns less than its 0.48m floor. A two-part tariff maximizes the joint margin; price parity avoids channel conflict.")
