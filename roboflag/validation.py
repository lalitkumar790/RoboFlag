"""Prespecified additional seed sweep, separate from native experiment seeds."""
import json
from statistics import mean
from .fleet import simulate,scenario

SEEDS=tuple(range(200,220))
COUNTS=(6,12,24)
def validate_trace(run,seed,count):
    w,h,walls,missions,_=scenario(seed,count)
    prev=[s for s,_ in missions]
    for frame in run["trace"]:
        pos=[tuple(p) for p in frame["positions"]]
        blocked={tuple(p) for p in frame["obstacles"]}
        assert len(pos)==count==len(set(pos))
        assert all(0<=x<w and 0<=y<h and (x,y) not in walls|blocked for x,y in pos)
        assert all(abs(a[0]-b[0])+abs(a[1]-b[1])<=1 for a,b in zip(prev,pos))
        assert all(a==b or b not in prev for a,b in zip(prev,pos))
        prev=pos
    assert run["trace"][-1]["completed"]==sum(m["success"] for m in run["missions"])

def sweep(seeds=SEEDS,counts=COUNTS):
    result=[]
    for count in counts:
        arms={}
        for strategy in ("astar","congestion_aware"):
            runs=[]
            for seed in seeds:
                run=simulate(seed,count,strategy)
                validate_trace(run,seed,count)
                runs.append(run)
            missions=[m for r in runs for m in r["missions"]]
            arms[strategy]={"fleets":len(runs),"missions":len(missions),"completion_rate":mean(m["success"] for m in missions),
                "all_completed_rate":mean(all(m["success"] for m in r["missions"]) for r in runs),
                "capped_duration":mean(m["duration"] for m in missions),"blocked_proposals":sum(r["prevented_conflicts"] for r in runs)}
        result.append({"robots":count,"arms":arms})
    return {"kind":"additional_offline_validation","seeds":list(seeds),"results":result}
if __name__=="__main__":
    print(json.dumps(sweep(),indent=2))
