"""Shared presentation layer for the NorthStar course app.

Design tokens
-------------
red    #A6192E  Beedie red: decisions, the current answer, primary actions
ink    #1D232B  text
slate  #5B6472  secondary text, axes
blue   #1F5FA8  second series (as in the slides)
blush  #F6E7E9  highlight fill (the slides' Highlight boxes)
rule   #E2E4E8  hairlines

One signature element: the flip ruler. Every tool ends with its answer and the
threshold that would reverse it, drawn on the same scale.
"""
from __future__ import annotations

import html
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

RED, INK, SLATE, BLUE, BLUSH, RULE = "#A6192E", "#1D232B", "#5B6472", "#1F5FA8", "#F6E7E9", "#E2E4E8"
GREEN, AMBER = "#2E7D4F", "#B7791F"

pio.templates["northstar"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Source Sans 3, Source Sans Pro, Helvetica, Arial, sans-serif", size=13, color=INK),
        colorway=[RED, BLUE, SLATE, GREEN, AMBER],
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
        xaxis=dict(gridcolor="#EEF0F3", zerolinecolor=RULE, linecolor=RULE, ticks="outside", tickcolor=RULE),
        yaxis=dict(gridcolor="#EEF0F3", zerolinecolor=RULE, linecolor=RULE, ticks="outside", tickcolor=RULE),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=36, b=10),
        hoverlabel=dict(bgcolor="#FFFFFF", font_color=INK, bordercolor=RULE),
    )
)
pio.templates.default = "northstar"

CSS = f"""
<style>
:root {{ --red:{RED}; --ink:{INK}; --slate:{SLATE}; --blue:{BLUE}; --blush:{BLUSH}; --rule:{RULE}; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }}
h1, h2, h3 {{ letter-spacing: -0.01em; }}
.ns-question {{ font-size: 1.12rem; color: var(--slate); max-width: 70ch; margin: -0.4rem 0 1.1rem; line-height: 1.5; }}
.ns-lede {{ color: var(--slate); max-width: 72ch; line-height: 1.55; margin: 0 0 .8rem; }}
.ns-answer {{ display: grid; grid-template-columns: 1.1fr 1.4fr 1.4fr; gap: 0; border: 1px solid var(--rule);
  border-left: 4px solid var(--red); background: #fff; border-radius: 6px; margin: .6rem 0 .4rem; }}
.ns-answer > div {{ padding: .85rem 1rem; }}
.ns-answer > div + div {{ border-left: 1px solid var(--rule); }}
.ns-answer .lbl {{ font-size: .82rem; color: var(--slate); margin-bottom: .2rem; }}
.ns-answer .big {{ font-family: 'Source Serif 4', 'Source Serif Pro', Georgia, serif; font-size: 1.35rem;
  line-height: 1.25; font-weight: 650; color: var(--ink); font-variant-numeric: tabular-nums; }}
.ns-answer .txt {{ line-height: 1.45; }}
@media (max-width: 760px) {{ .ns-answer {{ grid-template-columns: 1fr; }}
  .ns-answer > div + div {{ border-left: none; border-top: 1px solid var(--rule); }} }}
.ns-ruler {{ background:#fff; border:1px solid var(--rule); border-radius:6px; padding:.7rem 1rem .9rem; margin:.4rem 0 1rem; }}
.ns-ruler .head {{ display:flex; justify-content:space-between; gap:1rem; font-size:.9rem; margin-bottom:.55rem; }}
.ns-ruler .head b {{ color: var(--ink); }}
.ns-ruler .track {{ position:relative; height:10px; border-radius:5px; background:linear-gradient(90deg, var(--zl) 0 var(--cut), var(--zr) var(--cut) 100%); }}
.ns-ruler .cut {{ position:absolute; top:-5px; width:2px; height:20px; background:var(--ink); left:var(--cut); }}
.ns-ruler .now {{ position:absolute; top:-6px; width:22px; height:22px; margin-left:-11px; border-radius:50%;
  background:var(--red); border:3px solid #fff; box-shadow:0 0 0 1px var(--red); left:var(--now); }}
.ns-ruler .ends {{ display:flex; justify-content:space-between; font-size:.82rem; color:var(--slate); margin-top:.5rem; }}
.ns-ruler .ends span:last-child {{ text-align:right; }}
.ns-step {{ border-left: 3px solid var(--rule); padding: .1rem 0 .1rem .9rem; margin: .4rem 0; }}
.ns-step b {{ color: var(--ink); }}
.ns-chain {{ display:grid; grid-template-columns: repeat(5, 1fr); gap: 0; border-top: 2px solid var(--ink); margin: .4rem 0 1.4rem; }}
.ns-chain > div {{ padding: .8rem .9rem 1rem 0; }}
.ns-chain > div + div {{ padding-left: .9rem; border-left: 1px solid var(--rule); }}
.ns-chain .n {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 2.1rem; color: var(--red); line-height: 1; }}
.ns-chain .t {{ font-weight: 700; margin: .35rem 0 .2rem; }}
.ns-chain .q {{ color: var(--slate); font-size: .92rem; line-height: 1.4; min-height: 3.9em; }}
.ns-chain .a {{ margin-top: .5rem; font-family: 'Source Serif 4', Georgia, serif; font-size: 1.02rem; line-height: 1.35; }}
@media (max-width: 900px) {{ .ns-chain {{ grid-template-columns: 1fr 1fr; }} .ns-chain > div + div {{ border-left: none; padding-left: 0; }} }}
.ns-matrix {{ border-collapse: collapse; margin: .2rem 0 .6rem; font-variant-numeric: tabular-nums; }}
.ns-matrix th, .ns-matrix td {{ border: 1px solid var(--rule); padding: .55rem .9rem; text-align: center; background:#fff; }}
.ns-matrix th {{ background: #F1F2F5; font-weight: 600; }}
.ns-matrix td.ne {{ background: var(--blush); }}
.ns-matrix .br {{ text-decoration: underline; text-decoration-color: var(--red); text-decoration-thickness: 2px; font-weight: 700; }}
.ns-note {{ font-size: .88rem; color: var(--slate); }}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(x) -> str:
    return html.escape(str(x))


def header(title: str, question: str):
    st.title(title)
    st.markdown(f'<p class="ns-question">{esc(question)}</p>', unsafe_allow_html=True)


def lede(text: str):
    st.markdown(f'<p class="ns-lede">{text}</p>', unsafe_allow_html=True)


def answer(result: str, why: str, do: str):
    """The three-part answer card used by every tool."""
    st.markdown(
        f'<div class="ns-answer"><div><div class="lbl">Answer</div><div class="big">{result}</div></div>'
        f'<div><div class="lbl">Why</div><div class="txt">{why}</div></div>'
        f'<div><div class="lbl">So NorthStar should</div><div class="txt">{do}</div></div></div>',
        unsafe_allow_html=True,
    )


def flip_ruler(title: str, value: float, cut: float, lo: float, hi: float, fmt=lambda v: f"{v:,.0f}",
               left: str = "", right: str = "", good_side: str = "right"):
    """Current value against the threshold that flips the decision, on one scale."""
    span = (hi - lo) or 1
    pos = lambda v: max(0.0, min(100.0, (v - lo) / span * 100))
    zl, zr = ("#EEF0F3", BLUSH) if good_side == "right" else (BLUSH, "#EEF0F3")
    side = "above" if value > cut else ("below" if value < cut else "at")
    st.markdown(
        f'<div class="ns-ruler" style="--cut:{pos(cut):.2f}%; --now:{pos(value):.2f}%; --zl:{zl}; --zr:{zr};">'
        f'<div class="head"><span>{esc(title)}</span>'
        f'<span>Now <b>{esc(fmt(value))}</b>, {side} the flip point <b>{esc(fmt(cut))}</b></span></div>'
        f'<div class="track"><div class="cut"></div><div class="now"></div></div>'
        f'<div class="ends"><span>{esc(left)}</span><span>{esc(right)}</span></div></div>',
        unsafe_allow_html=True,
    )


def step(text: str):
    st.markdown(f'<div class="ns-step">{text}</div>', unsafe_allow_html=True)


def note(text: str):
    st.markdown(f'<p class="ns-note">{text}</p>', unsafe_allow_html=True)


def case_value_help(case, fmt=None) -> str:
    return f"Case value: {fmt(case) if fmt else case}"


def cslider(label, key, lo, hi, case, step=None, fmt_help=None, fmt=None, help=None):
    """Slider whose default is the fact-sheet value; the help text always shows that value."""
    h = case_value_help(case, fmt_help) + (f". {help}" if help else "")
    kwargs = dict(min_value=lo, max_value=hi, value=case, key=key, help=h)
    if step is not None:
        kwargs["step"] = step
    if fmt is not None:
        kwargs["format"] = fmt
    return st.slider(label, **kwargs)


def predict(key: str, prompt: str, truth: float, unit: str = "", tol: float = 0.02, fmt=lambda v: f"{v:,.0f}"):
    """Ask for a prediction before revealing the answer."""
    with st.expander(f"Predict first: {prompt}", expanded=False):
        guess = st.number_input("Your prediction", key=f"{key}_guess", value=None, placeholder="Type a number",
                                format="%f" if abs(truth) < 10 else "%.0f")
        if st.button("Check my prediction", key=f"{key}_btn"):
            st.session_state[f"{key}_shown"] = True
        if st.session_state.get(f"{key}_shown"):
            if guess is None:
                st.info("Type a prediction first, then check it.")
            else:
                err = abs(guess - truth) / (abs(truth) or 1)
                verdict = "Spot on." if err <= tol else ("Close." if err <= 0.1 else "Not quite.")
                st.markdown(f"**{verdict}** The model gives **{fmt(truth)}{unit}**; you predicted {fmt(guess)}{unit}.")


def fig(height=380, xtitle="", ytitle="", **kw) -> go.Figure:
    f = go.Figure()
    f.update_layout(height=height, xaxis_title=xtitle, yaxis_title=ytitle, **kw)
    return f


def show(f: go.Figure, key=None):
    st.plotly_chart(f, key=key, config={"displayModeBar": False})


def m(x):
    """CAD millions with two decimals."""
    return f"CAD {x/1e6:,.2f}m"


def cad(x, d=0):
    return f"CAD {x:,.{d}f}"
