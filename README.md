# NorthStar Economics Dashboard — Streamlit Prototype

A teaching prototype for an MBA Managerial Economics course.

## Included modules

### Module 1 — Customers, Costs, Pricing & Productivity
- Demand equation: `Qd = 26,000 - 20P`
- Supply equation: `Qs = -6,000 + 20P`
- Equilibrium price and quantity
- Movement along curves vs shifts in curves
- Point elasticity
- Simple ±5% pricing scenarios using contribution margin

### Module 2 — Competition, Strategy & Information
- Simple 2×2 game theory / expected payoff model
- Adverse selection with expected value and screening
- Moral hazard with effort choice and incentive pay
- Signalling with type-specific signal costs

### Module 3 — Global Markets, Trade & Sourcing
- Absolute advantage
- Opportunity cost
- Comparative advantage
- Production allocation
- Exchange-rate impact on imported cost and profit
- AI/automation productivity shocks that can change comparative advantage

### Module 4 — Reading the Economy, Anticipating Policy & Managing Risk
- Economic signal → policymaker objective → possible policy response → NorthStar implication
- Structured dropdown
- Separate plain-English text input button using transparent keyword rules
- Price ceiling / floor model using Module 1 equations
- Shortage / surplus calculation

### Module 5 — Internal Levers, Behaviour & Evidence
- Incentives / AI productivity with quality-adjusted output
- Cost per effective unit
- Customer choice / default / framing economics
- Simple treatment-control experiment
- Scale / Retest / Stop recommendation

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Streamlit will normally open at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Put these files in a GitHub repository.
2. Sign in to Streamlit Community Cloud.
3. Create a new app.
4. Select the repository and `app.py`.
5. Deploy.

No API key is required for this prototype.

## Teaching design

Each model follows:

**Input → Economic Result → Interpretation → Managerial Recommendation**

The prototype deliberately uses transparent classroom assumptions rather than estimated forecasting models. It is designed so each module can be expanded after the corresponding lecture without changing the overall app architecture.
