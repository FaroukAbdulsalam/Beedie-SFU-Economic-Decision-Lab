"""Smoke test: render every module and the live-experiments page headlessly."""
from streamlit.testing.v1 import AppTest

MODS = ["Course overview", "1. Customers, costs & pricing", "2. Competition & information", "3. Trade & sourcing",
        "4. External shocks", "5. Behaviour & evidence"]

for mod in MODS:
    at = AppTest.from_file("app.py", default_timeout=60)
    at.run()
    at.sidebar.radio(key="nav_module").set_value(mod).run()
    assert not at.exception, (mod, at.exception)
    print(f"OK  {mod}: {len(at.get('plotly_chart'))} charts, {len(at.slider)} sliders")

at = AppTest.from_file("pages/Module_5_Live_Experiments.py", default_timeout=60)
at.run()
assert not at.exception, at.exception
at.text_input[0].set_value("northstar").run()
assert not at.exception, at.exception
at.radio(key="inst_source").set_value("Demo data (preview only)").run()
assert not at.exception, at.exception
print("OK  live experiments page, instructor view with demo data:", len(at.metric), "metrics")
