import json
from pathlib import Path
from roboflag.reconcile import reconcile

def test_numeric_archive():
    root=Path(__file__).resolve().parents[1]
    d=json.loads((root/"roboflag/experiment_445.json").read_text())
    rows=[json.loads(s) for s in (root/"evidence/experiment_445_fleets.jsonl").read_text().splitlines()]
    assert len(rows)==len({r["identity"] for r in rows})==200
    assert sorted(r["seed"] for r in rows)==list(range(3000,3200))
    local={}
    for arm in ("control","adaptive"):
        group=[r for r in rows if r["variant"]==arm]
        assert all(r["experiment_id"]==445 and r["missions"]==12 and r["completion_rate"]==r["successes"]/12 for r in group)
        local[arm]={"n":len(group),"sum":sum(r["completion_rate"] for r in group),"sum_squares":sum(r["completion_rate"]**2 for r in group)}
        for key,field in (("missions","missions"),("successes","successes"),("blocked","prevented_conflicts")):
            assert sum(r[field] for r in group)==d["local"][arm][key]
    inference=reconcile(local,{"results":d["native"]})["adaptive"]
    assert inference["chance_to_win"]==1 and inference["ci_low"]>0
