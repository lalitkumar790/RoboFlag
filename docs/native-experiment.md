# Native Flagsmith experiment setup

Use a separate multivariate flag fleet_navigation_experiment, enabled, control value control, keyed treatment value congestion_aware (key adaptive). Connect the managed warehouse in Environment Settings > Warehouse. Create a mean numeric metric fleet_completion_rate (higher is better), optionally mean fleet_mean_duration (lower is better) and occurrence fleet_all_missions_completed. Create an experiment with equal allocation, full enrollment, and start it. The flag is locked while running.

Each fleet, not individual interacting robots, is a randomized unit. Each receives a unique identity; all its robots use its assigned controller. Seeds are specified before evaluation. Completion fraction is computed from the actual simulation, not synthetic conversions. No guardrail changes the assigned controller mid-experiment. Keep fault-injection demos separate.

Run python -m roboflag.experiment --fleets 4 --robots 12
Inspect exposures and outcomes in Flagsmith before running a larger batch. SDK calls do not prove ingestion; verify warehouse results. Do not run repeated batches with overlapping seeds for confirmatory analysis. The offline paired benchmark is separate. Guardrail decisions are exploratory recommendations only and never mutate remote state.
