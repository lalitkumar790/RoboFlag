# Rollout rehearsal

Run python -m roboflag.rollout and python -m roboflag.rollout --fault.
Nested deterministic identity cohorts progress through 10/25/50/100 percent. Small fleets may not exactly match target percentages. Each stage reruns the same mission seeds; this is an exploratory paired rehearsal, not an independent randomized trial. The guardrail is a five percentage point drop in mission completion relative to baseline. A rollback resets the candidate allocation to zero and stops subsequent stages.

Fault mode models a failed downstream mission acceptance check for successful candidate missions. Raw simulation outcomes are preserved and injected losses are recorded separately. This is a deliberately injected application-level failure, not a physical collision or a simulated controller defect.

The engine does not change Flagsmith, start experiment 440 or emit experiment events. A simulated advance is not a production promotion recommendation. Remote rollout control and authorization are separate future work.
