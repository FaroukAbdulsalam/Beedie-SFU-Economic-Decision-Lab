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
    provider_expected_cost, pilot_screen_value, high_effort_value,
    bargaining_split, delivered_cost, quality_adjusted_value,
    warranty_default_effect, framing_effect,
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
st.caption("Assignment 2 build • Modules 1–5 enabled")

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
        ("M2","Strategy & Information","Price wars, provider quality, contracts, bargaining."),
        ("M3","Trade & Sourcing","Comparative advantage, delivered cost, FX, technology."),
        ("M4","Policy & Risk","Shock transmission, price controls, scenarios, triggers."),
        ("M5","Behaviour & Evidence","KPIs, defaults, color, framing, experiments."),
    ]
    for col,(num,title,desc) in zip(cols,cards):
        with col:
            st.markdown(f'<div class="decision-box"><div class="decision-label">{num}</div><b>{title}</b><br><span class="small-note">{desc}</span></div>',unsafe_allow_html=True)
    st.info("For Module 5 live classroom experiments, use the **Module 5 Live Experiments** page in the sidebar. The dashboard tabs are aligned to the guided Assignment 2 calculations and decision prompts.")

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
    banner("MODULE 2","Competition, Strategy & Information","How should NorthStar respond when rivals, retailers and providers respond strategically or know something NorthStar does not?")
    st.caption("Assignment 2 • Part A. These tabs use the same baseline numbers as the guided assignment.")
    pw_tab,provider_tab,contract_tab,bargain_tab=st.tabs(["Price War","Provider Quality & Screening","Moral Hazard & Contract","HomeHub Bargaining"])

    with pw_tab:
        st.subheader("A1–A2. NovaHome response and the price-war problem")
        st.write("The payoff table reports **relative strategic value** as (NorthStar payoff, NovaHome payoff).")
        payoff_df=pd.DataFrame(
            [["8, 8","4, 11"],["11, 4","5, 5"]],
            index=["NorthStar Maintains","NorthStar Discounts"],
            columns=["NovaHome Maintains","NovaHome Discounts"]
        )
        st.dataframe(payoff_df,use_container_width=True)
        c1,c2=st.columns([1,1.25])
        with c1:
            rival_action=st.radio("If NovaHome chooses...",["Maintains","Discounts"],horizontal=True,key="m2_rival_action")
            if rival_action=="Maintains":
                ns_maintain,ns_discount=8,11
            else:
                ns_maintain,ns_discount=4,5
            st.metric("NorthStar payoff — Maintain",ns_maintain)
            st.metric("NorthStar payoff — Discount",ns_discount)
            st.metric("NorthStar best response","Discount" if ns_discount>ns_maintain else "Maintain")
        with c2:
            pricewar_df=pd.DataFrame([
                ["NorthStar maintains",899,479,10000,(899-479)*10000],
                ["NorthStar discounts alone",849,479,12000,(849-479)*12000],
                ["Both firms discount",849,479,10500,(849-479)*10500],
            ],columns=["Scenario","Price","VC","Units","Total contribution"])
            st.dataframe(pricewar_df.style.format({
                "Price":"CAD {:,.0f}","VC":"CAD {:,.0f}","Units":"{:,.0f}",
                "Total contribution":"CAD {:,.0f}"
            }),use_container_width=True,hide_index=True)
        gain_alone=(849-479)*12000-(899-479)*10000
        change_both=(849-479)*10500-(899-479)*10000
        c1,c2=st.columns(2)
        c1.metric("Gain if NorthStar discounts alone",f"CAD {gain_alone:,.0f}")
        c2.metric("Change if NovaHome matches",f"CAD {change_both:,.0f}")
        decision_strip(
            "Discount is a best response in the payoff table, but mutual discounting lowers value.",
            "The price cut looks attractive if NovaHome stays passive: contribution rises by CAD 240,000. If NovaHome matches, NorthStar contribution falls by CAD 315,000 versus maintaining.",
            "Do not evaluate a discount in isolation. Compare price matching with differentiation, service, warranty value, versioning or targeted offers, and state what rival response would change your decision."
        )

    with provider_tab:
        st.subheader("A3. Warranty provider: cheap may be expensive")
        units=st.slider("Appliances covered",1000,30000,10000,1000,key="m2_provider_units")
        c1,c2=st.columns(2)
        with c1:
            h_fee=st.number_input("High-quality provider fee / unit",value=115.0,key="m2_h_fee")
            h_extra=st.number_input("High-quality expected extra cost / unit",value=15.0,key="m2_h_extra")
            high=provider_expected_cost(h_fee,h_extra,units)
            st.metric("High-quality total cost / unit",f"CAD {high['total_per_unit']:,.0f}")
            st.metric("High-quality total expected cost",f"CAD {high['total_expected_cost']:,.0f}")
        with c2:
            l_fee=st.number_input("Low-quality provider fee / unit",value=85.0,key="m2_l_fee")
            l_extra=st.number_input("Low-quality expected extra cost / unit",value=70.0,key="m2_l_extra")
            low=provider_expected_cost(l_fee,l_extra,units)
            st.metric("Low-quality total cost / unit",f"CAD {low['total_per_unit']:,.0f}")
            st.metric("Low-quality total expected cost",f"CAD {low['total_expected_cost']:,.0f}")
        st.metric("Expected cost difference",f"CAD {low['total_expected_cost']-high['total_expected_cost']:,.0f} more for low quality")
        st.info("**Concept check:** Before signing, hidden provider quality is an **adverse-selection** problem. A guarantee voluntarily offered by the provider is **signalling**; a pilot or test designed by NorthStar is **screening**.")
        st.divider()
        st.markdown("#### Is the pilot screen worth it?")
        c1,c2,c3=st.columns(3)
        p_reveal=c1.slider("Probability pilot reveals low quality",0.0,1.0,0.70,0.05,key="m2_pilot_prob")
        avoided_loss=c2.number_input("Loss avoided if problem is found (CAD)",value=300000.0,step=10000.0,key="m2_avoid_loss")
        pilot_cost=c3.number_input("Pilot cost (CAD)",value=50000.0,step=5000.0,key="m2_pilot_cost")
        ps=pilot_screen_value(p_reveal,avoided_loss,pilot_cost)
        c1,c2=st.columns(2)
        c1.metric("Expected benefit",f"CAD {ps['expected_benefit']:,.0f}")
        c2.metric("Net expected value",f"CAD {ps['net_expected_value']:,.0f}")
        decision_strip(
            f"Pilot net expected value = CAD {ps['net_expected_value']:,.0f}",
            "Screening is an investment in information. It is worthwhile when the expected loss avoided exceeds the cost of the screen.",
            "Under the assignment baseline the pilot has positive expected value. Still ask what the pilot can miss and whether the result generalizes to national scale."
        )

    with contract_tab:
        st.subheader("A4. Hidden effort after the contract")
        c1,c2=st.columns([1,1.2])
        with c1:
            low_repeat=st.slider("Repeat visits under low effort (%)",0.0,30.0,12.0,1.0,key="m2_low_rep")/100
            high_repeat=st.slider("Repeat visits under high effort (%)",0.0,30.0,5.0,1.0,key="m2_high_rep")/100
            cases=st.slider("Service cases",1000,30000,10000,1000,key="m2_cases")
            repeat_cost=st.slider("Cost per repeat visit (CAD)",50,500,250,10,key="m2_repeat_cost")
            effort_cost=st.slider("Provider cost of high effort (CAD)",0,300000,120000,10000,key="m2_effort_cost")
            hv=high_effort_value(low_repeat,high_repeat,cases,repeat_cost,effort_cost)
        with c2:
            st.latex(r"Value\ of\ high\ effort=(r_L-r_H)\times Cases\times Cost_{repeat}")
            st.metric("Gross value to NorthStar",f"CAD {hv['gross_benefit']:,.0f}")
            st.metric("Net joint surplus after effort cost",f"CAD {hv['net_surplus']:,.0f}")
            st.write("**Why moral hazard?** The contract is already signed; the hidden action is the provider's effort afterward.")
        st.markdown("#### Design a balanced performance contract")
        measures=st.multiselect(
            "Which measures should NorthStar monitor?",
            ["Response time","First-time fix rate","Repeat visits","Customer satisfaction","Parts usage","Complaint rate"],
            default=["First-time fix rate","Repeat visits","Customer satisfaction"],
            key="m2_contract_measures"
        )
        st.write("Selected measures:", ", ".join(measures) if measures else "None yet")
        st.warning("Avoid paying only for one narrow metric. A provider can improve the measured KPI while damaging the underlying objective.")

    with bargain_tab:
        st.subheader("A4. HomeHub bargaining and outside options")
        total_value=st.slider("Value created by cooperation (CAD millions)",5.0,20.0,10.0,0.5,key="m2_total_value")
        ns_out=st.slider("NorthStar outside option (CAD millions)",0.0,10.0,4.0,0.5,key="m2_ns_out")
        hh_out=st.slider("HomeHub outside option (CAD millions)",0.0,10.0,3.0,0.5,key="m2_hh_out")
        share=st.slider("NorthStar share of cooperative surplus (%)",0,100,50,5,key="m2_share")/100
        b=bargaining_split(total_value,ns_out,hh_out,share)
        c1,c2,c3=st.columns(3)
        c1.metric("Cooperative surplus",f"CAD {b['surplus']:,.1f}m")
        c2.metric("NorthStar value",f"CAD {b['party_a']:,.1f}m")
        c3.metric("HomeHub value",f"CAD {b['party_b']:,.1f}m")
        improved_out=st.slider("Stress test: improve NorthStar direct-channel outside option",ns_out,10.0,max(ns_out,5.0),0.5,key="m2_improved_out")
        b2=bargaining_split(total_value,improved_out,hh_out,share)
        st.metric("NorthStar value after stronger outside option",f"CAD {b2['party_a']:,.1f}m")
        decision_strip(
            f"NorthStar outside option: CAD {ns_out:.1f}m → CAD {improved_out:.1f}m",
            "Bargaining power depends on what each party can credibly do without the deal. Improving the direct channel can change the negotiation before the meeting starts.",
            "Do not negotiate only over HomeHub's requested margin. Invest in credible alternatives and compare the value of agreement with the value of walking away."
        )

with m3:
    banner("MODULE 3","Global Markets, Trade & Sourcing","Where should NorthStar source when locations differ in productivity, delivered cost, currencies, policy exposure and technology?")
    st.caption("Assignment 2 • Part B. Use the tabs below for B1–B3.")
    trade_tab,cost_tab,fx_tab,tech_tab=st.tabs(["Comparative Advantage","Delivered Economic Cost","FX & Capital Mobility","Technology & Flip Condition"])

    with trade_tab:
        st.subheader("B1. Absolute advantage is not comparative advantage")
        ca_boards=st.slider("Canada — control boards/day",1.0,40.0,12.0,1.0,key="m3_ca_boards")
        ca_sensors=st.slider("Canada — AI sensors/day",1.0,50.0,24.0,1.0,key="m3_ca_sensors")
        mx_boards=st.slider("Mexico — control boards/day",1.0,40.0,8.0,1.0,key="m3_mx_boards")
        mx_sensors=st.slider("Mexico — AI sensors/day",1.0,50.0,10.0,1.0,key="m3_mx_sensors")
        res=trade_advantage(ca_boards,ca_sensors,mx_boards,mx_sensors,"Canada","Mexico")
        df=pd.DataFrame([
            ["Canada",ca_boards,ca_sensors,res["oc_board_a"],res["oc_sensor_a"]],
            ["Mexico",mx_boards,mx_sensors,res["oc_board_b"],res["oc_sensor_b"]]
        ],columns=["Location","Boards/day","Sensors/day","OC of 1 board (sensors)","OC of 1 sensor (boards)"])
        st.dataframe(df.style.format({
            "Boards/day":"{:.1f}","Sensors/day":"{:.1f}",
            "OC of 1 board (sensors)":"{:.2f}","OC of 1 sensor (boards)":"{:.2f}"
        }),use_container_width=True,hide_index=True)
        decision_strip(
            f"{res['comparative_board']} → boards; {res['comparative_sensor']} → sensors",
            "Comparative advantage is determined by opportunity cost, not by who can produce more of both goods.",
            res["recommendation"]
        )

    with cost_tab:
        st.subheader("B2. Quote price is not delivered economic cost")
        c1,c2,c3=st.columns(3)
        domestic=c1.number_input("Canada quoted cost / unit (CAD)",value=185.0,key="m3_domestic")
        mexico=c2.number_input("Mexico quoted cost / unit (CAD)",value=150.0,key="m3_mexico")
        asia_quote=c3.number_input("Asia quoted cost / unit (CAD)",value=125.0,key="m3_asia_quote")
        st.markdown("**Add-ons for Asian sourcing**")
        a,b,c,d,e=st.columns(5)
        freight=a.number_input("Freight",value=9.0,key="m3_freight")
        insurance=b.number_input("Insurance",value=2.0,key="m3_ins")
        compliance=c.number_input("Compliance",value=3.0,key="m3_comp")
        inventory=d.number_input("Inventory",value=7.0,key="m3_inv")
        rework=e.number_input("Quality / rework",value=5.0,key="m3_rework")
        asia=delivered_cost(asia_quote,freight,insurance,compliance,inventory,rework)
        comp=pd.DataFrame([
            ["Canada",domestic,"Quote shown; add comparable local costs if relevant"],
            ["Mexico",mexico,"Quote shown; verify whether logistics/inventory/quality costs are included"],
            ["Asia",asia["delivered_cost"],f"Quote {asia_quote:.0f} + add-ons {asia['add_on_cost']:.0f}"],
        ],columns=["Location","Current comparison cost","Important caveat"])
        st.dataframe(comp.style.format({"Current comparison cost":"CAD {:,.0f}"}),use_container_width=True,hide_index=True)
        st.metric("Asia delivered economic cost",f"CAD {asia['delivered_cost']:,.0f}/unit")
        decision_strip(
            f"Asia: CAD {asia_quote:,.0f} quote → CAD {asia['delivered_cost']:,.0f} delivered",
            "A low invoice price can be offset by freight, inventory, compliance, quality and the economic value of time and flexibility.",
            "Do not declare a winner until all locations are compared on the same delivered-cost basis. Near-ties make responsiveness, policy and currency exposure especially important."
        )

    with fx_tab:
        st.subheader("B3. Currency risk and capital mobility")
        usd=st.slider("USD component price",40,250,100,5,key="m3_usd")
        c1,c2=st.columns(2)
        fx0=c1.slider("Baseline CAD per USD",0.90,1.80,1.30,0.01,key="m3_fx0")
        fx1=c2.slider("Stress CAD per USD",0.90,1.80,1.45,0.01,key="m3_fx1")
        cad0=usd*fx0; cad1=usd*fx1
        c1,c2,c3=st.columns(3)
        c1.metric("Baseline CAD cost",f"CAD {cad0:,.0f}")
        c2.metric("Stress CAD cost",f"CAD {cad1:,.0f}")
        c3.metric("Increase",f"CAD {cad1-cad0:,.0f}/unit")
        st.info("**Exchange-rate risk:** At what price can NorthStar convert currency?  \n**Convertibility / capital-mobility risk:** Can NorthStar convert or move funds when needed, and under what restrictions?")
        st.markdown("#### Capital-mobility stress test")
        mobility=st.selectbox("Access to foreign currency / ability to move funds",["Normal","Delayed / costly","Restricted"],key="m3_mobility")
        if mobility=="Normal":
            st.success("Financial mobility does not currently add a major constraint.")
        elif mobility=="Delayed / costly":
            st.warning("Add liquidity buffers, payment lead time and financing cost to the sourcing comparison.")
        else:
            st.error("A location can look cheap operationally and still be unattractive if profits, supplier payments or currency conversion are constrained.")

    with tech_tab:
        st.subheader("B3. Technology can change comparative advantage")
        st.write("The module example reduces Canadian labour hours per batch from **100 to 40** after automation.")
        before=st.slider("Canadian labour hours per batch — before automation",20,200,100,5,key="m3_hours_before")
        after=st.slider("Canadian labour hours per batch — after automation",10,before,40,5,key="m3_hours_after")
        reduction=(before-after)/before*100
        st.metric("Labour-hours reduction",f"{reduction:.1f}%")
        st.write("Use the comparative-advantage tab to test how a productivity shock changes opportunity cost.")
        flip=st.multiselect(
            "Which conditions could flip your sourcing recommendation?",
            ["CAD depreciates materially","New tariff / trade restriction","Lead time worsens","Convertibility restrictions tighten","Domestic automation lowers cost","Supplier quality changes"],
            default=["CAD depreciates materially","Domestic automation lowers cost"],
            key="m3_flip"
        )
        st.write("Selected flip conditions:", ", ".join(flip) if flip else "None yet")
        decision_strip(
            "Comparative advantage is dynamic",
            "Automation can reduce the labour-cost disadvantage of nearby production while AI can also make distant coordination easier.",
            "State a sourcing recommendation for today's assumptions and a specific condition that would reverse it."
        )

with m4:
    banner("MODULE 4","Managing External Shocks","How should NorthStar trace macro and policy shocks into the firm, preserve flexibility and act before conditions force a response?")
    st.caption("Assignment 2 • Part C. The app follows Shock → Transmission → Exposure → Response.")
    shock_tab,control_tab,scenario_tab=st.tabs(["Shock Map","Price Ceiling / Floor","Scenario & Contingent Plan"])

    with shock_tab:
        st.subheader("C1. Shock → Transmission → Exposure → Response")
        shock=st.selectbox("Select a shock",[
            "Elevated inflation","High interest rates","Weaker Canadian dollar","Slower housing activity"
        ],key="m4_shock")
        map4={
            "Elevated inflation":{
                "transmission":"Input, wage, freight and energy costs rise.",
                "exposure":"Margins, supplier contracts, pricing and working capital.",
                "response":"Stress-test pass-through, supplier renegotiation, product design and sourcing."
            },
            "High interest rates":{
                "transmission":"Financing and working-capital costs rise; durable-goods demand may weaken.",
                "exposure":"Inventory, borrowing, capex, housing-linked demand and AI investment.",
                "response":"Tighten inventory, raise investment hurdle rates, stage hard-to-reverse projects."
            },
            "Weaker Canadian dollar":{
                "transmission":"USD-priced imports become more expensive in CAD.",
                "exposure":"Imported components, gross margin, supplier payments and sourcing.",
                "response":"Revisit Module 3 sourcing, hedging, pricing and supplier mix."
            },
            "Slower housing activity":{
                "transmission":"Fewer housing transactions and renovations can reduce appliance demand.",
                "exposure":"Sales forecast, inventory, production and retailer orders.",
                "response":"Reduce forecast commitment, target replacement demand and preserve liquidity."
            },
        }
        m=map4[shock]
        c1,c2,c3=st.columns(3)
        c1.info(f"**Transmission**\n\n{m['transmission']}")
        c2.info(f"**NorthStar exposure**\n\n{m['exposure']}")
        c3.info(f"**Possible response**\n\n{m['response']}")
        st.write("**Assignment move:** choose two shocks and complete the chain for each. At least one should connect back to your Module 3 sourcing recommendation.")

    with control_tab:
        st.subheader("C2. Government changes the market")
        c1,c2=st.columns([.9,1.5])
        with c1:
            policy_type=st.radio("Policy",["Price ceiling","Price floor"],horizontal=True,key="m4_policy_type")
            default_policy_price=600 if policy_type=="Price ceiling" else 1000
            policy_price=st.slider("Controlled price (CAD)",300,1300,default_policy_price,25,key="m4_policy_price")
            a_d=26000; a_s=-6000
            res=price_control(a_d,20,a_s,20,policy_type,policy_price)
            st.metric("Market equilibrium price",f"CAD {res['equilibrium_price']:,.0f}")
            st.metric("Quantity demanded",f"{res['qd']:,.0f}")
            st.metric("Quantity supplied",f"{res['qs']:,.0f}")
            if res["shortage"]>0: st.metric("Shortage",f"{res['shortage']:,.0f}")
            if res["surplus"]>0: st.metric("Surplus",f"{res['surplus']:,.0f}")
        with c2:
            st.plotly_chart(plot_demand_supply(a_d,20,a_s,20,control_price=policy_price),use_container_width=True)
        decision_strip(res["result_label"],res["interpretation"],res["recommendation"])

    with scenario_tab:
        st.subheader("C3. Scenario planning: action + indicator + trigger")
        scenario=st.selectbox("Choose scenario",["Soft landing","Persistent inflation","Recession"],key="m4_scenario")
        scenarios={
            "Soft landing":{
                "signals":"Inflation falling; rates lower; CAD stable; demand healthy.",
                "challenge":"Avoid being too defensive as financing conditions and demand improve.",
                "actions":["Revisit postponed investments","Normalize inventory cautiously","Test selective growth initiatives"],
                "ai":"A staged rollout can accelerate if financing costs fall and demand remains healthy."
            },
            "Persistent inflation":{
                "signals":"Costs elevated; rates high; CAD weak; demand moderate.",
                "challenge":"Protect margins without destroying demand or locking into inflexible commitments.",
                "actions":["Stage price pass-through","Diversify sourcing","Tighten inventory and preserve cash"],
                "ai":"Pilot/stage rather than fully commit unless labour savings are especially valuable."
            },
            "Recession":{
                "signals":"Demand weakens sharply; rates high initially and later fall.",
                "challenge":"Protect liquidity and avoid excess inventory/capacity.",
                "actions":["Reduce forecast commitment","Delay hard-to-reverse capex","Focus on replacement demand and cash"],
                "ai":"Wait or run a low-cost pilot unless automation is essential to near-term cost survival."
            },
        }
        s=scenarios[scenario]
        st.info(f"**Signals:** {s['signals']}")
        st.warning(f"**Management challenge:** {s['challenge']}")
        st.write("**Possible immediate actions:**")
        for a in s["actions"]: st.write("•",a)
        st.write("**AI/automation implication:**",s["ai"])
        indicator=st.text_input("Indicator to monitor",placeholder="e.g., CAD/USD, lead time, borrowing rate, housing starts",key="m4_indicator")
        trigger=st.text_input("Trigger that would change the decision",placeholder="e.g., CAD/USD exceeds 1.50 for four weeks",key="m4_trigger")
        contingent=st.text_input("Contingent action",placeholder="e.g., shift 20% of sourcing to Mexico and increase safety stock",key="m4_contingent")
        if indicator or trigger or contingent:
            st.success(f"**Your contingent plan:** Monitor **{indicator or '...'}**. If **{trigger or '...'}**, then **{contingent or '...'}**.")

with m5:
    banner("MODULE 5","Behaviour, Incentives & Evidence","Which controllable interventions improve productivity, customer outcomes and margins—and what evidence shows that they actually worked?")
    st.caption("Assignment 2 • Part D. Complete D1, one behavioural experiment (D2A–D2C), and D3. The additional behavioural experiment can be used for bonus work.")
    st.page_link("pages/Module_5_Live_Experiments.py", label="Open the Module 5 Live Experiments", icon="🧪")
    kpi_tab,default_tab,color_tab,frame_tab,evidence_tab=st.tabs(["KPI & Quality","Experiment 2: Warranty Default","Experiment 3: Color Preference","Experiment 4: Gains vs Losses","Evidence & Scaling"])

    with kpi_tab:
        st.subheader("D1. Incentives: more activity or more value?")
        st.latex(r"Quality\ adjusted\ value=10\times Correct-6\times Incorrect")
        st.info("**Worked example — Control:** 10 × 9 − 6 × 1 = **84**.")
        df=pd.DataFrame([
            ["Control",10,9,1,quality_adjusted_value(9,1)],
            ["Quantity incentive",14,10,4,quality_adjusted_value(10,4)],
            ["Balanced incentive",12,11,1,quality_adjusted_value(11,1)],
        ],columns=["Group","Attempted","Correct","Incorrect","Quality-adjusted value"])
        st.dataframe(df,use_container_width=True,hide_index=True)
        activity=df.loc[df["Attempted"].idxmax(),"Group"]
        value=df.loc[df["Quality-adjusted value"].idxmax(),"Group"]
        c1,c2=st.columns(2)
        c1.metric("Most activity",activity)
        c2.metric("Highest quality-adjusted value",value)
        decision_strip(
            f"Quantity system = {quality_adjusted_value(10,4)}; Balanced = {quality_adjusted_value(11,1)}",
            "The quantity incentive produces more activity but less economic value because errors are costly. This is the Goodhart/KPI problem.",
            "Use a balanced incentive that rewards throughput and quality. Monitor errors, repeat work, complaints and other hidden costs."
        )

    with default_tab:
        st.subheader("D2A. Experiment 2 — Warranty Default")
        opt_in=st.slider("Opt-in adoption (%)",0,100,20,1,key="m5_optin")/100
        opt_out=st.slider("Opt-out adoption (%)",0,100,40,1,key="m5_optout")/100
        customers=st.slider("Customers",1000,50000,10000,1000,key="m5_def_customers")
        contrib=st.slider("Net contribution per plan (CAD)",0,200,40,5,key="m5_def_contrib")
        w=warranty_default_effect(opt_in,opt_out,customers,contrib)
        c1,c2,c3=st.columns(3)
        c1.metric("Default effect",f"{w['lift_pp']:.0f} pp")
        c2.metric("Incremental plans",f"{w['incremental_plans']:,.0f}")
        c3.metric("Incremental contribution",f"CAD {w['incremental_contribution']:,.0f}")
        decision_strip(
            f"Incremental contribution = CAD {w['incremental_contribution']:,.0f}",
            "A default can change choices through inertia, attention, status quo or implied recommendation.",
            "Do not scale from margin alone. Monitor cancellations, complaints, trust, transparency, vulnerable customers and regulatory risk."
        )

    with color_tab:
        st.subheader("D2B. Experiment 3 — Product Color Preference")
        st.write("Students choose among **White, Black, Silver and Navy Blue** while price and features are held constant.")
        st.info("This is a **preference test**, not a treatment-effect experiment: everyone sees all options.")
        color_data=pd.DataFrame({
            "Color":["White","Black","Silver","Navy Blue"],
            "Preference share (%)":[25,35,20,20],
            "Purchase likelihood (1–5)":[3.6,4.2,3.5,3.9],
            "Would pay CAD 50 more (%)":[12,28,16,24],
        })
        st.caption("Enter your class or pilot results below; the defaults are illustrative only.")
        edited=st.data_editor(color_data,num_rows="fixed",use_container_width=True,key="m5_color_editor")
        winner=edited.loc[edited["Preference share (%)"].astype(float).idxmax(),"Color"]
        st.metric("Highest preference share",winner)
        st.write("Use preference share together with purchase likelihood and willingness to pay. The winning color is useful evidence, but it is **not automatically the production decision**.")
        st.warning("Also consider small-sample uncertainty, inventory complexity, production costs, segment differences and changing tastes.")

    with frame_tab:
        st.subheader("D2C. Experiment 4 — Gains vs. Losses")
        st.write("**Standard appliance = CAD 899. EcoSmart = CAD 999. EcoSmart saves about CAD 180/year in energy costs.**")
        c1,c2=st.columns(2)
        c1.info("**Gain frame (control)**\n\nChoose EcoSmart and **save about CAD 180 per year** in energy costs.")
        c2.warning("**Loss frame (treatment)**\n\nChoose the standard model and you could **lose about CAD 180 per year** in extra energy costs.")
        gain_rate=st.slider("EcoSmart choice under gain frame (%)",0,100,40,1,key="m5_gain_rate")/100
        loss_rate=st.slider("EcoSmart choice under loss frame (%)",0,100,50,1,key="m5_loss_rate")/100
        fe=framing_effect(gain_rate,loss_rate)
        st.metric("Framing effect: Loss − Gain",f"{fe['effect_pp']:+.1f} pp")
        decision_strip(
            f"Loss-frame minus gain-frame = {fe['effect_pp']:+.1f} pp",
            "The economic facts are held constant. Any systematic choice difference is consistent with framing affecting how customers evaluate the offer.",
            "Treat loss aversion as a behavioural hypothesis, not a universal law. Test transparently and consider trust and manipulation concerns before scaling."
        )

    with evidence_tab:
        st.subheader("D3. Evidence: did the intervention cause the result?")
        evidence_type=st.radio("What kind of evidence are you evaluating?",["Treatment vs Control","Preference Test"],horizontal=True,key="m5_evidence_type")
        if evidence_type=="Treatment vs Control":
            c1,c2=st.columns([1,1.3])
            with c1:
                n_control=st.slider("Control sample size",50,5000,500,50,key="m5_n_control")
                n_treat=st.slider("Treatment sample size",50,5000,500,50,key="m5_n_treat")
                conv_control=st.slider("Control outcome rate (%)",0.0,100.0,20.0,1.0,key="m5_conv_control")
                conv_treat=st.slider("Treatment outcome rate (%)",0.0,100.0,26.0,1.0,key="m5_conv_treat")
                value_per_success=st.slider("Value per success (CAD)",10,1000,420,10,key="m5_value")
                treatment_cost_per_person=st.slider("Treatment cost / exposed person (CAD)",0.0,100.0,2.0,0.5,key="m5_cost")
                res=experiment_model(n_control,n_treat,conv_control,conv_treat,value_per_success,treatment_cost_per_person)
            with c2:
                st.metric("Estimated treatment effect",f"{res['effect_pp']:.1f} pp")
                st.metric("Approx. z-statistic",f"{res['z']:.2f}")
                st.metric("Incremental value / treated person",f"CAD {res['value_per_treated']:.2f}")
                st.metric("Decision aid",res["decision"])
            decision_strip(f"Treatment effect = {res['effect_pp']:.1f} pp",res["interpretation"],res["recommendation"])
        else:
            st.info("A color preference test tells NorthStar **what this sample prefers**. Because everyone sees all colors, it does not estimate a causal treatment effect.")
            st.write("Before scaling a color decision, ask whether the sample is representative, whether preferences differ by segment, whether willingness to pay covers added complexity, and whether the preference is stable over time.")
        st.divider()
        st.markdown("#### Before-and-after is weak evidence")
        st.write("If sales rise from **10,000 to 12,000** after a marketing change, the change may have helped—but seasonality, competitor stockouts, subsidies, price changes or customer mix could also explain the increase.")
        st.write("A credible test asks: **What changed? Who received it? Who is the comparison group? What outcome reflects real value? Could something else explain the result? Is the effect large enough to justify scaling?**")

st.divider()
st.caption("NorthStar Appliances — teaching prototype aligned to Assignments 1 & 2. Results are based on transparent classroom assumptions. Use the tools to understand the mechanism, interpret evidence, state a recommendation and identify the condition that would change it.")
