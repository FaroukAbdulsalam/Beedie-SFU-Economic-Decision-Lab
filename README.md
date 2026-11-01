# NorthStar Economics Lab (BUS 703)

The course app for Managerial Economics at Beedie. Every tool starts at the numbers on the revised
Module 1–5 slides, so what students see in the app matches the lecture.

## Structure

```
app.py                         dashboard entry point (deploy this file)
models.py                      the case fact sheet (CASE) and every economic model; no Streamlit code
ui.py                          styling, chart template, answer card, flip ruler, predict-first widget
views/home.py                  course overview
views/m1.py … views/m5.py      one file per module
pages/Module_5_Live_Experiments.py   live classroom experiments + instructor results
test_models.py                 checks the models reproduce the slide numbers (python test_models.py)
test_app.py                    renders every module and the experiments page headlessly (python test_app.py)
.streamlit/config.toml         theme (Beedie red, serif headings)
```

## Deploy

Point Streamlit Community Cloud at the root `app.py`. The sidebar shows "Build: revised Modules 1–5
(October 2026)"; if it does not, an older `app.py` is still running.

Set the `INSTRUCTOR_CODE` environment variable (secret) to change the instructor code (default `northstar`).
Live-experiment submissions are stored in `northstar_experiments.db` next to the app. On Streamlit
Community Cloud that file is reset when the app restarts, so download the CSVs after each class.

## Changing a case number

Edit `CASE` in `models.py`, then run `python test_models.py`. The test lists any slide number the change breaks.

## Before class

In the experiments page, open Instructor results and choose "Demo data (preview only)" to rehearse the
debrief with a synthetic class. Between sections, use "Start a new class session" to archive results.
