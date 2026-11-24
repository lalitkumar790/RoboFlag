# RoboFlag submission handoff

## Project
RoboFlag — FeatureOps for Physical AI (AlphaBot)
Track: native experimentation.

## Review links
- Demo: https://roboflag.vercel.app
- Source: https://github.com/lalitkumar790/RoboFlag
- Validated engineering checkpoint: https://github.com/lalitkumar790/RoboFlag/commit/184921319f834d98408e5a7739b404fe73bc7fb0
- Passing CI: https://github.com/lalitkumar790/RoboFlag/actions/runs/45486003657
- Native aggregate snapshot: ../roboflag/experiment_442.json
- Original 200 fleet outcomes: ../evidence/experiment_442_fleets.jsonl
- Demo storyboard: demo.md

## Submission description
RoboFlag enables controlled software experiments for simulated autonomous warehouse fleets. Native Flagsmith identity assignment selects conventional A* or congestion-aware A* for entire fleets, and the SDK reports measured outcomes. In experiment 442, 2 of 88 control fleets and 88 of 112 adaptive fleets completed all 12 missions, a 76.30 percentage-point difference across 2,400 simulated robot missions. Independent exact tests support the observed improvement. An interactive replay dashboard, offline staged rollout rehearsal and injected-failure rollback recommendation demonstrate the engineering workflow.

## Evidence boundary
The 4,560 mission total includes 2,160 offline benchmark and 2,400 native experiment missions; rollout rehearsal is separate. Experiment 442 completed with control retained, not adaptive deployed. Native inference and SRM are null; independent tests are not Flagsmith inference. The captured aggregate remains is_final=false. No physical hardware validation or actual remote rollback is claimed.

## Reviewer reproduction (no credentials)
pip install -r requirements.txt
python -m pytest -q
python -m roboflag.export_dashboard
python -m http.server 8000 --directory dashboard

Do not execute the native runner again against completed experiment 442.

## Human submission checklist
- [ ] Open production URL signed out; if blocked, authorize a narrowly scoped public-access change or provide a reviewer-accessible demo.
- [ ] Record the actual dashboard and native experiment (hide credentials and account details).
- [ ] Include the actual control rollout decision and simulation limitations.
- [ ] Verify current hackathon submission rules, eligibility, and timing on the organizer portal before submitting.
- [ ] Submit the entry and confirm receipt.

Authenticated production HTTP checks succeeded. Anonymous access, video recording, organizer requirements and submission receipt are not verified. No entry has been submitted by this document.
