"""NorthStar Appliances: the BUS 703 course app (dashboard).

Run locally:   streamlit run app.py
Live classroom experiments are on the page in pages/Module_5_Live_Experiments.py.
"""
import streamlit as st

st.set_page_config(page_title="NorthStar Economics Lab", page_icon="🧭", layout="wide")

from ui import inject_css  # noqa: E402
from views import home, m1, m2, m3, m4, m5  # noqa: E402

inject_css()

MODULES = {
    "Course overview": ("home", home.render),
    "1. Customers, costs & pricing": ("m1", m1.render),
    "2. Competition & information": ("m2", m2.render),
    "3. Trade & sourcing": ("m3", m3.render),
    "4. External shocks": ("m4", m4.render),
    "5. Behaviour & evidence": ("m5", m5.render),
}

with st.sidebar:
    st.markdown("### NorthStar Economics Lab")
    st.caption("BUS 703 Managerial Economics · Beedie School of Business")
    choice = st.radio("Module", list(MODULES), key="nav_module", label_visibility="collapsed")
    prefix, render = MODULES[choice]
    st.divider()
    if prefix != "home":
        st.caption("Every slider starts at the slide value. Change it, read the answer, then find what flips it.")
        if st.button("Reset this module to the case values", width="stretch"):
            for k in [k for k in st.session_state.keys() if str(k).startswith(prefix + "_")]:
                del st.session_state[k]
            st.rerun()
    st.page_link("pages/Module_5_Live_Experiments.py", label="Live classroom experiments", icon="🧪")
    st.caption("Build: revised Modules 1–5 (October 2026)")

render()
