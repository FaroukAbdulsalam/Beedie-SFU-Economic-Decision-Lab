import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from models import (CASE, comparative_advantage, specialization_gain, wage_band, unit_labour_costs,
                    inventory_cost_per_unit, supplier_costs, dual_sourcing, tariff_threshold, fx_breakeven, automation_cost)
from ui import (header, lede, answer, flip_ruler, cslider, predict, fig, show, note, step, m, cad,
                RED, BLUE, SLATE, BLUSH, INK, GREEN)

NAMES = ["Canada", "Mexico", "Asia"]
COLORS = {"Canada": SLATE, "Mexico": BLUE, "Asia": RED}


def _inputs():
    """Shared sourcing assumptions, kept in the sidebar-free 'Assumptions' expander of the delivered-cost tab."""
    ss = st.session_state
    return dict(fx=ss.get("m3_fx", CASE["fx"]), tariff=ss.get("m3_tariff", 0) / 100,
                p_asia=ss.get("m3_p_asia", 15) / 100, p_mex=ss.get("m3_p_mex", 5) / 100, p_can=ss.get("m3_p_can", 2.5) / 100,
                carry=ss.get("m3_carry", 25) / 100, lead_asia=ss.get("m3_lead_asia", 10), rework_asia=ss.get("m3_rework_asia", 5))


def _costs(inp):
    out = {}
    for n in NAMES:
        kw = dict(fx=inp["fx"], carry=inp["carry"])
        if n == "Asia":
            kw.update(tariff=inp["tariff"], p_disrupt=inp["p_asia"], lead=inp["lead_asia"], quality=inp["rework_asia"])
        elif n == "Mexico":
            kw.update(p_disrupt=inp["p_mex"])
        else:
            kw.update(p_disrupt=inp["p_can"])
        out[n] = supplier_costs(n, **kw)
    return out


def render():
    header("Module 3 · Trade & sourcing",
           "Where should NorthStar source its control board when locations differ in cost, distance, currency, policy and technology?")
    tabs = st.tabs(["Comparative advantage", "Delivered cost", "Tariffs & currency", "Supplier risk & automation", "Decision & flip points"])

    # ------------------------------------------------------------------ comparative advantage
    with tabs[0]:
        lede("Slides 6–9. Specialize where your opportunity cost is lowest. Comparative advantage reaches a supplier's quote through wages.")
        c1, c2 = st.columns([1, 1.4])
        with c1:
            cb = cslider("Canada: boards per worker-day", "m3_ca_cb", 1, 30, 12, 1)
            cs = cslider("Canada: sensors per worker-day", "m3_ca_cs", 1, 40, 24, 1)
            mb = cslider("Mexico: boards per worker-day", "m3_ca_mb", 1, 30, 8, 1)
            ms = cslider("Mexico: sensors per worker-day", "m3_ca_ms", 1, 40, 10, 1)
            ca = comparative_advantage(cb, cs, mb, ms)
            sp = specialization_gain((cb, cs), (mb, ms))
        with c2:
            st.dataframe(pd.DataFrame([
                {"Location": "Canada", "Boards": cb, "Sensors": cs, "Opportunity cost of a board (sensors)": ca["oc_board_a"]},
                {"Location": "Mexico", "Boards": mb, "Sensors": ms, "Opportunity cost of a board (sensors)": ca["oc_board_b"]},
            ]).style.format({"Opportunity cost of a board (sensors)": "{:.2f}"}), hide_index=True, width="stretch")
            f = fig(260, "", "Units from 20 worker-days")
            f.add_bar(x=["Boards", "Sensors"], y=[sp["split"]["boards"], sp["split"]["sensors"]], name="Each splits 50/50", marker_color="#C9CDD4")
            f.add_bar(x=["Boards", "Sensors"], y=[sp["spec"]["boards"], sp["spec"]["sensors"]], name="Specialize", marker_color=RED)
            f.update_layout(barmode="group")
            show(f, "m3_ca_fig")
        answer(f"{ca['comp_board']} makes boards; {ca['comp_sensor']} makes sensors",
               f"Absolute advantage in boards: {ca['abs_board']}. Opportunity cost decides: {ca['oc_board_a']:.2f} vs {ca['oc_board_b']:.2f} sensors per board.",
               f"Specializing adds {sp['extra_sensors']:,.0f} sensors from the same workers; terms of trade between "
               f"{ca['tot_low']:.2f} and {ca['tot_high']:.2f} sensors per board let both gain.")
        st.subheader("From productivity to prices: the wage band")
        c1, c2 = st.columns([1, 1.4])
        lo, hi = wage_band((cb, cs), (mb, ms)) if mb and ms else (0, 0)
        with c1:
            wc = cslider("Canada daily wage (CAD)", "m3_w_c", 100, 600, 360, 10)
            wm = cslider("Mexico daily wage (CAD)", "m3_w_m", 50, 400, 180, 10)
            ulc = unit_labour_costs(wc, wm, (cb, cs), (mb, ms))
        with c2:
            st.dataframe(pd.DataFrame([
                {"Unit labour cost": "Board", "Canada": ulc["board_a"], "Mexico": ulc["board_b"]},
                {"Unit labour cost": "Sensor", "Canada": ulc["sensor_a"], "Mexico": ulc["sensor_b"]},
            ]).style.format({"Canada": "{:.2f}", "Mexico": "{:.2f}"}), hide_index=True, width="stretch")
        ratio = wc / wm
        cheaper_board = "Mexico" if ulc["board_b"] < ulc["board_a"] else "Canada"
        answer(f"Wage ratio {ratio:.2f}: {cheaper_board} quotes the cheaper board",
               f"Mexico is cheaper in boards when the ratio exceeds {lo:.2f}; Canada stays cheaper in sensors below {hi:.2f}.",
               "A low wage is a low cost only when it outweighs the productivity gap.")
        flip_ruler("Canada/Mexico wage ratio", ratio, lo, 0.5, 4, fmt=lambda v: f"{v:.2f}",
                   left="Canada cheaper even in boards", right="Mexico cheaper in boards")
        with st.expander("Pause and apply: engineers' time (slide 9)"):
            hrs = cslider("Engineer-hours a year to make the board in-house", "m3_e_hrs", 0, 5000, 2000, 100)
            val = cslider("Contribution per engineer-hour on the AI platform (CAD)", "m3_e_val", 0, 300, 150, 10)
            oc = hrs * val / CASE["boards"]
            st.metric("Opportunity cost per board", cad(oc, 1)); st.metric("True in-house cost", cad(185 + oc, 1))
            note("Scarce talent has an opportunity cost even when no invoice shows it.")

    # ------------------------------------------------------------------ delivered cost
    with tabs[1]:
        lede("Slides 12–14. A quote covers the board at the supplier's door. Add logistics, inventory for the lead time, "
             "quality, and expected disruption.")
        with st.expander("Assumptions (shared by every Module 3 tab)", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                cslider("CAD per USD", "m3_fx", 1.20, 1.90, CASE["fx"], 0.01)
                cslider("Tariff on Asian boards (%)", "m3_tariff", 0, 25, 0, 1)
            with c2:
                cslider("Asia disruption risk (%)", "m3_p_asia", 0, 60, 15, 1)
                cslider("Mexico disruption risk (%)", "m3_p_mex", 0, 30, 5, 1)
            with c3:
                cslider("Canada disruption risk (%)", "m3_p_can", 0.0, 20.0, 2.5, 0.5)
                cslider("Inventory carrying cost (% a year)", "m3_carry", 10, 40, 25, 1)
            with c4:
                cslider("Asia lead time (weeks)", "m3_lead_asia", 2, 16, 10, 1)
                cslider("Asia rework cost per board (CAD)", "m3_rework_asia", 0, 15, 5, 1)
        inp = _inputs()
        costs = _costs(inp)
        f = fig(360, "", "CAD per board")
        parts = [("quote", "Quote", "#8C93A0"), ("logistics", "Freight, insurance, compliance", "#B7BCC6"),
                 ("tariff", "Tariff", "#6B4E9B"), ("inventory", "Inventory", BLUE), ("quality", "Quality / rework", "#D6A2AC"),
                 ("disruption", "Expected disruption", RED)]
        for k, lbl, col in parts:
            f.add_bar(x=NAMES, y=[costs[n][k] for n in NAMES], name=lbl, marker_color=col)
        f.update_layout(barmode="stack")
        for n in NAMES:
            f.add_annotation(x=n, y=costs[n]["risk_adjusted"], text=f"<b>{costs[n]['risk_adjusted']:.1f}</b>", showarrow=False, yshift=12)
        show(f, "m3_dc_fig")
        best = min(NAMES, key=lambda n: costs[n]["risk_adjusted"])
        second = sorted(NAMES, key=lambda n: costs[n]["risk_adjusted"])[1]
        lead = costs[second]["risk_adjusted"] - costs[best]["risk_adjusted"]
        predict("m3_dc_pred", "Asia's risk-adjusted cost per board at the case values?", 157, tol=0.02)
        answer(f"{best} at {costs[best]['risk_adjusted']:.1f} a board",
               f"{lead:.1f} below {second}: {cad(lead * CASE['boards'])} a year on 10,000 boards.",
               "Compare delivered, risk-adjusted cost, never invoice prices. A thin lead means the flip points matter.")
        st.caption("Inventory is computed from the lead time (slide 13), so the table shows 1.3 / 2.8 / 7.0 where the slide rounds to 1 / 3 / 7.")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Time is money: inventory from lead time")
            L = np.arange(1, 17)
            f2 = fig(280, "Lead time (weeks)", "Inventory cost per board, CAD")
            f2.add_trace(go.Scatter(x=L, y=[inventory_cost_per_unit(l, 125, carry=inp["carry"])["per_unit"] for l in L],
                                    line=dict(color=RED, width=3), name="Asia (board worth 125)"))
            show(f2, "m3_inv_fig")
            note("Pipeline stock grows with the lead time; safety stock grows with its square root.")
        with c2:
            st.subheader("Is a second source worth it?")
            share = cslider("Volume kept in Asia (%)", "m3_ds_share", 50, 95, 70, 5) / 100
            ds = dual_sourcing(inp["p_asia"], inp["p_mex"], share, cost_asia=costs["Asia"]["delivered"], cost_mex=costs["Mexico"]["delivered"])
            st.metric("Asia only (CAD a year)", m(ds["single"])); st.metric(f"{share:.0%} Asia / {1-share:.0%} Mexico", m(ds["dual"]))
            flip_ruler("Asia disruption risk", inp["p_asia"] * 100, ds["p_star"] * 100, 0, 60, fmt=lambda v: f"{v:.0f}%",
                       left="Single source", right="Dual source pays")

    # ------------------------------------------------------------------ tariffs & currency
    with tabs[2]:
        inp = _inputs()
        costs = _costs({**inp, "tariff": 0})
        lead_vs_mex = costs["Mexico"]["risk_adjusted"] - costs["Asia"]["risk_adjusted"]
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Tariffs (slides 15–16)")
            thr = tariff_threshold(lead_vs_mex, costs["Asia"]["quote"])
            flip_ruler("Tariff on Asian boards", inp["tariff"] * 100, thr * 100, 0, 25, fmt=lambda v: f"{v:.1f}%",
                       left="Asia stays cheapest", right="Mexico cheaper")
            lede("Who bears a tariff: with spare capacity and linear demand, half passes to customers. "
                 "Switching caps the damage at Asia's lead over Mexico.")
            note("As of October 2026, CUSMA remains in force: the US declined to renew it at the July 1, 2026 review, "
                 "triggering annual reviews. Qualifying goods keep preferential treatment; US Section 232 tariffs apply regardless.")
        with c2:
            st.subheader("Exchange rates (slide 17)")
            e = np.linspace(1.2, 1.95, 76)
            f = fig(320, "CAD per USD", "Risk-adjusted CAD per board")
            other = {n: costs[n]["risk_adjusted"] - costs[n]["quote"] for n in NAMES}
            usd = {"Mexico": 150 / CASE["fx"], "Asia": 125 / CASE["fx"]}
            f.add_trace(go.Scatter(x=e, y=[costs["Canada"]["risk_adjusted"]] * len(e), name="Canada (CAD)", line=dict(color=SLATE, width=3)))
            for n in ("Mexico", "Asia"):
                f.add_trace(go.Scatter(x=e, y=usd[n] * e + other[n], name=f"{n} (USD)", line=dict(color=COLORS[n], width=3)))
            f.add_vline(x=inp["fx"], line_dash="dot", annotation_text=f"now {inp['fx']:.2f}")
            show(f, "m3_fx_fig")
            be_mex = fx_breakeven(usd["Mexico"], other["Mexico"], costs["Canada"]["risk_adjusted"])
            be_asia = fx_breakeven(usd["Asia"], other["Asia"], costs["Canada"]["risk_adjusted"])
            st.metric("Mexico loses to Canada at", f"{be_mex:.2f}"); st.metric("Asia loses to Canada at", f"{be_asia:.2f}")
        answer("Currency moves the budget more than the ranking",
               f"Asia's USD amount is smaller, so a weaker CAD widens its lead over Mexico. A 10% CAD fall adds about "
               f"{usd['Asia'] * inp['fx'] * 0.1:.1f} a board ({cad(usd['Asia'] * inp['fx'] * 0.1 * CASE['boards'])} a year).",
               "Hedge 6–12 months of USD payments for budget certainty; set tariff and disruption triggers for the sourcing choice.")
        with st.expander("Exchange rate vs convertibility: buying vs owning (slide 18)"):
            step("<b>Buying from a supplier:</b> convertibility risk is supply risk. If the supplier's country restricts USD, "
                 "it cannot pay for imported chips: raise the disruption probability in the Assumptions panel.")
            step("<b>Owning a plant abroad:</b> profits earned in local currency can be trapped by controls on conversion, "
                 "dividends and transfers.")

    # ------------------------------------------------------------------ supplier risk & automation
    with tabs[3]:
        c1, c2 = st.columns(2)
        inp = _inputs(); costs = _costs(inp)
        lead_vs_mex = costs["Mexico"]["risk_adjusted"] - costs["Asia"]["risk_adjusted"]
        with c1:
            st.subheader("Hold-up after commitment (slide 19)")
            sw = cslider("Cost of switching suppliers later (CAD)", "m3_h_sw", 0, 400_000, CASE["switching_cost"], 10_000)
            raise_max = sw / CASE["boards"]
            st.metric("Price rise the supplier could impose", cad(raise_max, 1) + " a board")
            flip_ruler("Possible hold-up vs Asia's lead", raise_max, lead_vs_mex, 0, 40, fmt=lambda v: f"{v:.1f}",
                       left="Lead survives", right="Lead erased", good_side="left")
            note("Protections: multi-year prices, NorthStar owns the tooling, and a qualified second source as an outside option.")
        with c2:
            st.subheader("Can automation bring production home? (slide 21)")
            sav = cslider("Labour saving per board (CAD)", "m3_a_sav", 0, 60, CASE["auto_saving"], 1)
            fixed = cslider("Automation cost a year (CAD)", "m3_a_fix", 50_000, 600_000, CASE["auto_fixed"], 10_000)
            vol = np.linspace(5_000, 60_000, 56)
            f = fig(300, "Boards a year", "CAD per board")
            base = costs["Canada"]["risk_adjusted"]
            f.add_trace(go.Scatter(x=vol, y=[automation_cost(v, base, sav, fixed) for v in vol], name="Canada, automated", line=dict(color=SLATE, width=3)))
            for n in ("Mexico", "Asia"):
                f.add_trace(go.Scatter(x=vol, y=[costs[n]["risk_adjusted"]] * len(vol), name=n, line=dict(color=COLORS[n], dash="dot")))
            show(f, "m3_a_fig")
            denom = costs["Mexico"]["risk_adjusted"] - (base - sav)
            q_mex = fixed / denom if denom > 0 else float("inf")
            st.metric("Volume where automated Canada matches Mexico", f"{q_mex:,.0f}" if np.isfinite(q_mex) else "never")
        answer("Automation reverses advantage only at scale",
               "It cuts the labour gap but adds a fixed cost; scope across product lines is what brings the volume.",
               "Revisit domestic sourcing if board volume approaches the matching point.")

    # ------------------------------------------------------------------ decision & flips
    with tabs[4]:
        lede("Slides 22–23. Every threshold below is computed from the current assumptions. Change them in the Delivered cost tab.")
        inp = _inputs(); costs = _costs({**inp})
        base_costs = _costs({**inp, "tariff": 0})
        lead = base_costs["Mexico"]["risk_adjusted"] - base_costs["Asia"]["risk_adjusted"]
        other = {n: base_costs[n]["risk_adjusted"] - base_costs[n]["quote"] for n in NAMES}
        p_switch = (base_costs["Mexico"]["risk_adjusted"] - base_costs["Asia"]["delivered"]) / 40
        ds = dual_sourcing(inp["p_asia"], inp["p_mex"], 0.7, cost_asia=base_costs["Asia"]["delivered"], cost_mex=base_costs["Mexico"]["delivered"])
        rows = [
            ("Tariff on Asian boards", f"{inp['tariff']:.0%}", f"≥ {tariff_threshold(lead, base_costs['Asia']['quote']):.1%}", "Mexico cheaper"),
            ("Asia disruption risk", f"{inp['p_asia']:.0%}", f"≥ {ds['p_star']:.0%} / ≥ {p_switch:.0%}", "Add a second source / switch to Mexico"),
            ("CAD per USD", f"{inp['fx']:.2f}",
             f"{fx_breakeven(150/CASE['fx'], other['Mexico'], base_costs['Canada']['risk_adjusted']):.2f} / "
             f"{fx_breakeven(125/CASE['fx'], other['Asia'], base_costs['Canada']['risk_adjusted']):.2f}", "Mexico / Asia lose to Canada"),
            ("Hold-up price rise", "0", f"> {lead:.1f} a board", "Asia's lead gone"),
            ("US exports losing CUSMA origin", "none", "any material volume", "Prefer a CUSMA-qualifying board"),
        ]
        st.dataframe(pd.DataFrame(rows, columns=["Driver", "Now", "Flip point", "What happens"]), hide_index=True, width="stretch")
        best = min(NAMES, key=lambda n: costs[n]["risk_adjusted"])
        answer(f"Source from {best}",
               f"Risk-adjusted: Canada {costs['Canada']['risk_adjusted']:.1f}, Mexico {costs['Mexico']['risk_adjusted']:.1f}, Asia {costs['Asia']['risk_adjusted']:.1f}.",
               "Qualify a second source now (a cheap option), hedge USD payments, and act on the tariff and disruption triggers.")
