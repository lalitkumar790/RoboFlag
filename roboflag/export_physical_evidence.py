"""Aggregate archived physical campaigns without MuJoCo dependencies."""
import json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    campaigns=[]
    for name,label in [
        ("physics_three_way_4300_4301","V3 development — livelock / unsuccessful experiments"),
        ("physics_static_holdout","Independent static physical holdout"),
        ("physics_dynamic_holdout","Independent moving-cart holdout"),
        ("physics_v5_development","V5 fixed reversal penalty — rejected"),
        ("physics_v5b_holdout","V5b independent validation — mixed efficiency"),
        ("physics_v6_development","V6 development — no incremental benefit over V5b"),
        ("physics_v6_diagnostics","V6 deadline stress — exploratory"),
        ("physics_v6_holdout","Frozen V6 deadline holdout — V4 remains preferred")]:
        d=json.loads((root/"evidence"/(name+".json")).read_text())
        arms=[]
        for mode in sorted({r["strategy"] for r in d["rows"]}):
            rs=[r for r in d["rows"] if r["strategy"]==mode]
            arms.append({"label":{"astar":"V1","congestion_aware":"V2","physics_aware":"V3","progress_aware":"V4","reversal_aware":"V5","cycle_aware":"V5b","deadline_aware":"V6"}[mode],"successes":sum(r["successes"] for r in rs),"missions":sum(r["robots"] for r in rs),"contacts":sum(r["external_contact_episodes"] for r in rs)})
        campaigns.append({"label":label,"arms":arms,"source":f"https://github.com/lalitkumar790/RoboFlag/actions/runs/{d['source_run']}"})
    (root/"dashboard"/"physical-evidence.json").write_text(json.dumps({"campaigns":campaigns},separators=(",",":")))

if __name__=="__main__":
    main()
