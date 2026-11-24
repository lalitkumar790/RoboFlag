# Experiment protocol

Offline paired benchmark: identical seeds, starting positions, goals and attempted dynamic obstacle schedules in independent homogeneous fleets. The obstacle generator excludes occupied cells at runtime, so realized obstacles may differ by controller. The experimental planner penalizes cells near current robots. Both arms share the same conservative movement arbitration. Completed robots remain parked; congestion, waits and deadlocks are possible.

Primary metric: fraction reaching goal within 100 ticks. Secondary: capped duration (including failures), steps, waits and prevented movement conflicts. No energy or physical collision claims. A tick is not a measured wall-clock duration. The conflict counter measures blocked proposals, not collisions.

Run: python -m roboflag.benchmark --seeds 20 --robots 12

Live identity mode: python -m roboflag.benchmark --live --robots 12

Live mode resolves flags once per mission per robot and records source. Offline benchmark is not a native Flagsmith experiment. Native exposure/outcome attribution and statistical inference remain future work. Treat seeds as experimental units, not individual correlated robots. Do not promote based on the exploratory benchmark alone.
