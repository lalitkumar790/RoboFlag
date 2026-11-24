"""Paired seeds; separate homogeneous fleets avoid cross-arm interference."""
import argparse
import json
from statistics import mean
from .fleet import simulate

def benchmark(seeds=20,count=12):
    report = {}
    for strategy in ("astar","congestion_aware"):
        runs = [simulate(seed,count,strategy) for seed in range(seeds)]
        missions = [m for r in runs for m in r["missions"]]
        report[strategy] = {"missions":len(missions),"success_rate":mean(m["success"] for m in missions),
                            "mean_duration_capped_ticks":mean(m["duration"] for m in missions),
                            "mean_steps":mean(m["steps"] for m in missions),
                            "mean_waits":mean(m["waits"] for m in missions),
                            "prevented_conflicts":sum(r["prevented_conflicts"] for r in runs),
                            "per_seed":[{"seed":r["seed"],"successes":sum(m["success"] for m in r["missions"])} for r in runs]}
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seeds",type=int,default=20)
    p.add_argument("--robots",type=int,default=12)
    p.add_argument("--live",action="store_true")
    a=p.parse_args()
    if a.seeds < 1:
        p.error("seeds must be positive")
    if a.live:
        from .config import resolve
        print(json.dumps(simulate(count=a.robots,resolve=resolve)))
    else:
        print(json.dumps(benchmark(a.seeds,a.robots),indent=2))
