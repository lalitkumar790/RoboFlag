"""Export genuine simulator traces for a static, offline dashboard."""
import argparse
import json
from pathlib import Path
from .fleet import simulate
from .benchmark import benchmark
from .rollout import rehearse

def build(seeds=(0,1,2,3,4,5), count=12):
    return {"kind":"offline_simulation","robot_count":count,
            "replays":[{"seed":seed,"arms":{s:simulate(seed,count,s) for s in ("astar","congestion_aware")}} for seed in seeds],
            "benchmark":benchmark(20,count),
            "rollouts":{"normal":rehearse(),"fault":rehearse(inject_fault=True)}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="dashboard/data.json")
    args=p.parse_args()
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(build(),separators=(",",":")),encoding="utf-8")

if __name__=="__main__":
    main()
