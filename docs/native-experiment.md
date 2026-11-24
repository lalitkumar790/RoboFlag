# Native Flagsmith experiment setup

Use a separate multivariate flag fleet_navigation_experiment, enabled, control value control, keyed treatment value congestion_aware (key adaptive). Connect the managed warehouse in Environment Settings > Warehouse. Create a mean numeric metric fleet_completion_rate (higher is better), optionally mean fleet_mean_duration (lower is better) and occurrence fleet_all_missions_completed. Create an experiment with equal allocation, full enrollment, and start it. The flag is locked while running.

Each fleet, not individual interacting robots, is a randomized unit. Each receives a unique identity; all its robots use its assigned controller. Seeds are specified before evaluation. Completion fraction is computed from the actual simulation, not synthetic conversions. No guardrail changes the assigned controller mid-experiment. Keep fault-injection demos separate.

Run python -m roboflag.experiment --fleets 4 --robots 12
Inspect exposures and outcomes in Flagsmith before running a larger batch. SDK calls do not prove ingestion; verify warehouse results. Do not run repeated batches with overlapping seeds for confirmatory analysis. The offline paired benchmark is separate. Guardrail decisions are exploratory recommendations only and never mutate remote state.

The runner explicitly closes the SDK in a finally block, including when a fleet fails. Output is a local submission record, not a warehouse receipt. A synchronous error aborts the batch; do not blindly retry a partially submitted batch. Check warehouse ingestion and experiment exposures separately.

## Pilot incident and correction
The first running pilot (seeds 1000–1003, batch 5f80e8b6ed744caabcdc9519d517fe22) completed 48/48 missions, all adaptive, but SDK reported 14 dropped events. Its native attribution may be incomplete; do not treat it as clean confirmatory data or replay its identities. Experiment 440 may retain partial pilot events. The corrected runner uses SDK 6.7.0, automatic exposure with experiment metadata, 1000-event buffer, per-fleet flush, 30-second close, and aborts on SDK delivery warnings. Flush is not a receipt. Retry pilot on seeds 1010–1013; verify native counts before scaling. For a clean confirmatory experiment consider a fresh experiment after pilot validation, with explicit approval, rather than silently pooling the contaminated pilot.
