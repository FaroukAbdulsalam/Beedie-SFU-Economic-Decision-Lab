from math import sqrt

POLICY_MAP = {
    "High inflation": {
        "objective": "Restore price stability",
        "response": "Higher interest rates, tighter fiscal stance, targeted subsidies",
        "business": "Financing costs may rise; durable-goods demand may soften; input and wage pressure may persist. Revisit pricing, inventory and investment timing."
    },
    "Weak growth or unemployment": {
        "objective": "Support activity",
        "response": "Lower rates, fiscal stimulus, tax relief, public spending",
        "business": "Demand may receive support and financing may ease. Revisit sales forecasts, capacity plans and investment timing."
    },
    "Fiscal deficit or revenue shortfall": {
        "objective": "Raise revenue or reduce spending",
        "response": "Taxes, fees, subsidy cuts, spending restraint, borrowing",
        "business": "After-tax profitability, household demand, energy rebates and government procurement may change. Build fiscal-policy scenarios."
    },
    "Currency depreciation or falling reserves": {
        "objective": "Preserve external stability",
        "response": "Rate increases, FX intervention, import restrictions, capital controls",
        "business": "Imported costs may rise; supplier payments and currency conversion may become harder; sourcing and liquidity plans should be revisited."
    },
    "Affordability pressure": {
        "objective": "Protect households",
        "response": "Subsidies, transfers, price ceilings, supply-side measures",
        "business": "Demand can shift, but price controls or targeted support may change margins and product mix. Examine incidence and eligibility."
    },
    "Strategic-industry concerns": {
        "objective": "Build domestic capacity",
        "response": "Tariffs, local-content rules, public procurement, industrial subsidies",
        "business": "Relative sourcing costs can change and domestic production may become more attractive. Recalculate delivered cost and compliance exposure."
    },
    "Environmental objectives": {
        "objective": "Change behaviour",
        "response": "Carbon taxes, efficiency standards, green subsidies, reporting rules",
        "business": "Product design, energy efficiency, compliance costs and green-product demand may change. Revisit product positioning and investment."
    },
}

def demand_quantity(price, a_d=26000, b_d=20):
    return a_d - b_d*price

def supply_quantity(price, a_s=-6000, b_s=20):
    return a_s + b_s*price

def equilibrium(a_d=26000,b_d=20,a_s=-6000,b_s=20):
    price = (a_d-a_s)/(b_d+b_s)
    quantity = demand_quantity(price,a_d,b_d)
    return {"price":price,"quantity":quantity}

def point_elasticity(price,a_d=26000,b_d=20):
    q = demand_quantity(price,a_d,b_d)
    if q <= 0:
        return float("-inf")
    return -b_d*price/q

def pricing_scenarios(price,marginal_cost,a_d=26000,b_d=20):
    out=[]
    for label,mult in [("5% lower",0.95),("Current",1.0),("5% higher",1.05)]:
        p=price*mult
        q=max(0,demand_quantity(p,a_d,b_d))
        revenue=p*q
        unit_margin=p-marginal_cost
        total=unit_margin*q
        out.append({
            "label":label,"price":p,"quantity":q,"revenue":revenue,
            "unit_margin":unit_margin,"total_contribution":total
        })
    return out

def game_expected_payoffs(p_rival_discount,payoff_MM,payoff_MD,payoff_DM,payoff_DD):
    p=p_rival_discount
    maintain=(1-p)*payoff_MM+p*payoff_MD
    discount=(1-p)*payoff_DM+p*payoff_DD
    best="Maintain" if maintain>=discount else "Discount"
    return {"maintain":maintain,"discount":discount,"best_action":best}

def adverse_selection(p_good,value_good,value_bad,contract_price,screening_cost,screened_p_good):
    no_screen=p_good*value_good+(1-p_good)*value_bad-contract_price
    screen=screened_p_good*value_good+(1-screened_p_good)*value_bad-contract_price-screening_cost
    if screen>no_screen and screen>0:
        action="Screen first"
        rec="Screening creates enough expected value to justify its cost under the current assumptions."
    elif no_screen>=screen and no_screen>0:
        action="Contract without screening"
        rec="The expected benefit of screening does not currently justify the screening cost."
    else:
        action="Do not contract"
        rec="Expected net value is negative under both options; renegotiate price or improve information before contracting."
    return {"no_screen":no_screen,"screen":screen,"best_action":action,"recommendation":rec}

def moral_hazard(base_wage,bonus,p_low,p_high,effort_cost,firm_value):
    u_low=base_wage+bonus*p_low
    u_high=base_wage+bonus*p_high-effort_cost
    effort="High effort" if u_high>=u_low else "Low effort"
    p=p_high if effort=="High effort" else p_low
    profit=firm_value*p-base_wage-bonus*p
    if effort=="High effort":
        rec="The incentive is strong enough to induce high effort. Check whether the higher success probability creates enough firm value to cover the bonus."
    else:
        rec="The current bonus does not induce high effort. Consider a stronger incentive, better monitoring, or redesigning the task."
    return {"u_low":u_low,"u_high":u_high,"effort_choice":effort,"firm_profit":profit,"recommendation":rec}

def signalling_model(contract_benefit,signal_cost_high,signal_cost_low,outside_high,outside_low):
    high_signal=contract_benefit-signal_cost_high
    low_signal=contract_benefit-signal_cost_low
    high_wants=high_signal>outside_high
    low_wants=low_signal>outside_low
    separating=high_wants and not low_wants
    if separating:
        interpretation="The signal is cheaper or more valuable for the high-quality type, so only that type finds it worthwhile."
        recommendation="NorthStar can place more weight on the signal, while still checking whether it is verifiable and difficult to imitate."
    elif high_wants and low_wants:
        interpretation="Both types want to send the signal, so the signal does not separate quality."
        recommendation="Do not treat this signal as strong evidence of quality; redesign the signal or add screening."
    else:
        interpretation="The signal does not generate a clean separating equilibrium under the current assumptions."
        recommendation="Revisit the signal cost, contract value, or outside options before relying on signalling."
    return {
        "high_signal_payoff":high_signal,"low_signal_payoff":low_signal,
        "separating":separating,"interpretation":interpretation,"recommendation":recommendation
    }

def trade_advantage(a_board,a_sensor,b_board,b_sensor,name_a="A",name_b="B"):
    abs_board=name_a if a_board>b_board else name_b if b_board>a_board else "Tie"
    abs_sensor=name_a if a_sensor>b_sensor else name_b if b_sensor>a_sensor else "Tie"
    oc_board_a=a_sensor/a_board
    oc_sensor_a=a_board/a_sensor
    oc_board_b=b_sensor/b_board
    oc_sensor_b=b_board/b_sensor
    comp_board=name_a if oc_board_a<oc_board_b else name_b if oc_board_b<oc_board_a else "Tie"
    comp_sensor=name_a if oc_sensor_a<oc_sensor_b else name_b if oc_sensor_b<oc_sensor_a else "Tie"
    rec=f"Based on opportunity cost, {comp_board} has comparative advantage in boards and {comp_sensor} in sensors."
    return {
        "absolute_board":abs_board,"absolute_sensor":abs_sensor,
        "oc_board_a":oc_board_a,"oc_sensor_a":oc_sensor_a,
        "oc_board_b":oc_board_b,"oc_sensor_b":oc_sensor_b,
        "comparative_board":comp_board,"comparative_sensor":comp_sensor,
        "recommendation":rec
    }

def exchange_rate_profit(usd_component,fx_rate,other_cost,sale_price,units):
    imported=usd_component*fx_rate
    total_cost=imported+other_cost
    profit_unit=sale_price-total_cost
    total=profit_unit*units
    margin_pct=(profit_unit/sale_price*100) if sale_price else 0
    if profit_unit>0:
        rec="NorthStar remains profitable on a unit basis, but should compare the new margin with domestic/nearshore alternatives and its required margin threshold."
    else:
        rec="The current imported-cost structure eliminates unit profit. Reprice, renegotiate, hedge, redesign, or change sourcing."
    return {
        "imported_cost_cad":imported,"profit_per_unit":profit_unit,
        "total_profit":total,"margin_pct":margin_pct,"recommendation":rec
    }

def apply_ai_productivity(a_board,a_sensor,b_board,b_sensor,a_board_boost,a_sensor_boost,b_board_boost,b_sensor_boost):
    return {
        "a_board":a_board*(1+a_board_boost/100),
        "a_sensor":a_sensor*(1+a_sensor_boost/100),
        "b_board":b_board*(1+b_board_boost/100),
        "b_sensor":b_sensor*(1+b_sensor_boost/100),
    }

def policy_lookup(signal):
    return POLICY_MAP[signal]

def interpret_policy_text(text):
    t=(text or "").lower()
    keyword_map = [
        ("High inflation",["inflation","prices rising","price growth"]),
        ("Weak growth or unemployment",["unemployment","weak growth","recession","slow growth","job losses"]),
        ("Fiscal deficit or revenue shortfall",["deficit","revenue shortfall","fiscal pressure","public debt","debt service"]),
        ("Currency depreciation or falling reserves",["currency","depreciation","falling reserves","fx reserves","capital outflow","weakening"]),
        ("Affordability pressure",["affordability","cost of living","households struggling","living costs"]),
        ("Strategic-industry concerns",["strategic industry","local content","domestic capacity","industrial policy"]),
        ("Environmental objectives",["carbon","emissions","environment","green","climate"]),
    ]
    matches=[]
    for signal,keys in keyword_map:
        if any(k in t for k in keys):
            item={"signal":signal,**POLICY_MAP[signal]}
            matches.append(item)
    return {"matches":matches}

def price_control(a_d,b_d,a_s,b_s,policy_type,policy_price):
    eq=equilibrium(a_d,b_d,a_s,b_s)
    qd=max(0,demand_quantity(policy_price,a_d,b_d))
    qs=max(0,supply_quantity(policy_price,a_s,b_s))
    shortage=max(0,qd-qs)
    surplus=max(0,qs-qd)
    if policy_type=="Price ceiling":
        binding=policy_price<eq["price"]
        if binding:
            label=f"Binding ceiling → shortage of {shortage:,.0f}"
            interp="The ceiling is below equilibrium, so quantity demanded exceeds quantity supplied."
            rec="Expect non-price rationing, waiting, stockouts or reduced availability; assess how NorthStar allocates scarce supply."
        else:
            label="Non-binding ceiling"
            interp="The ceiling is at or above equilibrium, so it does not currently constrain the market."
            rec="Monitor the equilibrium; the policy becomes relevant if market-clearing price rises above the ceiling."
    else:
        binding=policy_price>eq["price"]
        if binding:
            label=f"Binding floor → surplus of {surplus:,.0f}"
            interp="The floor is above equilibrium, so quantity supplied exceeds quantity demanded."
            rec="Expect unsold inventory or excess capacity unless another mechanism absorbs the surplus."
        else:
            label="Non-binding floor"
            interp="The floor is at or below equilibrium, so it does not currently constrain the market."
            rec="Monitor the equilibrium; the policy becomes relevant if market-clearing price falls below the floor."
    return {
        "equilibrium_price":eq["price"],"equilibrium_quantity":eq["quantity"],
        "qd":qd,"qs":qs,"shortage":shortage,"surplus":surplus,
        "binding":binding,"result_label":label,"interpretation":interp,"recommendation":rec
    }

def incentive_productivity_model(base_output,base_error,productivity_gain,error_change,labor_cost,intervention_cost):
    base_error_rate=max(0,min(1,base_error/100))
    new_error_rate=max(0,min(1,(base_error+error_change)/100))
    base_effective=base_output*(1-base_error_rate)
    new_output=base_output*(1+productivity_gain/100)
    new_effective=new_output*(1-new_error_rate)
    base_cpu=labor_cost/base_effective if base_effective else float("inf")
    new_cpu=(labor_cost+intervention_cost)/new_effective if new_effective else float("inf")
    improvement=(base_cpu-new_cpu)/base_cpu*100 if base_cpu not in [0,float("inf")] else 0
    if improvement>5:
        interp="After accounting for errors and intervention cost, effective unit cost falls materially."
        rec="The intervention looks promising. Validate the result in a controlled pilot before scaling."
    elif improvement>0:
        interp="The intervention improves quality-adjusted unit cost, but only modestly."
        rec="Retest or redesign before a large rollout; small changes in quality or cost could reverse the result."
    else:
        interp="Raw output may have risen, but quality and/or intervention cost offset the productivity gain."
        rec="Do not scale yet. Redesign the incentive or AI workflow and measure quality-adjusted productivity."
    return {
        "base_effective":base_effective,"effective_output":new_effective,
        "new_output":new_output,"base_cost_per_effective":base_cpu,
        "new_cost_per_effective":new_cpu,"cost_improvement_pct":improvement,
        "interpretation":interp,"recommendation":rec
    }

def customer_choice_model(customers,baseline_conv,uplift_pp,contrib,intervention_cost_total):
    base_rate=max(0,min(1,baseline_conv/100))
    new_rate=max(0,min(1,(baseline_conv+uplift_pp)/100))
    base_conv=customers*base_rate
    new_conv=customers*new_rate
    incr=new_conv-base_conv
    incr_contrib=incr*contrib
    net=incr_contrib-intervention_cost_total
    if net>0:
        interp="The behavioural intervention raises expected contribution by more than its implementation cost."
        rec="Pilot at scale while monitoring cancellations, complaints and long-run customer value."
    else:
        interp="The conversion uplift is not large enough to cover the intervention cost under current assumptions."
        rec="Redesign the intervention, target a higher-value segment, or stop."
    return {
        "base_conversions":base_conv,"new_conversions":new_conv,
        "incremental_contribution":incr_contrib,"net_incremental_profit":net,
        "interpretation":interp,"recommendation":rec
    }

def experiment_model(n_control,n_treat,conv_control,conv_treat,value_per_success,treatment_cost_per_person):
    pc=max(0,min(1,conv_control/100))
    pt=max(0,min(1,conv_treat/100))
    effect=pt-pc
    se=sqrt(pc*(1-pc)/n_control + pt*(1-pt)/n_treat) if n_control and n_treat else float("inf")
    z=effect/se if se>0 else 0
    value_per_treated=effect*value_per_success-treatment_cost_per_person
    if value_per_treated>0 and abs(z)>=1.96:
        decision="Scale"
        interp="The treatment is economically positive and the observed difference is reasonably precise in this simple two-group test."
        rec="Scale cautiously while monitoring external validity and whether the effect persists outside the pilot."
    elif value_per_treated>0:
        decision="Retest"
        interp="The estimated effect is economically positive, but the evidence is still uncertain."
        rec="Run a larger or better-powered experiment before scaling."
    else:
        decision="Stop / Redesign"
        interp="The estimated incremental value does not cover the treatment cost."
        rec="Stop or redesign the intervention unless there is another strategic benefit not captured here."
    return {
        "effect_pp":effect*100,"z":z,"value_per_treated":value_per_treated,
        "decision":decision,"interpretation":interp,"recommendation":rec
    }


def break_even_quantity(fixed_cost, contribution_per_unit):
    if contribution_per_unit <= 0:
        return {"break_even_units": float("inf")}
    return {"break_even_units": fixed_cost / contribution_per_unit}

def channel_economics(retail_price, direct_variable_cost, retailer_share, wholesale_cost):
    direct_contribution = retail_price - direct_variable_cost
    northstar_retail_revenue = retail_price * (1 - retailer_share/100)
    retail_contribution = northstar_retail_revenue - wholesale_cost
    return {
        "direct_contribution": direct_contribution,
        "northstar_retail_revenue": northstar_retail_revenue,
        "retail_contribution": retail_contribution
    }
