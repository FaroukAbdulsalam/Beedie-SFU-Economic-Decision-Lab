"""Checks that the app reproduces the numbers on the revised Module 1-5 slides.

Run:  python test_models.py
"""
from models import *


def close(a, b, tol=0.01):
    return abs(a - b) <= tol


def check(name, cond):
    if not cond:
        raise AssertionError(name)


def run():
    # ---------------- Module 1
    opt = monopoly_optimum()
    check("M1 optimum Q", close(opt["q"], 8000)); check("M1 optimum P", close(opt["p"], 900))
    check("M1 contribution 3.2m", close(opt["contribution"], 3_200_000))
    check("M1 elasticity at 900", close(opt["elasticity"], -2.25))
    check("M1 Lerner", close(opt["lerner"], 1 / 2.25, 1e-6))
    t = mr_table()
    check("M1 MR table 6k-8k = 600", close(t[4]["MR per unit"], 600))
    check("M1 MR(8000)=500", close(marginal_revenue(8000), 500))
    cap = capacity_check(CASE["cap_y1"])
    check("M1 capacity price 950", close(cap["p"], 950)); check("M1 shadow 100", close(cap["shadow"], 100))
    check("M1 capacity contribution", close(cap["contribution"], 3_150_000))
    check("M1 rationing loss", close(cap["left_on_table"], 350_000))
    check("M1 arc elasticity", close(arc_elasticity(800, 600), -1.1667, 1e-3))
    pc = price_cut_test(900, 10)
    check("M1 price cut q1", close(pc["q1"], 9800)); check("M1 required %", close(pc["req_pct"], 29.03, 0.05))
    check("M1 rule %", close(pc["rule_pct"], 29.03, 0.05))
    ch = channel_cm()
    check("M1 direct CM", close(ch["direct"], 400)); check("M1 retail CM", close(ch["retail"], 220))
    check("M1 cannibal 55%", close(ch["cannibal_threshold"], 0.55))
    check("M1 campaign BE", close(break_even(1_200_000, 400), 3000))
    check("M1 AI BE", close(ai_value(7000)["break_even"], 6000)); check("M1 AI net y1", close(ai_value(7000)["net"], 100_000))
    ptr = pass_through(500, 400)
    check("M1 pass-through 50%", close(ptr["pass_through"], 0.5)); check("M1 AI price 850", close(ptr["p1"], 850))
    check("M1 CS after", close(ptr["cs1"], 2_025_000))
    check("M1 markup segment", close(markup_price(650, 2.0), 1300))
    s_low = scaled_demand_outcome(0.8)
    check("M1 -20% price", close(s_low["p"], 900)); check("M1 -20% units", close(s_low["q"], 6400))
    s_high = scaled_demand_outcome(1.2)
    check("M1 +20% price", close(s_high["p"], 1008.33, 0.05)); check("M1 +20% shadow", close(s_high["shadow"], 216.67, 0.05))

    # ---------------- Module 2
    g = price_game()
    check("M2 C", close(g["C"], 2_800_000)); check("M2 T", close(g["T"], 2_940_000))
    check("M2 S", close(g["S"], 2_240_000)); check("M2 P", close(g["P"], 2_572_500))
    check("M2 dominant cut", g["dominant"] == "Cut"); check("M2 NE", g["nash"] == [("Cut", "Cut")])
    check("M2 dilemma", g["dilemma"])
    check("M2 delta*", close(repeated_threshold(g["C"], g["T"], g["P"]), 0.381, 1e-3))
    check("M2 delta example", close(delta_from(0.8, 0.10), 0.727, 1e-3))
    tight = credibility(CASE["cap_y1"]); spare = credibility(CASE["fight_units_spare"])
    check("M2 empty threat", not tight["credible"] and close(tight["fight"], 2_100_000))
    check("M2 credible threat", spare["credible"] and close(spare["fight"], 2_850_000))
    check("M2 rival out", not spare["rival_enters"]); check("M2 units needed", close(spare["units_needed"], 9333.3, 0.1))
    check("M2 first mover", close(first_mover()["net"], 87_500) and close(first_mover(time_shift=0.2)["net"], -70_000))
    lm = lemons()
    check("M2 lemons avg", close(lm["avg_offer"], 102.5)); check("M2 high exits", lm["high_exits"])
    check("M2 lost trade", close(lm["lost_trade"], 200_000))
    sg = signalling()
    check("M2 signal costs", close(sg["cost_h"], 12) and close(sg["cost_l"], 52.5) and close(sg["reward"], 45))
    check("M2 separating", sg["separating"]); check("M2 min coverage", close(sg["min_coverage"], 0.857, 1e-3))
    check("M2 half coverage pools", not signalling(0.5)["separating"])
    pv = pilot_value()
    check("M2 pilot net", close(pv["net"], 55_000)); check("M2 perfect info", close(pv["perfect_info"], 150_000))
    check("M2 pilot BE detect", close(pv["break_even_detect"], 0.333, 1e-3))
    ai = ai_screen()
    check("M2 precision", close(ai["precision"], 0.6)); check("M2 AI value", close(ai["value_per_hire"], 30_000))
    cd = contract_design()
    check("M2 bonus", close(cd["bonus_min"], 200_000)); check("M2 base", close(cd["base"], 1_050_000))
    check("M2 saving", close(cd["saving"], 90_000)); check("M2 after monitoring", close(cd["saving_after_monitoring"], 20_000))
    check("M2 120k bonus fails", not contract_design(bonus=120_000)["induces_effort"])
    hb = homehub_bargain()
    check("M2 V", close(hb["V"], 1_335_000)); check("M2 fair margin", close(hb["fair_margin"], 0.2417, 1e-3))
    check("M2 walkaway", close(hb["walkaway_margin"], 0.3167, 1e-3)); check("M2 ns at ask", close(hb["ns_at_ask"], 525_000))
    check("M2 before Nova", close(homehub_bargain(CASE["hh_outside_before"])["fair_margin"], 0.2046, 1e-3))
    rc = retail_contract_forms()
    check("M2 wholesale price", close(rc[1]["Shelf price"], 1087.5)); check("M2 TPT joint", close(rc[2]["Joint margin"], 1_365_031.25, 1))

    # ---------------- Module 3
    ca = comparative_advantage(12, 24, 8, 10)
    check("M3 comparative", ca["comp_board"] == "Mexico" and ca["comp_sensor"] == "Canada")
    sp = specialization_gain()
    check("M3 extra sensors", close(sp["extra_sensors"], 30))
    check("M3 wage band", wage_band() == (1.5, 2.4))
    inv = inventory_cost_per_unit(10, 125)
    check("M3 Asia inventory", close(inv["per_unit"], 6.99, 0.02))
    check("M3 Mexico inventory", close(inventory_cost_per_unit(3, 150)["per_unit"], 2.81, 0.02))
    rr = case_rounded_costs()
    check("M3 delivered", [rr[k]["delivered"] for k in ("Canada", "Mexico", "Asia")] == [190, 165, 151])
    check("M3 risk adjusted", [rr[k]["risk_adjusted"] for k in ("Canada", "Mexico", "Asia")] == [191, 167, 157])
    ds = dual_sourcing()
    check("M3 dual single", close(ds["single"], 1_570_000)); check("M3 dual", close(ds["dual"], 1_582_000))
    check("M3 dual threshold", close(ds["p_star"], 0.20, 1e-3))
    check("M3 tariff threshold", close(tariff_threshold(), 0.08))
    check("M3 FX Mexico", close(fx_breakeven(107.14, 17, 191), 1.624, 1e-3))
    check("M3 FX Asia", close(fx_breakeven(89.29, 32, 191), 1.781, 1e-3))
    check("M3 automation 30k", close(automation_cost(30_000), 167.67, 0.01))

    # ---------------- Module 4
    check("M4 annuity 8%", close(annuity_factor(0.08, 5), 3.9927, 1e-4))
    check("M4 AI NPV 8%", close(npv(700_000, 0.08), 394_897, 1)); check("M4 AI NPV 12%", close(npv(700_000, 0.12), 123_343, 5))
    check("M4 IRR ~14%", close(irr_annuity(700_000), 0.1405, 1e-3))
    gi = general_inflation(0.10)
    check("M4 general inflation price", close(gi["p"], 990)); check("M4 real unchanged", close(gi["real_contribution"], 3_200_000))
    cs = monopoly_optimum(550)
    check("M4 cost shock", close(cs["p"], 925) and close(cs["contribution"], 2_812_500))
    rs = relative_shock_choice(50, rival_hit=False)
    check("M4 relative shock hold", rs["best"] == "Hold" and close(rs["c_star"], 700))
    lv2, lv1 = levy_incidence(50, None), levy_incidence(50, CASE["cap_y1"])
    check("M4 levy slack", close(lv2["buyer_share"], 25)); check("M4 levy binding", close(lv1["buyer_share"], 0))
    rb2, rb1 = rebate_capture(250, None), rebate_capture(250, CASE["cap_y1"])
    check("M4 rebate slack", close(rb2["sticker1"], 1025) and close(rb2["q1"], 10_500) and close(rb2["buyer_gain"], 125))
    check("M4 rebate binding", close(rb1["sticker1"], 1200) and close(rb1["buyer_gain"], 0))
    check("M4 cost per extra", close(rb2["cost_per_extra"], 1050))
    c850 = ceiling_on_price_setter(850)
    check("M4 ceiling raises output", close(c850["q"], 9000) and c850["regime"] == "Output rises")
    c900 = ceiling_on_price_setter(900, CASE["cap_y1"])
    check("M4 ceiling shortage", close(c900["shortage"], 1000))
    check("M4 exit ceiling", close(exit_ceiling(), 655.05, 0.01))
    outs = [scenario_outcome(s) for s in SCENARIOS]
    check("M4 scenario contributions", [round(o["contribution"]) for o in outs] == [3_150_000, 2_800_000, 2_240_000])
    check("M4 scenario AI NPV", close(outs[0]["ai_npv"], 394_897, 1) and close(outs[2]["ai_npv"], -277_159, 1))
    ov = option_value([s.prob for s in SCENARIOS], [o["ai_npv"] for o in outs], [s.rate for s in SCENARIOS], [True, True, False])
    check("M4 invest now", close(ov["now"], 263_215, 5)); check("M4 value of waiting", close(ov["value_of_waiting"], 51_261, 5))

    # ---------------- Module 5
    check("M5 threshold firm", close(threshold(10, 6), 0.375)); check("M5 threshold balanced", close(threshold(2, 2), 0.5))
    check("M5 aligned penalty", close(aligned_penalty(2), 1.2))
    check("M5 value per case", close(value_per_case(0.85) * 20, 152))
    dm = default_margin(0.20)
    check("M5 default gross", close(dm["gross"], 80_000)); check("M5 default net", close(dm["net"], 47_000))
    check("M5 break-even cancel", close(dm["breakeven_cancel"], 0.727, 1e-3))
    dp = diff_props(0.6, 30, 0.3, 30)
    check("M5 SE", close(dp["se"], 0.1225, 1e-3)); check("M5 CI low", close(dp["lo"], 0.06, 1e-2))
    check("M5 MDE", close(mde(0.45, 30), 0.36, 0.02))
    d = did(10_000, 12_000, 9_000, 10_350)
    check("M5 DiD", close(d["effect"], 500))
    check("M5 sqrt n", close(safety_stock_multiplier(4), 2))
    print("All model checks passed: the app reproduces the revised slide numbers.")


if __name__ == "__main__":
    run()
