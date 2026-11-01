"""NorthStar Appliances: economic models for the BUS 703 course app.

Every default below is taken from the revised Module 1-5 fact sheets, so the app
reproduces the numbers on the slides. Functions are pure (no Streamlit) and are
checked by test_models.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, isfinite


# ---------------------------------------------------------------------------
# Case fact sheet (single source of truth)
# ---------------------------------------------------------------------------
CASE = {
    # Module 1: NorthStar's own annual demand and costs
    "a": 26_000,            # demand intercept: Q = a - b P
    "b": 20,                # buyers lost per CAD 1
    "mc": 500,              # unit variable cost, direct = 430 + 45 + 25
    "mc_parts": {"Manufacturing": 430, "Fulfilment": 45, "Payment / service": 25},
    "fixed": 2_000_000,     # fixed operating cost per year
    "cap_y1": 7_000,
    "cap_y2": 15_000,
    "retailer_share": 0.25,
    "retail_unit_cost": 455,  # 430 manufacturing + 25 bulk logistics
    "campaign": 1_200_000,
    "ai_annual": 600_000,
    "ai_saving": 100,
    "ai_capex": 2_400_000,
    "ai_life": 5,
    "rate": 0.08,
    # Module 2: year 2 after NovaHome enters (direct sales)
    "p_hold": 900, "p_cut": 850,
    "q_both_hold": 7_000, "q_cut_alone": 8_400, "q_held_vs_cut": 5_600, "q_both_cut": 7_350,
    "rival_fixed": 2_000_000,
    "fight_price": 800, "fight_units_spare": 9_500,
    "rival_units_fight_spare": 1_500, "rival_units_fight_tight": 3_000,
    "warranty_units": 10_000, "contract_years": 3, "repeat_cost": 300,
    "inhouse_cost": 145,
    "type_high": {"min_fee": 110, "failure": 15, "quote": 115, "repeat_risk": 0.04},
    "type_low": {"min_fee": 60, "failure": 70, "quote": 70, "repeat_risk": 0.175},
    "prior_low": 0.5, "pilot_cost": 50_000, "pilot_detect": 0.7,
    "effort_cost": 120_000, "repeat_low_effort": 0.12, "repeat_high_effort": 0.05,
    "p_hit_high": 0.85, "p_hit_low": 0.25, "provider_cost": 1_100_000, "monitoring_cost": 70_000,
    "hh_units": 3_000, "hh_price": 900, "hh_cannibal": 0.40,
    "hh_outside_before": 250_000, "hh_outside_after": 450_000,
    "hh_retail_a": 7_500, "hh_retail_b": 5,
    # Module 3: control board sourcing
    "boards": 10_000, "weekly_sd": 60, "z": 1.65, "carry": 0.25, "fx": 1.40,
    "disruption_loss": 400_000,
    "suppliers": {
        "Canada": {"quote": 185, "logistics": 2, "quality": 2, "lead": 1, "p_disrupt": 0.025, "usd": False},
        "Mexico": {"quote": 150, "logistics": 8, "quality": 4, "lead": 3, "p_disrupt": 0.05, "usd": True},
        "Asia":   {"quote": 125, "logistics": 14, "quality": 5, "lead": 10, "p_disrupt": 0.15, "usd": True},
    },
    "switching_cost": 150_000, "auto_saving": 30, "auto_fixed": 200_000,
    "ricardo": {"Canada": (12, 24), "Mexico": (8, 10)},
    "wages": {"Canada": 360, "Mexico": 180},
    # Module 4
    "levy": 50, "rebate": 250, "standard_cost": 1_000_000,
    # Module 5
    "v_correct": 10, "v_incorrect": 6, "plan_contribution": 40, "customers": 10_000,
    "eco_price": 999, "eco_unit_cost": 560, "std_price": 899, "eco_saving_per_year": 180,
}


def fmt_cad(x: float, digits: int = 0) -> str:
    """CAD with thousands separators; millions shown as e.g. 'CAD 3.20m'."""
    if x is None or not isfinite(x):
        return "n/a"
    if abs(x) >= 1_000_000:
        return f"CAD {x/1e6:,.2f}m"
    return f"CAD {x:,.{digits}f}"


# ---------------------------------------------------------------------------
# Module 1: pricing, costs, capacity
# ---------------------------------------------------------------------------
def demand_q(p: float, a: float = CASE["a"], b: float = CASE["b"]) -> float:
    return max(0.0, a - b * p)


def inverse_p(q: float, a: float = CASE["a"], b: float = CASE["b"]) -> float:
    return (a - q) / b


def marginal_revenue(q: float, a: float = CASE["a"], b: float = CASE["b"]) -> float:
    """MR for linear demand P = a/b - q/b: same intercept, twice the slope."""
    return a / b - 2 * q / b


def point_elasticity(p: float, a: float = CASE["a"], b: float = CASE["b"]) -> float:
    q = a - b * p
    if q <= 0:
        return float("-inf")
    return -b * p / q


def arc_elasticity(p0: float, p1: float, a: float = CASE["a"], b: float = CASE["b"]) -> float:
    q0, q1 = demand_q(p0, a, b), demand_q(p1, a, b)
    dq = (q1 - q0) / ((q1 + q0) / 2)
    dp = (p1 - p0) / ((p1 + p0) / 2)
    return dq / dp if dp else float("nan")


def mr_table(step: int = 2_000, upto: int = 10_000, a: float = CASE["a"], b: float = CASE["b"]):
    """The whiteboard table: P, TR and MR per unit over 2,000-unit steps."""
    rows = []
    prev = None
    for q in range(0, upto + step, step):
        p = inverse_p(q, a, b)
        tr = p * q
        row = {"Q": q, "P": p, "TR": tr, "dTR": None, "MR per unit": None, "MR at midpoint Q": None}
        if prev is not None:
            row["dTR"] = tr - prev["TR"]
            row["MR per unit"] = row["dTR"] / step
            row["MR at midpoint Q"] = q - step / 2
        rows.append(row)
        prev = row
    return rows


def monopoly_optimum(mc: float = CASE["mc"], a: float = CASE["a"], b: float = CASE["b"]) -> dict:
    q = max(0.0, (a - b * mc) / 2)
    p = inverse_p(q, a, b)
    return {"q": q, "p": p, "cm_unit": p - mc, "contribution": (p - mc) * q,
            "elasticity": point_elasticity(p, a, b), "lerner": (p - mc) / p if p else float("nan")}


def capacity_check(cap: float, mc: float = CASE["mc"], a: float = CASE["a"], b: float = CASE["b"]) -> dict:
    opt = monopoly_optimum(mc, a, b)
    if opt["q"] <= cap:
        return {**opt, "binding": False, "shadow": 0.0, "rationed": 0.0, "left_on_table": 0.0, "clearing_price": opt["p"]}
    p_clear = inverse_p(cap, a, b)
    mr_cap = marginal_revenue(cap, a, b)
    return {"q": cap, "p": p_clear, "cm_unit": p_clear - mc, "contribution": (p_clear - mc) * cap,
            "elasticity": point_elasticity(p_clear, a, b), "lerner": (p_clear - mc) / p_clear,
            "binding": True, "shadow": mr_cap - mc, "rationed": opt["q"] - cap,
            "left_on_table": (p_clear - opt["p"]) * cap, "clearing_price": p_clear,
            "unconstrained_p": opt["p"], "unconstrained_q": opt["q"]}


def price_cut_test(p0: float, cut_pct: float, mc: float = CASE["mc"], a: float = CASE["a"], b: float = CASE["b"]) -> dict:
    p1 = p0 * (1 - cut_pct / 100)
    q0, q1 = demand_q(p0, a, b), demand_q(p1, a, b)
    cm0, cm1 = p0 - mc, p1 - mc
    contrib0, contrib1 = cm0 * q0, cm1 * q1
    q_needed = contrib0 / cm1 if cm1 > 0 else float("inf")
    return {"p0": p0, "p1": p1, "q0": q0, "q1": q1, "tr0": p0 * q0, "tr1": p1 * q1,
            "contrib0": contrib0, "contrib1": contrib1, "q_needed": q_needed,
            "req_pct": (q_needed / q0 - 1) * 100 if q0 else float("inf"),
            "got_pct": (q1 / q0 - 1) * 100 if q0 else float("inf"),
            "rule_pct": (p0 - p1) / (cm0 - (p0 - p1)) * 100 if cm0 > (p0 - p1) else float("inf")}


def channel_cm(price: float = 900, mc_direct: float = CASE["mc"], retailer_share: float = CASE["retailer_share"],
               retail_unit_cost: float = CASE["retail_unit_cost"]) -> dict:
    direct = price - mc_direct
    received = price * (1 - retailer_share)
    retail = received - retail_unit_cost
    return {"direct": direct, "retail_received": received, "retail": retail,
            "cannibal_threshold": retail / direct if direct > 0 else float("nan"), "gap": direct - retail}


def break_even(fixed: float, cm: float) -> float:
    return fixed / cm if cm > 0 else float("inf")


def ai_value(units: float, saving: float = CASE["ai_saving"], annual: float = CASE["ai_annual"]) -> dict:
    return {"gross": units * saving, "net": units * saving - annual, "break_even": break_even(annual, saving)}


def markup_price(mc: float, eps_abs: float) -> float:
    return mc * eps_abs / (eps_abs - 1) if eps_abs > 1 else float("inf")


def pass_through(mc_old: float, mc_new: float, a: float = CASE["a"], b: float = CASE["b"], cap: float | None = None) -> dict:
    """Who captures a cost change: firm contribution and consumer surplus before/after."""
    def outcome(mc):
        r = capacity_check(cap, mc, a, b) if cap else monopoly_optimum(mc, a, b)
        cs = 0.5 * r["q"] * (a / b - r["p"])
        return r, cs
    r0, cs0 = outcome(mc_old)
    r1, cs1 = outcome(mc_new)
    dmc = mc_new - mc_old
    return {"p0": r0["p"], "p1": r1["p"], "q0": r0["q"], "q1": r1["q"],
            "firm0": r0["contribution"], "firm1": r1["contribution"], "cs0": cs0, "cs1": cs1,
            "pass_through": (r1["p"] - r0["p"]) / dmc if dmc else float("nan")}


def scaled_demand_outcome(s: float, cap: float = CASE["cap_y1"], mc: float = CASE["mc"],
                          a: float = CASE["a"], b: float = CASE["b"], fixed: float = CASE["fixed"]) -> dict:
    """Demand scaled by s (Q = s(a - bP)): price, units, contribution with a capacity limit."""
    r = capacity_check(cap, mc, s * a, s * b)
    return {**r, "operating_profit": r["contribution"] - fixed}


# ---------------------------------------------------------------------------
# Module 2: games, information, contracts, bargaining
# ---------------------------------------------------------------------------
def price_game(q_both_hold=CASE["q_both_hold"], q_cut_alone=CASE["q_cut_alone"], q_held_vs_cut=CASE["q_held_vs_cut"],
               q_both_cut=CASE["q_both_cut"], p_hold=CASE["p_hold"], p_cut=CASE["p_cut"], mc=CASE["mc"]) -> dict:
    """Symmetric 2x2 price game in CAD contribution. Returns payoffs (row, col) in CAD."""
    C = (p_hold - mc) * q_both_hold
    T = (p_cut - mc) * q_cut_alone
    S = (p_hold - mc) * q_held_vs_cut
    P = (p_cut - mc) * q_both_cut
    matrix = {("Hold", "Hold"): (C, C), ("Hold", "Cut"): (S, T), ("Cut", "Hold"): (T, S), ("Cut", "Cut"): (P, P)}
    br_if_hold = "Cut" if T > C else ("Hold" if C > T else "Tie")
    br_if_cut = "Cut" if P > S else ("Hold" if S > P else "Tie")
    dominant = br_if_hold if br_if_hold == br_if_cut and br_if_hold != "Tie" else None
    # pure-strategy Nash equilibria of the symmetric game
    ne = []
    for r in ("Hold", "Cut"):
        for c in ("Hold", "Cut"):
            row_pay, col_pay = matrix[(r, c)]
            other_r = "Cut" if r == "Hold" else "Hold"
            other_c = "Cut" if c == "Hold" else "Hold"
            if row_pay >= matrix[(other_r, c)][0] and col_pay >= matrix[(r, other_c)][1]:
                ne.append((r, c))
    return {"C": C, "T": T, "S": S, "P": P, "matrix": matrix, "br_if_hold": br_if_hold,
            "br_if_cut": br_if_cut, "dominant": dominant, "nash": ne,
            "dilemma": dominant == "Cut" and P < C}


def repeated_threshold(C: float, T: float, P: float) -> float:
    """Grim trigger: hold if delta >= (T - C) / (T - P)."""
    if T <= C:
        return 0.0
    if T <= P:
        return float("inf")
    return (T - C) / (T - P)


def delta_from(p_continue: float, rate: float) -> float:
    return p_continue / (1 + rate)


def detection_lag_threshold(C: float, T: float, P: float, lag_periods: int) -> float:
    """With a k-period lag, hold if delta^k >= (T - C)/(T - P)."""
    base = repeated_threshold(C, T, P)
    if base <= 0:
        return 0.0
    if base >= 1:
        return float("inf")
    return base ** (1 / lag_periods)


def credibility(capacity_for_fight: float, fight_price=CASE["fight_price"], mc=CASE["mc"],
                accommodate=None, rival_units_fight=None, rival_fixed=CASE["rival_fixed"]) -> dict:
    accommodate = (CASE["p_hold"] - mc) * CASE["q_both_hold"] if accommodate is None else accommodate
    fight = (fight_price - mc) * capacity_for_fight
    credible = fight > accommodate
    needed = accommodate / (fight_price - mc) if fight_price > mc else float("inf")
    rival_accommodate = (CASE["p_hold"] - mc) * CASE["q_both_hold"] - rival_fixed
    if rival_units_fight is None:
        rival_units_fight = CASE["rival_units_fight_spare"] if credible else CASE["rival_units_fight_tight"]
    rival_fight = (fight_price - mc) * rival_units_fight - rival_fixed
    rival_enters = rival_fight >= 0 if credible else rival_accommodate >= 0
    ns_payoff = monopoly_optimum(mc)["contribution"] if not rival_enters else (fight if credible else accommodate)
    return {"fight": fight, "accommodate": accommodate, "credible": credible, "units_needed": needed,
            "rival_accommodate": rival_accommodate, "rival_fight": rival_fight,
            "rival_enters": rival_enters, "northstar": ns_payoff}


def first_mover(cost=700_000, extra_units=1_750, cm=450, time_shift=0.0) -> dict:
    inc = extra_units * (1 - time_shift)
    be = cost / cm
    return {"incremental_units": inc, "net": inc * cm - cost, "break_even_units": be,
            "max_time_shift": max(0.0, 1 - be / extra_units)}


def lemons(high=CASE["type_high"], low=CASE["type_low"], inhouse=CASE["inhouse_cost"], p_high=0.5,
           units=CASE["warranty_units"]) -> dict:
    max_h, max_l = inhouse - high["failure"], inhouse - low["failure"]
    avg = p_high * max_h + (1 - p_high) * max_l
    high_exits = avg < high["min_fee"]
    lost_trade = (max_h - high["min_fee"]) * units if high_exits else 0.0
    return {"max_high": max_h, "max_low": max_l, "avg_offer": avg, "high_exits": high_exits,
            "final_offer_cap": max_l if high_exits else avg, "lost_trade": lost_trade,
            "cost_high_total": high["quote"] + high["failure"], "cost_low_total": low["quote"] + low["failure"]}


def signalling(coverage=1.0, repeat_cost=CASE["repeat_cost"], high=CASE["type_high"], low=CASE["type_low"]) -> dict:
    cost_h = high["repeat_risk"] * repeat_cost * coverage
    cost_l = low["repeat_risk"] * repeat_cost * coverage
    reward = high["quote"] - low["quote"]
    separating = cost_h < reward < cost_l
    min_cov = reward / (low["repeat_risk"] * repeat_cost)
    return {"cost_h": cost_h, "cost_l": cost_l, "reward": reward, "separating": separating,
            "min_coverage": min_cov}


def pilot_value(prior_low=CASE["prior_low"], detect=CASE["pilot_detect"], loss=300_000, cost=CASE["pilot_cost"]) -> dict:
    benefit = prior_low * detect * loss
    perfect = prior_low * loss
    return {"benefit": benefit, "net": benefit - cost, "perfect_info": perfect,
            "share_of_perfect": benefit / perfect if perfect else 0,
            "break_even_detect": cost / (prior_low * loss) if prior_low * loss else float("inf")}


def ai_screen(flagged=30, true_high=18, base_rate_high=0.5, loss=300_000) -> dict:
    precision = true_high / flagged if flagged else 0
    return {"precision": precision, "lift_pp": (precision - base_rate_high) * 100,
            "expected_loss_flagged": (1 - precision) * loss,
            "expected_loss_random": (1 - base_rate_high) * loss,
            "value_per_hire": (precision - base_rate_high) * loss}


def contract_design(p_high=CASE["p_hit_high"], p_low=CASE["p_hit_low"], effort_cost=CASE["effort_cost"],
                    provider_cost=CASE["provider_cost"], bonus=None, units=CASE["warranty_units"],
                    repeat_cost=CASE["repeat_cost"], r_low=CASE["repeat_low_effort"], r_high=CASE["repeat_high_effort"],
                    monitoring=CASE["monitoring_cost"]) -> dict:
    dp = p_high - p_low
    b_min = effort_cost / dp if dp > 0 else float("inf")
    b = b_min if bonus is None else bonus
    induces = dp * b >= effort_cost - 1e-9
    base = provider_cost + effort_cost - p_high * b
    expected_pay = base + p_high * b
    ns_incentive = expected_pay + r_high * units * repeat_cost
    ns_flat = provider_cost + r_low * units * repeat_cost
    effort_value = (r_low - r_high) * units * repeat_cost
    return {"dp": dp, "bonus_min": b_min, "bonus": b, "induces_effort": induces, "base": base,
            "expected_pay": expected_pay, "northstar_incentive": ns_incentive, "northstar_flat": ns_flat,
            "saving": ns_flat - ns_incentive, "saving_after_monitoring": ns_flat - ns_incentive - monitoring,
            "effort_value": effort_value, "effort_efficient": effort_value > effort_cost,
            "gain_from_effort_at_bonus": dp * b}


def homehub_bargain(outside_hh=CASE["hh_outside_after"], cannibal=CASE["hh_cannibal"], units=CASE["hh_units"],
                    price=CASE["hh_price"], retail_cost=CASE["retail_unit_cost"], cm_direct=None, share_ns=0.5,
                    ask_margin=0.30) -> dict:
    cm_direct = (price - CASE["mc"]) if cm_direct is None else cm_direct
    V = units * (price - retail_cost)
    d_ns = cannibal * units * cm_direct
    S = V - d_ns - outside_hh
    hh = outside_hh + (1 - share_ns) * S
    ns = d_ns + share_ns * S
    sales = units * price
    ask_hh = ask_margin * sales
    return {"V": V, "d_ns": d_ns, "d_hh": outside_hh, "surplus": S, "hh": hh, "ns": ns,
            "fair_margin": hh / sales, "walkaway_margin": (V - d_ns) / sales,
            "ns_at_ask": V - ask_hh, "ns_floor": d_ns, "feasible": S >= 0}


def retail_contract_forms(a_r=CASE["hh_retail_a"], b_r=CASE["hh_retail_b"], cost=CASE["retail_unit_cost"],
                          parity_price=900, wholesale=675) -> list[dict]:
    choke = a_r / b_r
    def q(p): return max(0.0, a_r - b_r * p)
    p_w = (choke + wholesale) / 2
    p_tpt = (choke + cost) / 2
    rows = [
        {"Contract": "Margin share, price parity", "Shelf price": parity_price, "Units": q(parity_price),
         "Joint margin": (parity_price - cost) * q(parity_price), "NorthStar": None},
        {"Contract": f"Wholesale price {wholesale:,.0f}", "Shelf price": p_w, "Units": q(p_w),
         "Joint margin": (p_w - cost) * q(p_w), "NorthStar": (wholesale - cost) * q(p_w)},
        {"Contract": "Two-part tariff (at cost + fixed fee)", "Shelf price": p_tpt, "Units": q(p_tpt),
         "Joint margin": (p_tpt - cost) * q(p_tpt), "NorthStar": None},
    ]
    return rows


# ---------------------------------------------------------------------------
# Module 3: comparative advantage and sourcing
# ---------------------------------------------------------------------------
def comparative_advantage(a_board, a_sensor, b_board, b_sensor, name_a="Canada", name_b="Mexico") -> dict:
    oc_a, oc_b = a_sensor / a_board, b_sensor / b_board
    comp_board = name_a if oc_a < oc_b else name_b if oc_b < oc_a else "Neither"
    comp_sensor = (name_b if comp_board == name_a else name_a) if comp_board != "Neither" else "Neither"
    return {"oc_board_a": oc_a, "oc_board_b": oc_b, "oc_sensor_a": 1 / oc_a, "oc_sensor_b": 1 / oc_b,
            "abs_board": name_a if a_board > b_board else name_b if b_board > a_board else "Tie",
            "abs_sensor": name_a if a_sensor > b_sensor else name_b if b_sensor > a_sensor else "Tie",
            "comp_board": comp_board, "comp_sensor": comp_sensor,
            "tot_low": min(oc_a, oc_b), "tot_high": max(oc_a, oc_b)}


def specialization_gain(a=(12, 24), b=(8, 10), workers=10) -> dict:
    """Same workers, same board output: compare a 50/50 split with specialization by comparative advantage."""
    split_boards = workers / 2 * (a[0] + b[0])
    split_sensors = workers / 2 * (a[1] + b[1])
    oc_a, oc_b = a[1] / a[0], b[1] / b[0]
    lo, hi = (b, a) if oc_b < oc_a else (a, b)      # lo = lower opportunity cost of boards
    if workers * lo[0] >= split_boards:              # board specialist covers all boards
        lo_board_workers = split_boards / lo[0]
        sensors = (workers - lo_board_workers) * lo[1] + workers * hi[1]
        hi_board_workers = 0.0
    else:
        hi_board_workers = (split_boards - workers * lo[0]) / hi[0]
        sensors = (workers - hi_board_workers) * hi[1]
    return {"split": {"boards": split_boards, "sensors": split_sensors},
            "spec": {"boards": split_boards, "sensors": sensors, "hi_workers_on_boards": hi_board_workers},
            "extra_sensors": sensors - split_sensors}


def wage_band(a=(12, 24), b=(8, 10)) -> tuple[float, float]:
    """Relative wage w_a/w_b range consistent with b making boards and a making sensors."""
    return a[0] / b[0], a[1] / b[1]


def unit_labour_costs(w_a, w_b, a=(12, 24), b=(8, 10)) -> dict:
    return {"board_a": w_a / a[0], "board_b": w_b / b[0], "sensor_a": w_a / a[1], "sensor_b": w_b / b[1]}


def inventory_cost_per_unit(lead_weeks, unit_value, weekly_demand=CASE["boards"] / 52, sd=CASE["weekly_sd"],
                            z=CASE["z"], carry=CASE["carry"], volume=CASE["boards"]) -> dict:
    pipeline = weekly_demand * lead_weeks
    safety = z * sd * sqrt(lead_weeks)
    annual = (pipeline + safety) * unit_value * carry
    return {"pipeline": pipeline, "safety": safety, "annual": annual, "per_unit": annual / volume}


def supplier_costs(name, fx=CASE["fx"], tariff=0.0, p_disrupt=None, carry=CASE["carry"], quality=None,
                   lead=None, quote_override=None) -> dict:
    s = CASE["suppliers"][name]
    base_quote = s["quote"] if quote_override is None else quote_override
    quote = base_quote * (fx / CASE["fx"]) if s["usd"] else base_quote
    lead = s["lead"] if lead is None else lead
    inv = inventory_cost_per_unit(lead, s["quote"], carry=carry)["per_unit"]
    q = s["quality"] if quality is None else quality
    tariff_cost = quote * tariff
    delivered = quote + s["logistics"] + inv + q + tariff_cost
    p = s["p_disrupt"] if p_disrupt is None else p_disrupt
    disruption = p * CASE["disruption_loss"] / CASE["boards"]
    return {"quote": quote, "logistics": s["logistics"], "inventory": inv, "quality": q, "tariff": tariff_cost,
            "delivered": delivered, "disruption": disruption, "risk_adjusted": delivered + disruption, "lead": lead}


def case_rounded_costs() -> dict:
    """The slide table uses inventory rounded to 1 / 3 / 7."""
    out = {}
    for name, inv in [("Canada", 1), ("Mexico", 3), ("Asia", 7)]:
        s = CASE["suppliers"][name]
        delivered = s["quote"] + s["logistics"] + inv + s["quality"]
        dis = s["p_disrupt"] * CASE["disruption_loss"] / CASE["boards"]
        out[name] = {"delivered": delivered, "risk_adjusted": delivered + dis, "disruption": dis}
    return out


def dual_sourcing(p_asia=0.15, p_mex=0.05, share_asia=0.7, surge=300, loss_per_sale=400,
                  lost_if_full=1_000, cost_asia=151, cost_mex=165, units=CASE["boards"]) -> dict:
    single = units * cost_asia + p_asia * lost_if_full * loss_per_sale
    lost_asia_event = max(0.0, lost_if_full * share_asia - surge)
    lost_mex_event = lost_if_full * (1 - share_asia)
    dual = (units * share_asia * cost_asia + units * (1 - share_asia) * cost_mex
            + p_asia * lost_asia_event * loss_per_sale + p_mex * lost_mex_event * loss_per_sale)
    # break-even p_asia
    slope_single = lost_if_full * loss_per_sale
    slope_dual = lost_asia_event * loss_per_sale
    const_single = units * cost_asia
    const_dual = units * share_asia * cost_asia + units * (1 - share_asia) * cost_mex + p_mex * lost_mex_event * loss_per_sale
    p_star = (const_dual - const_single) / (slope_single - slope_dual) if slope_single > slope_dual else float("inf")
    return {"single": single, "dual": dual, "p_star": p_star}


def tariff_threshold(lead_per_unit=10, quote=125) -> float:
    return lead_per_unit / quote


def fx_breakeven(usd_quote, cad_other, target) -> float:
    return (target - cad_other) / usd_quote


def automation_cost(volume, base=191, saving=CASE["auto_saving"], fixed=CASE["auto_fixed"]) -> float:
    return base - saving + fixed / volume


# ---------------------------------------------------------------------------
# Module 4: shocks, policy, uncertainty
# ---------------------------------------------------------------------------
def annuity_factor(r: float, n: int) -> float:
    return n if r == 0 else (1 - (1 + r) ** -n) / r


def npv(annual: float, r: float, n: int = CASE["ai_life"], capex: float = CASE["ai_capex"]) -> float:
    return annual * annuity_factor(r, n) - capex


def irr_annuity(annual: float, n: int = CASE["ai_life"], capex: float = CASE["ai_capex"]) -> float:
    lo, hi = 0.0, 1.0
    if npv(annual, 0, n, capex) <= 0:
        return 0.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if npv(annual, mid, n, capex) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def general_inflation(infl: float, mc: float = CASE["mc"], a: float = CASE["a"], b: float = CASE["b"]) -> dict:
    """All reservation prices and costs scale by (1+infl): real outcomes unchanged."""
    k = 1 + infl
    r = monopoly_optimum(mc * k, a, b / k)
    return {**r, "real_contribution": r["contribution"] / k}


def relative_shock_choice(cost_increase: float, rival_hit: bool, mc=CASE["mc"]) -> dict:
    c = mc + cost_increase
    if rival_hit:
        hold = (CASE["p_hold"] - c) * CASE["q_cut_alone"]   # NorthStar now the cheaper firm
        raise_ = (950 - c) * CASE["q_both_hold"]
    else:
        hold = (CASE["p_hold"] - c) * CASE["q_both_hold"]
        raise_ = (950 - c) * CASE["q_held_vs_cut"]
    # unit cost at which raising alone beats holding (rival not hit)
    c_star = (CASE["q_both_hold"] * CASE["p_hold"] - CASE["q_held_vs_cut"] * 950) / (CASE["q_both_hold"] - CASE["q_held_vs_cut"])
    return {"hold": hold, "raise": raise_, "best": "Raise" if raise_ > hold else "Hold", "c_star": c_star}


def levy_incidence(levy: float, cap: float | None) -> dict:
    base = capacity_check(cap) if cap else monopoly_optimum()
    new = capacity_check(cap, CASE["mc"] + levy) if cap else monopoly_optimum(CASE["mc"] + levy)
    dp = new["p"] - base["p"]
    return {"p0": base["p"], "p1": new["p"], "buyer_share": dp, "firm_share": levy - dp,
            "contrib0": base["contribution"], "contrib1": new["contribution"]}


def rebate_capture(rebate: float, cap: float | None) -> dict:
    """A buyer rebate raises every reservation price by `rebate`."""
    a2 = CASE["a"] + CASE["b"] * rebate
    base = capacity_check(cap) if cap else monopoly_optimum()
    new = capacity_check(cap, CASE["mc"], a2) if cap else monopoly_optimum(CASE["mc"], a2)
    net = new["p"] - rebate
    return {"sticker0": base["p"], "sticker1": new["p"], "net_price": net, "buyer_gain": base["p"] - net,
            "firm_gain_unit": new["p"] - base["p"], "q0": base["q"], "q1": new["q"],
            "contrib0": base["contribution"], "contrib1": new["contribution"],
            "gov_cost": rebate * new["q"],
            "cost_per_extra": rebate * new["q"] / (new["q"] - base["q"]) if new["q"] > base["q"] else float("inf")}


def ceiling_on_price_setter(ceiling: float, cap: float | None = None, mc: float = CASE["mc"], fixed: float = CASE["fixed"]) -> dict:
    a, b = CASE["a"], CASE["b"]
    free = capacity_check(cap, mc) if cap else monopoly_optimum(mc)
    if ceiling >= free["p"]:
        return {"binding": False, "price": free["p"], "q": free["q"], "demand": demand_q(free["p"]),
                "shortage": 0.0, "contribution": free["contribution"], "exits": free["contribution"] < fixed,
                "regime": "Non-binding"}
    if ceiling <= mc:
        return {"binding": True, "price": ceiling, "q": 0.0, "demand": demand_q(ceiling), "shortage": demand_q(ceiling),
                "contribution": 0.0, "exits": True, "regime": "Below cost: no supply"}
    demand = demand_q(ceiling)
    q = demand if cap is None else min(demand, cap)
    contribution = (ceiling - mc) * q
    exits = contribution < fixed
    regime = "Exit: cannot cover fixed cost" if exits else ("Shortage (capacity binds)" if demand > q else "Output rises")
    return {"binding": True, "price": ceiling, "q": 0.0 if exits else q, "demand": demand,
            "shortage": demand if exits else demand - q, "contribution": contribution, "exits": exits, "regime": regime}


def exit_ceiling(mc: float = CASE["mc"], fixed: float = CASE["fixed"]) -> float:
    """Lowest ceiling at which (P - mc)(a - bP) covers fixed cost (no capacity limit)."""
    a, b = CASE["a"], CASE["b"]
    # b x^2 - (a - b mc) x + fixed = 0 with x = P - mc
    A, B, C = b, -(a - b * mc), fixed
    disc = B * B - 4 * A * C
    if disc < 0:
        return float("inf")
    return mc + (-B - sqrt(disc)) / (2 * A)


@dataclass
class Scenario:
    name: str
    prob: float
    demand_scale: float
    unit_cost: float
    rate: float
    fx: float
    ai_saving_per_unit: float


SCENARIOS = [
    Scenario("Soft landing", 0.40, 1.00, 500, 0.08, 1.40, 100),
    Scenario("Persistent inflation", 0.30, 1.00, 550, 0.12, 1.50, 120),
    Scenario("Recession", 0.30, 0.70, 500, 0.10, 1.40, 100),
]


def scenario_outcome(sc: Scenario, cap: float = CASE["cap_y1"]) -> dict:
    r = capacity_check(cap, sc.unit_cost, sc.demand_scale * CASE["a"], sc.demand_scale * CASE["b"])
    ai = npv(sc.ai_saving_per_unit * r["q"], sc.rate)
    asia = 89.29 * sc.fx + 32
    mex = 107.14 * sc.fx + 17
    return {"price": r["p"], "units": r["q"], "contribution": r["contribution"],
            "operating_profit": r["contribution"] - CASE["fixed"], "ai_npv": ai, "asia_lead": mex - asia}


def option_value(probs: list[float], npvs: list[float], rates: list[float], invest_if: list[bool]) -> dict:
    now = sum(p * v for p, v in zip(probs, npvs))
    wait = sum(p * v / (1 + r) for p, v, r, ok in zip(probs, npvs, rates, invest_if) if ok and v > 0)
    return {"now": now, "wait": wait, "value_of_waiting": wait - now, "best": "Wait / pilot" if wait > now else "Invest now"}


# ---------------------------------------------------------------------------
# Module 5: incentives, behaviour, evidence
# ---------------------------------------------------------------------------
def value_per_case(acc: float, r: float = CASE["v_correct"], l: float = CASE["v_incorrect"]) -> float:
    return r * acc - l * (1 - acc)


def threshold(reward: float, penalty: float) -> float:
    """Accuracy above which handling a case has positive value: penalty / (reward + penalty)."""
    return penalty / (reward + penalty) if reward + penalty > 0 else 0.0


def aligned_penalty(reward_points: float, firm_reward=CASE["v_correct"], firm_penalty=CASE["v_incorrect"]) -> float:
    return reward_points * firm_penalty / firm_reward


def default_margin(lift: float, customers=CASE["customers"], contribution=CASE["plan_contribution"],
                   cancel_rate=0.30, handling=15.0) -> dict:
    extra = lift * customers
    retained = extra * (1 - cancel_rate)
    cancelled = extra * cancel_rate
    gross = extra * contribution
    net = retained * contribution - cancelled * handling
    return {"extra": extra, "retained": retained, "cancelled": cancelled, "gross": gross, "net": net,
            "breakeven_cancel": contribution / (contribution + handling) if contribution + handling else 0}


def share_ci(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    se = sqrt(max(p * (1 - p), 0) / n)
    return p - z * se, p + z * se


def diff_props(p1: float, n1: int, p0: float, n0: int, z: float = 1.96) -> dict:
    if n1 <= 0 or n0 <= 0:
        return {"diff": float("nan"), "se": float("nan"), "lo": float("nan"), "hi": float("nan")}
    se = sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    d = p1 - p0
    return {"diff": d, "se": se, "lo": d - z * se, "hi": d + z * se}


def diff_means(m1: float, s1: float, n1: int, m0: float, s0: float, n0: int, z: float = 1.96) -> dict:
    if n1 <= 1 or n0 <= 1:
        return {"diff": m1 - m0, "se": float("nan"), "lo": float("nan"), "hi": float("nan")}
    se = sqrt(s1 ** 2 / n1 + s0 ** 2 / n0)
    d = m1 - m0
    return {"diff": d, "se": se, "lo": d - z * se, "hi": d + z * se}


def mde(p: float, n_per_arm: int, multiplier: float = 2.8) -> float:
    """Minimum detectable effect for two equal arms with baseline share p (80% power, 5% test)."""
    if n_per_arm <= 0:
        return float("inf")
    return multiplier * sqrt(2 * p * (1 - p) / n_per_arm)


def did(treat_before, treat_after, comp_before, comp_after) -> dict:
    growth = comp_after / comp_before - 1 if comp_before else 0
    counterfactual = treat_before * (1 + growth)
    return {"comp_growth": growth, "counterfactual": counterfactual, "effect": treat_after - counterfactual,
            "naive": treat_after - treat_before}


def scale_decision(lo_value: float, hi_value: float, cost: float, trust_fell: bool = False) -> str:
    if hi_value < cost:
        return "Stop"
    if trust_fell and lo_value > 0:
        return "Revise"
    if lo_value > cost:
        return "Scale (keep a holdout)"
    return "Test further"


def safety_stock_multiplier(n_skus: int) -> float:
    return sqrt(n_skus)
