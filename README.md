# RoboFlag — FeatureOps for Physical AI

Experiment before you deploy. Measure before you scale.

RoboFlag uses native Flagsmith experiments to evaluate robot fleet navigation policies in a seeded grid warehouse simulator. Whole fleets are randomized to avoid within-fleet interference.

## Confirmatory experiment #442

200 unique fleets, 12 robots each, seeds 2000–2199. Primary endpoint: every robot completes its mission.

| Outcome | Control A* | Congestion-aware A* |
|---|---:|---:|
| Native exposures | 88 | 112 |
| Native complete-fleet conversions | 2 | 88 |
| Complete fleet success | 2.27% | 78.57% |
| Individual mission completion | 662/1056 | 1312/1344 |
| Blocked proposals per fleet | 433.00 | 36.29 |

Primary absolute lift: 76.30 percentage points. Independent two-sided Fisher exact p = 2.0681e-31; exact binomial allocation p = 0.103639. Native inference was null at capture. Counts are native API aggregates reconciled with local terminal outcomes, not synthetic conversions. See [API snapshot](roboflag/experiment_442.json). Experiment status at capture: running; no further traffic planned.

## Reproduce

Python 3.10+:
```sh
pip install -r requirements.txt
python -m pytest -q
python -m roboflag.benchmark --seeds 20 --robots 12
python -m roboflag.validation
python -m roboflag.export_dashboard
python -m http.server 8000 --directory dashboard
```

[Mission Control deployment](https://roboflag.vercel.app) — static simulator traces, native snapshot and offline rollout rehearsal. Signed-out access must be checked before submission. See [experiment procedure](docs/native-experiment.md). Never commit credentials or rerun the confirmatory seeds against the same experiment.

## Evidence and limits

480 exploratory missions plus 1,680 density-validation missions and 2,400 confirmatory missions. Offline staged rollout rehearsal includes injected acceptance failure and a rollback recommendation, not a remote mutation. The grid simulator uses conservative movement arbitration; blocked proposals are not physical collisions. No hardware safety claim; high-density complete-fleet reliability remains limited. Native inference unavailable at capture. Browser and Python tests run in CI.
