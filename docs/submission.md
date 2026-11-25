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

## Numeric follow-up #445
Prespecified fresh seeds 3000–3199; 200 fleets, 100 per arm, 2,400 simulated missions. Native metric 405 mean completion: 67.00% control vs 97.17% adaptive; native relative lift +45.02%, 95% credible interval +37.58% to +52.47%, reported chance to win 100%. Native SRM is null; observed allocation is balanced. Both numeric moments and counts reconcile with the archived original records. The reported probability is model output, not physical certainty. Experiment was running at snapshot; no further traffic planned. Combined offline and two native experiments: 6,960 missions.

## Physical research and interactive preview
The integration branch mission-control-3d adds six regenerated native MuJoCo runs (6/12/24 robots, seed 4700) and a synchronized browser replay. The preview is https://roboflag-e5jxeyg6z-lalitsikarwar2001-6516s-projects.vercel.app/physics.html (authenticated assets verified, latest release-decision panel, may require Vercel login). Local Chromium tests passed in run 45560797100 and original regression in run 45560797207. Reproduce with pip install -r requirements-physics.txt, python -m roboflag.export_physical_evidence, python -m roboflag.export_physical, and the existing dashboard commands.
- Static frozen physical holdout: V2 146/168, V4 168/168.
- Moving-cart frozen holdout: V2 148/168, V4 168/168.
- Frozen V6 deadline holdout: V4 303/324, V5b 301/324, V6 302/324, all zero external contact episodes and tracking failures. Source run 45509923670; all 54 summaries archived in evidence/physics_v6_holdout.json.
- Total research attempts 10,872 (6,960 grid plus 3,912 physical), including comparative reruns and repeated assignments; regenerated display traces excluded. Not independent robot-level samples.
- V3 livelock, V5 completion regression and mixed V5b/V6 results are reported, not hidden. V4 remains preferred. The local physical evidence gate compares completion and contacts against V4; a separate grid rollout rehearsal shows injected failure rollback. These are not new Flagsmith assignments or actual remote rollback.
- Known obstacle schedules, modeled friction and nominal geometry limit external validity. No hardware safety certification. Actuator work proxy is not battery energy. Browser renders measured planar pose and heading using approximate 3D geometry.
- Record a real screen demo, verify anonymous reviewer access, confirm experiment #445 status, and submit manually. No submission receipt or video exists yet.

## Final verification checkpoint — 25 November 2026
Read-only Flagsmith #445 verification: running, n=100 per arm, unchanged inference, no rollout decision, is_final=false. Do not claim winner deployed. The user must complete the experiment with an explicit rollout choice in Flagsmith if desired. No new exposures, production promotion or permission changes were performed. The verified preview is not yet verified anonymously. Video and submission receipt are outstanding.

## Final native rollout — 26 November 2026 IST
Experiment #445 completed; final results is_final=true. Adaptive selected (variant 36620); published Development version 9dd83a5e-0721-4c09-be15-8e5569058882 verified enabled, allocation 100%. Native inference unchanged. No physical or Production Flagsmith rollout claimed. Earlier running-status statements in this document describe historical checkpoints only.
