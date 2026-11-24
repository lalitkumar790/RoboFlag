# Confirmatory experiment evidence

The JSONL archive contains the 200 simulated fleet outcomes emitted by the native SDK runner in the two prespecified batches. Source: original PowerShell execution log, extracted as JSON records; no rows generated or imputed. Identities are synthetic fleet UUIDs, not people. The SDK delivery field remains unchanged; aggregate reconciliation is not proof of individual event receipts.

Run python -m pytest -q to verify the archive against roboflag/experiment_442.json. No credentials or live traffic are needed. Native inference was null; independent exact tests are in tests/test_experiment_snapshot.py.

# Submission draft

RoboFlag — FeatureOps for Physical AI

Robotic software updates can introduce fleet congestion even when individual navigation algorithms appear correct. RoboFlag uses Flagsmith to randomize entire simulated warehouse fleets between conventional and congestion-aware A*, track complete fleet success, and compare release outcomes before scaling. In experiment 442, native Flagsmith aggregates report 2/88 successful control fleets and 88/112 successful adaptive fleets: +76.30 percentage points across 2,400 simulated missions. The independent Fisher exact test supports the observed difference. Offline staged rollout rehearsal demonstrates a rollback recommendation under deliberately injected acceptance failures. Hardware validation and live rollback automation are outside the demonstrated scope.

Demo: https://roboflag.vercel.app
Source: https://github.com/lalitkumar790/RoboFlag
