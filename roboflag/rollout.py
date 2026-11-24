"""Offline staged rollout rehearsal. Never mutates remote Flagsmith flags."""
import argparse
import hashlib
import json
from .fleet import simulate

STAGES=(10,25,50,100)
def cohort(identity, percentage):
    bucket=int.from_bytes(hashlib.sha256(identity.encode()).digest()[:8],"big")/2**64
    return bucket < percentage/100

def rehearse(seeds=(20,21,22,23), count=24, regression_limit=.05, inject_fault=False):
    if not seeds or not 0<=regression_limit<=1:
        raise ValueError("invalid rehearsal configuration")
    baseline=[simulate(seed,count,"astar") for seed in seeds]
    baseline_rate=sum(m["success"] for r in baseline for m in r["missions"])/(len(seeds)*count)
    history=[]
    active=0
    for stage in STAGES:
        runs=[]
        for seed in seeds:
            def resolve(identity):
                return ("congestion_aware" if cohort(identity,stage) else "astar","offline_rollout")
            runs.append(simulate(seed,count,resolve=resolve))
        missions=[m for r in runs for m in r["missions"]]
        assigned=sum(m["strategy"]=="congestion_aware" for m in missions)
        # Explicit fault injection: failed mission acceptance in candidate cohort.
        # Preserve original simulation outcomes and distinguish effective outcomes.
        raw_success=sum(m["success"] for m in missions)
        injected_losses=sum(m["success"] and m["strategy"]=="congestion_aware" for m in missions) if inject_fault else 0
        rate=(raw_success-injected_losses)/len(missions)
        regression=baseline_rate-rate
        decision="ROLLBACK" if regression>regression_limit else "ADVANCE_REHEARSAL"
        history.append({"stage_percent":stage,"assigned":assigned,"missions":len(missions),
                        "raw_successes":raw_success,"injected_losses":injected_losses,
                        "effective_success_rate":rate,"baseline_rate":baseline_rate,
                        "regression":regression,"decision":decision})
        if decision=="ROLLBACK":
            active=0
            break
        active=stage
    return {"kind":"offline_rollout_rehearsal","fault_injection":inject_fault,
            "baseline_rate":baseline_rate,"regression_limit":regression_limit,
            "seeds":list(seeds),"history":history,"final_candidate_percentage":active,
            "remote_flags_modified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fault",action="store_true")
    a=p.parse_args()
    print(json.dumps(rehearse(inject_fault=a.fault),indent=2))
if __name__=="__main__":
    main()
