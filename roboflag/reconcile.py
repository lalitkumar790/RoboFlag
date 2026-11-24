"""Offline audit of numeric experiment 445. Never sends events."""
import argparse
import json
import math
from pathlib import Path

def aggregate(root, expected):
    rows=[]
    for path in Path(root).glob("*.jsonl"):
        lines=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if len(lines)!=2:
            raise ValueError(f"Incomplete ledger: {path}")
        reservation,row=lines
        if reservation.get("state")!="reserved" or any(reservation[k]!=row[k] for k in ("seed","identity","experiment_id")):
            raise ValueError(f"Reservation mismatch: {path}")
        if row["experiment_id"]!=445 or row["missions"]!=12 or not 0<=row["successes"]<=12 or not math.isclose(row["completion_rate"],row["successes"]/12):
            raise ValueError(f"Invalid outcome: {path}")
        if {"control":"astar","adaptive":"congestion_aware"}.get(row["variant"])!=row["strategy"]:
            raise ValueError(f"Invalid assignment: {path}")
        rows.append(row)
    if len(rows)!=expected or len({r["identity"] for r in rows})!=expected or sorted(r["seed"] for r in rows)!=list(range(3000,3000+expected)):
        raise ValueError("Incomplete or duplicate fleet cohort")
    result={}
    for arm in ("control","adaptive"):
        group=[r for r in rows if r["variant"]==arm]
        values=[r["completion_rate"] for r in group]
        result[arm]={"n":len(group),"sum":math.fsum(values),"sum_squares":math.fsum(v*v for v in values),"missions":sum(r["missions"] for r in group),"successes":sum(r["successes"] for r in group),"blocked":sum(r["prevented_conflicts"] for r in group)}
    return result

def reconcile(local, remote):
    metrics=remote["results"]["payload"]["metrics"]
    metric=next(m for m in metrics if m["metric_id"]==405)
    for arm,stats in local.items():
        native=metric["variants"][arm]
        if native["n"]!=stats["n"] or any(not math.isclose(native[k],stats[k],rel_tol=1e-8,abs_tol=1e-8) for k in ("sum","sum_squares")):
            raise ValueError(f"Native aggregate mismatch: {arm}")
    return metric["inference"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger",default="experiment-ledger/445")
    p.add_argument("--expected",type=int,choices=[100,200],required=True)
    p.add_argument("--native-json")
    a=p.parse_args()
    local=aggregate(a.ledger,a.expected)
    print(json.dumps(local,indent=2))
    if a.native_json:
        print(json.dumps({"reconciled":True,"native_inference":reconcile(local,json.loads(Path(a.native_json).read_text(encoding="utf-8-sig")))},indent=2))

if __name__=="__main__":
    main()
