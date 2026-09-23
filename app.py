import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from models import (
    demand_quantity, supply_quantity, equilibrium,
    point_elasticity, pricing_scenarios,
    game_expected_payoffs, adverse_selection,
    moral_hazard, signalling_model,
    trade_advantage, exchange_rate_profit,
    apply_ai_productivity,
    policy_lookup, interpret_policy_text,
    price_control,
    incentive_productivity_model,
    customer_choice_model,
    experiment_model,
    break_even_quantity, channel_economics,
)

BEEDIE_RED = "#A6192E"

st.set_page_config(page_title="NorthStar Economics Dashboard", page_icon="📈", layout="wide")

st.markdown(f"""
<style>
.stApp {{background-color:#F7F8FA;}}
.block-container {{padding-top:1.3rem;padding-bottom:2rem;max-width:1500px;}}
.northstar-title {{font-size:2.15rem;font-weight:800;margin-bottom:.15rem;color:#20242A;}}
.northstar-subtitle {{color:#6B7280;margin-bottom:1.1rem;}}
.module-banner {{background:white;border-left:5px solid {BEEDIE_RED};border-radius:10px;padding:.8rem 1rem;margin-bottom:1rem;box-shadow:0 1px 2px rgba(0,0,0,.04);}}
.decision-box {{background:white;border:1px solid #E5E7EB;border-radius:10px;padding:.9rem 1rem;min-height:118px;}}
.decision-label {{color:{BEEDIE_RED};font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.02em;margin-bottom:.25rem;}}
.small-note {{color:#6B7280;font-size:.86rem;}}
div[data-testid="stMetric"] {{background:white;border:1px solid #E5E7EB;padding:.8rem;border-radius:10px;}}
</style>
""", unsafe_allow_html=True)

def banner(module,title,question):
    st.markdown(f'''<div class="module-banner"><div style="color:{BEEDIE_RED};font-weight:800;font-size:.78rem;">{module}</div><div style="font-weight:800;font-size:1.3rem;">{title}</div><div style="color:#6B7280;margin-top:.2rem;">{question}</div></div>''', unsafe_allow_html=True)

def decision_strip(result,interpretation,recommendation):
    c1,c2,c3=st.columns(3)
    for col,label,text in [(c1,"Economic result",result),(c2,"Interpretation",interpretation),(c3,"Managerial recommendation",recommendation)]:
        with col:
            st.markdown(f'<div class="decision-box"><div class="decision-label">{label}</div>{text}</div>',unsafe_allow_html=True)

def plot_demand_supply(a_d,b_d,a_s,b_s,price_marker=None,control_price=None):
    eq=equilibrium(a_d,b_d,a_s,b_s)
    prices=np.linspace(0,max(1400,eq["price"]*1.6),220)
    qd=np.maximum(0,a_d-b_d*prices)
    qs=np.maximum(0,a_s+b_s*prices)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=qd,y=prices,mode="lines",name="Demand"))
    fig.add_trace(go.Scatter(x=qs,y=prices,mode="lines",name="Supply"))
    fig.add_trace(go.Scatter(x=[eq["quantity"]],y=[eq["price"]],mode="markers+text",text=[f"Equilibrium<br>P={eq['price']:.0f}, Q={eq['quantity']:.0f}"],textposition="top right",marker=dict(size=10),name="Equilibrium"))
    if price_marker is not None:
        qdm=max(0,demand_quantity(price_marker,a_d,b_d)); qsm=max(0,supply_quantity(price_marker,a_s,b_s))
        fig.add_trace(go.Scatter(x=[qdm,qsm],y=[price_marker,price_marker],mode="markers",name="At selected price"))
    if control_price is not None:
        fig.add_hline(y=control_price,line_dash="dash",annotation_text=f"Policy price = {control_price:.0f}")
    fig.update_layout(height=430,margin=dict(l=20,r=20,t=35,b=20),xaxis_title="Quantity",yaxis_title="Price (CAD)",legend_orientation="h",legend_y=1.08)
    return fig

st.markdown('<div class="northstar-title">NorthStar Economics Dashboard</div>',unsafe_allow_html=True)
st.markdown('<div class="northstar-subtitle">A live managerial-economics laboratory: <b>Input → Model → Interpretation → Decision</b></div>',unsafe_allow_html=True)

home,m1,m2,m3,m4,m5=st.tabs(["Course Demo","Module 1","Module 2","Module 3","Module 4","Module 5"])

with home:
    st.subheader("How the prototype works")
    st.write("Each module contains a small number of transparent economic models. Students change assumptions, observe results, explain the economics, and use the evidence to update one continuing recommendation for NorthStar.")
    st.markdown("""### Master NorthStar baseline
**Current selling price:** CAD 900  |  **Demand:** Qd = 26,000 - 20P  |  **Marginal cost:** CAD 480  
**Imported component:** USD 100  |  **CAD/USD:** 1.30  |  **Other variable cost:** CAD 350  
At the baseline price, predicted quantity is **8,000 units**, contribution is **CAD 420 per unit**, and total operating contribution is **CAD 3.36 million**.

**Decision Lab method:** Predict → Experiment → Observe → Explain → Decide → Reconsider.
""")
    cols=st.columns(5)
    cards=[
        ("M1","Markets & Pricing","Demand, supply, equilibrium, elasticity."),
        ("M2","Strategy & Information","Games, adverse selection, moral hazard, signalling."),
        ("M3","Trade & Sourcing","Comparative advantage, FX, AI productivity."),
        ("M4","Policy & Risk","Economic signals, policy responses, price controls."),
        ("M5","Internal Levers","Incentives, customer choice, experiments."),
    ]
    for col,(num,title,desc) in zip(cols,cards):
        with col:
            st.markdown(f'<div class="decision-box"><div class="decision-label">{num}</div><b>{title}</b><br><span class="small-note">{desc}</span></div>',unsafe_allow_html=True)
    st.info("")

with m1:
    banner("MODULE 1","Customers, Costs, Pricing & Productivity","What should NorthStar produce, how much, and at what price?")
    st.caption("Baseline equations: Qd = 26,000 − 20P and Qs = −6,000 + 20P.")
    t1,t2,t3,t4=st.tabs(["Demand & Supply","Movement vs Shift","Elasticity & Pricing","Break-Even & Channels"])
    with t1:
        c1,c2=st.columns([.9,1.5])
        with c1:
            demand_shift=st.slider("Demand intercept shift",-8000,8000,0,500,key="m1_dshift")
            supply_shift=st.slider("Supply intercept shift",-8000,8000,0,500,key="m1_sshift")
            a_d=26000+demand_shift; a_s=-6000+supply_shift
            eq=equilibrium(a_d,20,a_s,20)
            st.metric("Equilibrium price",f"CAD {eq['price']:,.0f}")
            st.metric("Equilibrium quantity",f"{eq['quantity']:,.0f}")
        with c2:
            st.plotly_chart(plot_demand_supply(a_d,20,a_s,20),use_container_width=True)
        decision_strip(f"P* = CAD {eq['price']:,.0f}; Q* = {eq['quantity']:,.0f}",f"The current demand and supply curves intersect at approximately CAD {eq['price']:,.0f} and {eq['quantity']:,.0f} units.","Use the equilibrium as a market benchmark, then layer in NorthStar's costs, competitive position and channel strategy before choosing an actual price.")
    with t2:
        left,right=st.columns([.9,1.5])
        with left:
            selected_price=st.slider("NorthStar market price (movement along curves)",350,1200,800,25,key="m1_move_price")
            demand_shift2=st.slider("Demand shift",-6000,6000,0,500,key="m1_move_d")
            supply_shift2=st.slider("Supply shift",-6000,6000,0,500,key="m1_move_s")
            a_d2=26000+demand_shift2; a_s2=-6000+supply_shift2
            qd_now=demand_quantity(selected_price,a_d2,20); qs_now=supply_quantity(selected_price,a_s2,20)
            st.metric("Quantity demanded at selected price",f"{qd_now:,.0f}")
            st.metric("Quantity supplied at selected price",f"{qs_now:,.0f}")
        with right:
            st.plotly_chart(plot_demand_supply(a_d2,20,a_s2,20,price_marker=selected_price),use_container_width=True)
        st.markdown("**Movement:** change the price while holding the curve fixed. **Shift:** change the demand/supply intercept to represent a change in income, tastes, costs, technology, capacity, etc.")
    with t3:
        c1,c2=st.columns([.9,1.4])
        with c1:
            price=st.slider("Current NorthStar price (CAD)",450,1100,900,10,key="m1_price")
            marginal_cost=st.slider("Variable / marginal cost per unit (CAD)",200,700,480,10,key="m1_mc")
            a_d3=st.slider("Demand intercept",18000,34000,26000,1000,key="m1_a_d")
            elasticity=point_elasticity(price,a_d3,20)
            scenarios=pricing_scenarios(price,marginal_cost,a_d3,20)
            st.metric("Point elasticity",f"{elasticity:.2f}")
            st.metric("Current predicted quantity",f"{max(0,demand_quantity(price,a_d3,20)):,.0f}")
        with c2:
            df=pd.DataFrame(scenarios)
            st.dataframe(df.rename(columns={"label":"Scenario","price":"Price","quantity":"Quantity","revenue":"Revenue","unit_margin":"Unit margin","total_contribution":"Total contribution"}).style.format({"Price":"CAD {:,.0f}","Quantity":"{:,.0f}","Revenue":"CAD {:,.0f}","Unit margin":"CAD {:,.0f}","Total contribution":"CAD {:,.0f}"}),use_container_width=True,hide_index=True)
        best=max(scenarios,key=lambda x:x["total_contribution"])
        elas_msg="Demand is locally inelastic: quantity is relatively less responsive to price." if abs(elasticity)<1 else "Demand is locally elastic: quantity is relatively responsive to price." if abs(elasticity)>1 else "Demand is approximately unit elastic at this point."
        decision_strip(f"ε = {elasticity:.2f}",elas_msg,f"Among the simple ±5% scenarios, the highest predicted total contribution is <b>{best['label']}</b> at about CAD {best['price']:,.0f}. Treat this as a decision aid, not a complete pricing rule.")

    with t4:
        st.subheader("Break-even, channel choice, and scale")
        st.caption("Contribution per unit matters, but so does quantity. Use these tools to compare investment thresholds, direct versus retail economics, and the scale required for AI to pay for itself.")

        be_tab, pricecut_tab, channel_tab, ai_be_tab = st.tabs(["Investment Break-Even","Price-Cut Break-Even","Direct vs Retail","AI Investment"])

        with be_tab:
            c1,c2=st.columns([1,1.3])
            with c1:
                fixed_investment=st.slider("Fixed campaign / investment cost (CAD)",100000,3000000,1200000,50000,key="m1_be_fixed")
                contribution_incremental=st.slider("Contribution per incremental unit (CAD)",50,600,300,10,key="m1_be_cm")
                expected_incremental_units=st.slider("Expected incremental units",0,30000,5000,500,key="m1_be_units")
                be=break_even_quantity(fixed_investment,contribution_incremental)
                expected_contribution=expected_incremental_units*contribution_incremental
                net_value=expected_contribution-fixed_investment
            with c2:
                st.latex(r"Q_{BE}=\frac{F}{P-VC}")
                st.metric("Break-even quantity",f"{be['break_even_units']:,.0f} units")
                st.metric("Expected contribution",f"CAD {expected_contribution:,.0f}")
                st.metric("Contribution after fixed investment",f"CAD {net_value:,.0f}")
            status="Above break-even" if expected_incremental_units>=be["break_even_units"] else "Below break-even"
            decision_strip(status,
                f"NorthStar needs about {be['break_even_units']:,.0f} incremental units to recover the fixed investment.",
                "Use break-even as a threshold, then ask how credible the required volume is and what uncertainty or opportunity cost remains.")

        with pricecut_tab:
            st.subheader("Patricia's 5% price-cut test")
            st.caption("Does the additional volume generated by a lower price compensate for the contribution margin given up on each unit?")
            c1,c2=st.columns([1,1.35])
            with c1:
                pc_current_price=st.slider("Current price (CAD)",600,1200,900,10,key="m1_pc_price")
                pc_cut_pct=st.slider("Proposed price cut (%)",1,20,5,1,key="m1_pc_cut")
                pc_mc=st.slider("Variable / marginal cost per unit (CAD)",200,700,480,10,key="m1_pc_mc")
                pc_a_d=st.slider("Demand intercept",18000,34000,26000,1000,key="m1_pc_ad")
                pc_b_d=20
                pc_new_price=pc_current_price*(1-pc_cut_pct/100)
                pc_q0=max(0,demand_quantity(pc_current_price,pc_a_d,pc_b_d))
                pc_q1=max(0,demand_quantity(pc_new_price,pc_a_d,pc_b_d))
                pc_cm0=pc_current_price-pc_mc
                pc_cm1=pc_new_price-pc_mc
                pc_base_contribution=pc_q0*pc_cm0
                pc_new_contribution=pc_q1*pc_cm1
                pc_be_q=(pc_base_contribution/pc_cm1) if pc_cm1>0 else float("inf")
                pc_required_growth=((pc_be_q/pc_q0)-1)*100 if pc_q0>0 else float("inf")
                pc_predicted_growth=((pc_q1/pc_q0)-1)*100 if pc_q0>0 else float("inf")
                pc_gap=pc_be_q-pc_q1
            with c2:
                pc_df=pd.DataFrame([
                    ["Current",pc_current_price,pc_q0,pc_cm0,pc_base_contribution],
                    [f"After {pc_cut_pct}% cut",pc_new_price,pc_q1,pc_cm1,pc_new_contribution]
                ],columns=["Scenario","Price","Predicted quantity","Contribution / unit","Total contribution"])
                st.dataframe(pc_df.style.format({
                    "Price":"CAD {:,.0f}",
                    "Predicted quantity":"{:,.0f}",
                    "Contribution / unit":"CAD {:,.0f}",
                    "Total contribution":"CAD {:,.0f}"
                }),use_container_width=True,hide_index=True)
                m1,m2,m3=st.columns(3)
                m1.metric("Break-even quantity",f"{pc_be_q:,.0f}")
                m2.metric("Predicted quantity",f"{pc_q1:,.0f}")
                m3.metric("Gap to break-even",f"{abs(pc_gap):,.0f} units",delta=("above" if pc_gap<=0 else "short"))
                m4,m5=st.columns(2)
                m4.metric("Required volume increase",f"{pc_required_growth:.2f}%")
                m5.metric("Predicted volume increase",f"{pc_predicted_growth:.2f}%")
            if pc_gap>0:
                pc_result=f"Price cut falls {pc_gap:,.0f} units short of contribution break-even"
                pc_interp=f"NorthStar needs about {pc_be_q:,.0f} units at CAD {pc_new_price:,.0f} to preserve baseline contribution, but the demand model predicts {pc_q1:,.0f}."
                pc_rec="The cut narrowly fails under the current assumptions. Treat the gap as a flip condition: a slightly stronger demand response could reverse the recommendation."
            else:
                pc_result=f"Price cut exceeds contribution break-even by {-pc_gap:,.0f} units"
                pc_interp=f"The demand model predicts {pc_q1:,.0f} units versus about {pc_be_q:,.0f} needed to preserve baseline contribution."
                pc_rec="The modeled price cut passes the contribution test. Still stress-test demand, capacity, competitor response and implementation risk before treating it as a final pricing rule."
            decision_strip(pc_result,pc_interp,pc_rec)

        with channel_tab:
            c1,c2=st.columns([1,1.3])
            with c1:
                retail_price=st.slider("Customer retail price (CAD)",600,1400,899,10,key="m1_ch_price")
                direct_vc=st.slider("Direct-channel variable cost (CAD)",250,700,479,10,key="m1_ch_direct_vc")
                retailer_share=st.slider("Retailer share of retail price (%)",0,50,25,1,key="m1_ch_share")
                wholesale_cost=st.slider("NorthStar cost per retail-channel unit (CAD)",250,700,430,10,key="m1_ch_wholesale")
                direct_units=st.slider("Expected direct-channel units",0,30000,8000,500,key="m1_ch_direct_units")
                retail_units=st.slider("Expected retail-channel units",0,50000,15000,500,key="m1_ch_retail_units")
                ch=channel_economics(retail_price,direct_vc,retailer_share,wholesale_cost)
                direct_total=ch["direct_contribution"]*direct_units
                retail_total=ch["retail_contribution"]*retail_units
            with c2:
                df=pd.DataFrame([
                    ["Direct",direct_units,ch["direct_contribution"],direct_total],
                    ["Retail",retail_units,ch["retail_contribution"],retail_total]
                ],columns=["Channel","Expected units","Contribution / unit","Total contribution"])
                st.dataframe(df.style.format({
                    "Expected units":"{:,.0f}",
                    "Contribution / unit":"CAD {:,.2f}",
                    "Total contribution":"CAD {:,.0f}"
                }),use_container_width=True,hide_index=True)
                st.metric("Direct contribution / unit",f"CAD {ch['direct_contribution']:,.2f}")
                st.metric("Retail contribution / unit",f"CAD {ch['retail_contribution']:,.2f}")
                ratio=(ch["direct_contribution"]/ch["retail_contribution"]) if ch["retail_contribution"]>0 else float("inf")
                st.metric("Retail units needed per direct sale",f"{ratio:.2f}×")
            preferred="Direct" if direct_total>=retail_total else "Retail"
            decision_strip(
                f"Higher modeled total contribution: {preferred}",
                "Direct can have the higher unit contribution while retail can still create more total contribution if it generates enough additional volume.",
                "Do not choose a channel from unit margin alone. Compare volume, capacity, reach, customer acquisition, service and total contribution.")

        with ai_be_tab:
            c1,c2=st.columns([1,1.3])
            with c1:
                ai_fixed=st.slider("Annual AI system cost (CAD)",100000,2000000,600000,50000,key="m1_ai_fixed")
                saving_per_unit=st.slider("Variable-cost saving per appliance (CAD)",5,150,40,5,key="m1_ai_save")
                expected_volume=st.slider("Expected annual appliance volume",1000,50000,15000,1000,key="m1_ai_volume")
                ai_be=break_even_quantity(ai_fixed,saving_per_unit)
                annual_savings=expected_volume*saving_per_unit
                ai_net=annual_savings-ai_fixed
            with c2:
                st.latex(r"Q_{BE}^{AI}=\frac{AI\ Fixed\ Cost}{Variable\ Cost\ Saving\ per\ Unit}")
                st.metric("AI break-even volume",f"{ai_be['break_even_units']:,.0f} units")
                st.metric("Savings at expected volume",f"CAD {annual_savings:,.0f}")
                st.metric("Net annual benefit",f"CAD {ai_net:,.0f}")
            decision_strip(
                f"Break-even = {ai_be['break_even_units']:,.0f} units",
                "AI raises fixed cost but can lower marginal cost, so its economics improve as the saving is spread over more units.",
                "Treat the threshold as a screening device. Ask whether the per-unit saving is credible and whether implementation, quality and opportunity costs change the decision.")

with m2:
    banner("MODULE 2","Competition, Strategy & Information","How should NorthStar act when others respond strategically or know something we do not?")
    gt,adv,mh,sig=st.tabs(["Game Theory","Adverse Selection","Moral Hazard","Signalling"])
    with gt:
        st.write("NorthStar chooses **Maintain** or **Discount**. NovaHome can do the same. Payoffs are annual operating contribution in CAD millions under the calibrated NorthStar case.")
        c1,c2=st.columns([1,1])
        with c1:
            p_rival_discount=st.slider("Probability NovaHome discounts",0.0,1.0,0.50,0.05)
            payoff_MM=st.number_input("NorthStar payoff: Maintain / Rival Maintain",value=3.36)
            payoff_MD=st.number_input("NorthStar payoff: Maintain / Rival Discount",value=2.10)
            payoff_DM=st.number_input("NorthStar payoff: Discount / Rival Maintain",value=3.90)
            payoff_DD=st.number_input("NorthStar payoff: Discount / Rival Discount",value=1.80)
            result=game_expected_payoffs(p_rival_discount,payoff_MM,payoff_MD,payoff_DM,payoff_DD)
        with c2:
            table=pd.DataFrame([[f"{payoff_MM:.1f}",f"{payoff_MD:.1f}"],[f"{payoff_DM:.1f}",f"{payoff_DD:.1f}"]],index=["NorthStar: Maintain","NorthStar: Discount"],columns=["NovaHome: Maintain","NovaHome: Discount"])
            st.dataframe(table,use_container_width=True)
            st.metric("Expected payoff — Maintain",f"CAD {result['maintain']:.2f}m")
            st.metric("Expected payoff — Discount",f"CAD {result['discount']:.2f}m")
        decision_strip(f"Best expected action: {result['best_action']}","The best action depends on what NorthStar believes NovaHome is likely to do.",f"Choose <b>{result['best_action']}</b> under the current probability and payoff assumptions; revisit if beliefs about NovaHome change.")
    with adv:
        st.write("A supplier can be high quality or low quality, but NorthStar does not directly observe type before contracting.")
        c1,c2=st.columns([1,1])
        with c1:
            p_good=st.slider("Probability supplier is high quality",0.0,1.0,0.55,0.05)
            value_good=st.slider("Value if high quality",50,200,140,5)
            value_bad=st.slider("Value if low quality",0,120,45,5)
            contract_price=st.slider("Contract price",20,160,90,5)
            screening_cost=st.slider("Cost of screening",0,40,8,1)
            screened_p_good=st.slider("Probability high quality after screening",p_good,1.0,min(0.9,max(p_good,0.8)),0.05)
            res=adverse_selection(p_good,value_good,value_bad,contract_price,screening_cost,screened_p_good)
        with c2:
            st.latex(r"E[V\mid no\ screening]=pV_H+(1-p)V_L-P")
            st.latex(r"E[V\mid screening]=\tilde pV_H+(1-\tilde p)V_L-P-C_s")
            st.metric("Expected net value — no screening",f"{res['no_screen']:.1f}")
            st.metric("Expected net value — screen first",f"{res['screen']:.1f}")
        decision_strip(f"Preferred approach: {res['best_action']}","Adverse selection matters because the mix of hidden supplier types changes expected value before the contract is signed.",res["recommendation"])
    with mh:
        st.write("NorthStar cannot perfectly observe employee effort after contracting.")
        c1,c2=st.columns([1,1])
        with c1:
            base_wage=st.slider("Fixed wage / task bundle",20,120,60,5)
            bonus=st.slider("Bonus if successful",0,120,35,5)
            p_low=st.slider("Success probability — low effort",0.10,0.90,0.50,0.05)
            p_high=st.slider("Success probability — high effort",p_low,1.00,min(0.85,max(p_low+0.1,0.75)),0.05)
            effort_cost=st.slider("Employee cost of high effort",0,80,20,5)
            firm_value=st.slider("Firm value if successful",50,300,160,10)
            res=moral_hazard(base_wage,bonus,p_low,p_high,effort_cost,firm_value)
        with c2:
            st.latex(r"U_L=w+b\,p_L")
            st.latex(r"U_H=w+b\,p_H-c_H")
            st.latex(r"\Pi=V\,p(e)-w-b\,p(e)")
            st.metric("Employee utility — low effort",f"{res['u_low']:.1f}")
            st.metric("Employee utility — high effort",f"{res['u_high']:.1f}")
            st.metric("Firm expected profit",f"{res['firm_profit']:.1f}")
        decision_strip(f"Employee chooses: {res['effort_choice']}","A performance bonus changes the employee's private return to effort, but too large a bonus can also become expensive for the firm.",res["recommendation"])
    with sig:
        st.write("A costly signal can separate high-quality from low-quality suppliers only if the signal is worthwhile for one type but not the other.")
        c1,c2=st.columns([1,1])
        with c1:
            contract_benefit=st.slider("Benefit from winning NorthStar contract",20,150,80,5)
            signal_cost_high=st.slider("Signal cost — high-quality supplier",0,100,20,5)
            signal_cost_low=st.slider("Signal cost — low-quality supplier",0,120,70,5)
            outside_high=st.slider("Outside option — high quality",0,100,35,5)
            outside_low=st.slider("Outside option — low quality",0,100,30,5)
            res=signalling_model(contract_benefit,signal_cost_high,signal_cost_low,outside_high,outside_low)
        with c2:
            st.latex(r"Signal\ if:\ B-C_{signal} > Outside\ Option")
            st.metric("High-quality net payoff from signalling",f"{res['high_signal_payoff']:.1f}")
            st.metric("Low-quality net payoff from signalling",f"{res['low_signal_payoff']:.1f}")
        decision_strip(f"Separating signal: {'Yes' if res['separating'] else 'No'}",res["interpretation"],res["recommendation"])

with m3:
    banner("MODULE 3","Global Markets, Trade & Sourcing","How should NorthStar choose where to source when productivity, costs, currencies and technology differ?")
    trade_tab,fx_tab,ai_tab=st.tabs(["Absolute & Comparative Advantage","Exchange Rate Exposure","AI Changes the Trade-off"])
    with trade_tab:
        st.write("Outputs are units per day. Baseline: Canada 12 boards / 24 sensors; Mexico 8 boards / 10 sensors.")
        c1,c2=st.columns([1,1.3])
        with c1:
            ca_boards=st.slider("Canada — boards/day",1.0,40.0,12.0,1.0)
            ca_sensors=st.slider("Canada — sensors/day",1.0,50.0,24.0,1.0)
            mx_boards=st.slider("Mexico — boards/day",1.0,40.0,8.0,1.0)
            mx_sensors=st.slider("Mexico — sensors/day",1.0,50.0,10.0,1.0)
            res=trade_advantage(ca_boards,ca_sensors,mx_boards,mx_sensors,"Canada","Mexico")
        with c2:
            df=pd.DataFrame([["Canada",ca_boards,ca_sensors,res["oc_board_a"],res["oc_sensor_a"]],["Mexico",mx_boards,mx_sensors,res["oc_board_b"],res["oc_sensor_b"]]],columns=["Location","Boards/day","Sensors/day","OC of 1 board (sensors)","OC of 1 sensor (boards)"])
            st.dataframe(df.style.format({"Boards/day":"{:.1f}","Sensors/day":"{:.1f}","OC of 1 board (sensors)":"{:.2f}","OC of 1 sensor (boards)":"{:.2f}"}),use_container_width=True,hide_index=True)
            st.write(f"**Absolute advantage — boards:** {res['absolute_board']}")
            st.write(f"**Absolute advantage — sensors:** {res['absolute_sensor']}")
            st.write(f"**Comparative advantage — boards:** {res['comparative_board']}")
            st.write(f"**Comparative advantage — sensors:** {res['comparative_sensor']}")
        decision_strip(f"{res['comparative_board']} → boards; {res['comparative_sensor']} → sensors","Comparative advantage is determined by opportunity cost, not simply by who can produce more of everything.",res["recommendation"])
    with fx_tab:
        c1,c2=st.columns([1,1.3])
        with c1:
            usd_component=st.slider("Imported component price (USD)",40,250,100,5)
            fx_rate=st.slider("CAD per USD",0.90,1.80,1.30,0.01)
            other_cost=st.slider("Other CAD variable cost per appliance",100,700,350,10)
            sale_price=st.slider("NorthStar selling price (CAD)",500,1400,900,10)
            units=st.slider("Units sold",1000,30000,8000,1000)
            res=exchange_rate_profit(usd_component,fx_rate,other_cost,sale_price,units)
        with c2:
            st.latex(r"Imported\ Cost_{CAD}=Price_{USD}\times (CAD/USD)")
            st.latex(r"Profit/unit=P-(Imported\ Cost_{CAD}+Other\ Cost)")
            st.metric("Imported cost / unit",f"CAD {res['imported_cost_cad']:,.0f}")
            st.metric("Profit / unit",f"CAD {res['profit_per_unit']:,.0f}")
            st.metric("Total operating contribution",f"CAD {res['total_profit']:,.0f}")
            st.metric("Margin",f"{res['margin_pct']:.1f}%")
        decision_strip(f"Margin = {res['margin_pct']:.1f}%","A weaker CAD raises the domestic-currency cost of USD-priced inputs when the USD supplier price is unchanged.",res["recommendation"])
    with ai_tab:
        st.write("Use AI/automation as a productivity shock, then recalculate absolute and comparative advantage.")
        c1,c2=st.columns([1,1.3])
        with c1:
            canada_ai_boards=st.slider("Canada AI boost — boards (%)",0,200,0,10)
            canada_ai_sensors=st.slider("Canada AI boost — sensors (%)",0,200,0,10)
            mexico_ai_boards=st.slider("Mexico AI boost — boards (%)",0,200,0,10)
            mexico_ai_sensors=st.slider("Mexico AI boost — sensors (%)",0,200,0,10)
            base=dict(a_board=12,a_sensor=24,b_board=8,b_sensor=10)
            new=apply_ai_productivity(**base,a_board_boost=canada_ai_boards,a_sensor_boost=canada_ai_sensors,b_board_boost=mexico_ai_boards,b_sensor_boost=mexico_ai_sensors)
            res=trade_advantage(new["a_board"],new["a_sensor"],new["b_board"],new["b_sensor"],"Canada","Mexico")
        with c2:
            df=pd.DataFrame([["Canada",12,24,new["a_board"],new["a_sensor"]],["Mexico",8,10,new["b_board"],new["b_sensor"]]],columns=["Location","Boards before","Sensors before","Boards after AI","Sensors after AI"])
            st.dataframe(df.style.format({c:"{:.1f}" for c in df.columns if c!="Location"}),use_container_width=True,hide_index=True)
            st.write(f"**After AI — comparative advantage in boards:** {res['comparative_board']}")
            st.write(f"**After AI — comparative advantage in sensors:** {res['comparative_sensor']}")
        decision_strip(f"Post-AI allocation: {res['comparative_board']} → boards; {res['comparative_sensor']} → sensors","Technology can change productivity unevenly across locations and activities, which can change opportunity costs.","Recalculate the sourcing/production allocation after a material technology shock rather than assuming the old comparative advantage still holds.")

with m4:
    banner("MODULE 4","Reading the Economy, Anticipating Policy & Managing Risk","How can managers read economic signals, anticipate policy responses, and prepare NorthStar?")
    policy_tab,control_tab=st.tabs(["Economic Signal → Policy → Business","Price Ceiling / Floor"])
    with policy_tab:
        st.subheader("NorthStar economic outlook")
        outlook=st.selectbox("Stress-test scenario",["Baseline","Demand slowdown","CAD depreciation","Inflation + weak CAD","Domestic-production support"])
        outlook_map={
            "Baseline":"Demand and costs remain near the master assumptions; CAD/USD = 1.30.",
            "Demand slowdown":"Household durable-goods demand weakens. Test a negative demand-intercept shift in Module 1.",
            "CAD depreciation":"CAD/USD rises from 1.30 toward 1.45. Revisit imported cost and margin in Module 3.",
            "Inflation + weak CAD":"Demand softens while imported and domestic costs rise. Stress-test both demand and cost assumptions.",
            "Domestic-production support":"Industrial policy lowers the effective cost of domestic capacity. Revisit Module 3 sourcing and AI-productivity choices."}
        st.info(outlook_map[outlook])
        st.subheader("Structured signal")
        signal=st.selectbox("Choose an economic signal or pressure",["High inflation","Weak growth or unemployment","Fiscal deficit or revenue shortfall","Currency depreciation or falling reserves","Affordability pressure","Strategic-industry concerns","Environmental objectives"])
        p=policy_lookup(signal)
        c1,c2,c3=st.columns(3)
        c1.info(f"**Policymaker objective**\n\n{p['objective']}")
        c2.info(f"**Possible policy response**\n\n{p['response']}")
        c3.info(f"**Possible NorthStar implication**\n\n{p['business']}")
        st.divider(); st.subheader("Plain-English signal")
        text_signal=st.text_area("Enter a signal or pressure",placeholder="Example: Inflation is rising quickly and the currency is weakening.")
        if st.button("Interpret text signal",type="primary"):
            parsed=interpret_policy_text(text_signal)
            if parsed["matches"]:
                for item in parsed["matches"]:
                    with st.expander(item["signal"],expanded=True):
                        st.write(f"**Objective:** {item['objective']}")
                        st.write(f"**Possible response:** {item['response']}")
                        st.write(f"**Business implication:** {item['business']}")
            else:
                st.warning("No prototype rule matched that sentence yet. Choose the closest structured signal above or add the wording to the model map later.")
        decision_strip(p["objective"],"The same economic signal can support several policy responses. The dashboard shows a plausible policy menu rather than pretending to forecast one certain action.","Identify NorthStar's exposure and prepare contingent actions before the policy is announced.")
    with control_tab:
        c1,c2=st.columns([.9,1.5])
        with c1:
            policy_type=st.radio("Policy",["Price ceiling","Price floor"],horizontal=True)
            default_policy_price=600 if policy_type=="Price ceiling" else 1000
            policy_price=st.slider("Controlled price (CAD)",300,1300,default_policy_price,25,key=f"policy_price_{policy_type}")
            d_shift=st.slider("Demand shift",-4000,4000,0,500,key="m4_ds")
            s_shift=st.slider("Supply shift",-4000,4000,0,500,key="m4_ss")
            a_d=26000+d_shift; a_s=-6000+s_shift
            res=price_control(a_d,20,a_s,20,policy_type,policy_price)
            st.metric("Market equilibrium price",f"CAD {res['equilibrium_price']:,.0f}")
            st.metric("Quantity demanded at policy price",f"{res['qd']:,.0f}")
            st.metric("Quantity supplied at policy price",f"{res['qs']:,.0f}")
            if res["shortage"]>0: st.metric("Shortage",f"{res['shortage']:,.0f}")
            elif res["surplus"]>0: st.metric("Surplus",f"{res['surplus']:,.0f}")
        with c2:
            st.plotly_chart(plot_demand_supply(a_d,20,a_s,20,control_price=policy_price),use_container_width=True)
        decision_strip(res["result_label"],res["interpretation"],res["recommendation"])

with m5:
    banner("MODULE 5","Internal Levers, Behaviour & Evidence","How can managers improve productivity, customer outcomes and margins using levers within their control—and know what actually worked?")
    inc_tab,choice_tab,exp_tab=st.tabs(["Incentives & Quality","Customer Choice","Experiment: Scale / Retest / Stop"])
    with inc_tab:
        c1,c2=st.columns([1,1.3])
        with c1:
            base_output=st.slider("Baseline tasks completed",20,200,80,5)
            base_error=st.slider("Baseline error rate (%)",0.0,30.0,5.0,1.0)
            productivity_gain=st.slider("Output gain from incentive / AI (%)",0,80,20,5)
            error_change=st.slider("Change in error rate (percentage points)",-10.0,30.0,5.0,1.0)
            labor_cost=st.slider("Labour / system cost (CAD)",200,3000,1000,50)
            intervention_cost=st.slider("Incremental intervention cost (CAD)",0,1000,150,25)
            res=incentive_productivity_model(base_output,base_error,productivity_gain,error_change,labor_cost,intervention_cost)
        with c2:
            st.latex(r"Effective\ Output = Raw\ Output\times(1-Error\ Rate)")
            st.latex(r"Cost\ per\ Effective\ Unit=\frac{Labour+Intervention\ Cost}{Effective\ Output}")
            st.metric("Raw output after intervention",f"{res['new_output']:,.1f}")
            st.metric("Quality-adjusted output",f"{res['effective_output']:,.1f}")
            st.metric("Cost / effective unit",f"CAD {res['new_cost_per_effective']:.2f}")
            st.metric("Improvement vs baseline",f"{res['cost_improvement_pct']:.1f}%")
        decision_strip(f"Cost/effective unit = CAD {res['new_cost_per_effective']:.2f}",res["interpretation"],res["recommendation"])
    with choice_tab:
        c1,c2=st.columns([1,1.3])
        with c1:
            customers=st.slider("Customers exposed",100,20000,5000,100)
            baseline_conv=st.slider("Baseline conversion (%)",0.0,80.0,20.0,1.0)
            uplift_pp=st.slider("Default / framing uplift (percentage points)",-20.0,40.0,8.0,1.0)
            contrib=st.slider("Contribution per conversion (CAD)",10,500,420,10)
            intervention_cost_total=st.slider("Total intervention cost (CAD)",0,100000,5000,500)
            res=customer_choice_model(customers,baseline_conv,uplift_pp,contrib,intervention_cost_total)
        with c2:
            st.latex(r"Incremental\ Profit=(\Delta Conversion\times Customers\times Contribution)-Intervention\ Cost")
            st.metric("Baseline conversions",f"{res['base_conversions']:,.0f}")
            st.metric("New conversions",f"{res['new_conversions']:,.0f}")
            st.metric("Incremental contribution",f"CAD {res['incremental_contribution']:,.0f}")
            st.metric("Net incremental profit",f"CAD {res['net_incremental_profit']:,.0f}")
        decision_strip(f"Net incremental profit = CAD {res['net_incremental_profit']:,.0f}",res["interpretation"],res["recommendation"])
    with exp_tab:
        st.write("Prototype A/B test: treatment and control conversion rates.")
        c1,c2=st.columns([1,1.3])
        with c1:
            n_control=st.slider("Control sample size",50,5000,500,50)
            n_treat=st.slider("Treatment sample size",50,5000,500,50)
            conv_control=st.slider("Control conversion (%)",0.0,80.0,20.0,1.0)
            conv_treat=st.slider("Treatment conversion (%)",0.0,80.0,26.0,1.0)
            value_per_success=st.slider("Contribution per conversion (CAD)",10,500,420,10,key="m5_exp_val")
            treatment_cost_per_person=st.slider("Treatment cost per exposed customer (CAD)",0.0,50.0,2.0,0.5)
            res=experiment_model(n_control,n_treat,conv_control,conv_treat,value_per_success,treatment_cost_per_person)
        with c2:
            st.latex(r"\hat{\tau}=\bar{Y}_{Treatment}-\bar{Y}_{Control}")
            st.latex(r"Incremental\ value/person=\hat{\tau}\times Contribution-Cost")
            st.metric("Estimated treatment effect",f"{res['effect_pp']:.1f} pp")
            st.metric("Approx. z-statistic",f"{res['z']:.2f}")
            st.metric("Incremental value / treated customer",f"CAD {res['value_per_treated']:.2f}")
            st.metric("Decision",res["decision"])
        decision_strip(f"Treatment effect = {res['effect_pp']:.1f} pp",res["interpretation"],res["recommendation"])

st.divider()
st.caption("NorthStar Appliances — teaching prototype. Results are based on transparent classroom assumptions, not estimated forecasts. The purpose is to make the economic mechanism visible.")
