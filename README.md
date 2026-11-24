# RoboFlag — FeatureOps for Physical AI

A hackathon research prototype for controlled experiments and progressive deployment of robotic navigation behaviours using Flagsmith.

## Current milestone
Identity-based feature evaluation selects conventional A* or congestion-aware A* at mission start. A deterministic grid demonstration reports the route and congestion cost. This is not yet a fleet simulator or a physical safety system.

## Run locally
Python 3.10+:
```sh
pip install -r requirements.txt
python -m pytest
python -m roboflag.demo
```
Copy .env.example to .env and set FLAGSMITH_ENVIRONMENT_KEY locally. Never commit credentials. In Flagsmith create enabled feature navigation_strategy with value astar or congestion_aware. The demo uses identity robot-demo-001. Missing, disabled or invalid configuration selects the baseline; source is reported explicitly.

## Roadmap
- Multi-robot simulation and reproducible mission metrics
- Native Flagsmith experiment exposure and outcome reporting
- Guardrail evaluation and rollback with audit history
- Interactive mission control and deployment

No empirical fleet results or hardware safety claims are made yet.

## Mission Control dashboard
Run `python -m roboflag.export_dashboard` then `python -m http.server 8000 --directory dashboard`. Open http://localhost:8000. The dashboard replays actual simulation traces and shows offline rollout audits. Vercel configuration builds the static dashboard from the same Python engine. Public deployment is not yet verified.
