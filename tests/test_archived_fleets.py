import json
from pathlib import Path

def test_archived_fleet_outcomes():
    root=Path(__file__).resolve().parents[1]
    rows=[json.loads(line) for line in (root/"evidence/experiment_442_fleets.jsonl").read_text().splitlines()]
    snapshot=json.loads((root/"roboflag/experiment_442.json").read_text())
    assert len(rows)==len({r["identity"] for r in rows})==200
    assert sorted(r["seed"] for r in rows)==list(range(2000,2200))
    for r in rows:
        assert r["experiment_id"]==442 and r["missions"]==12
        assert 0<=r["successes"]<=12
        assert r["strategy"]=={"control":"astar","adaptive":"congestion_aware"}[r["variant"]]
    for arm,l in snapshot["local"].items():
        group=[r for r in rows if r["variant"]==arm]
        assert len(group)==l["fleets"]
        assert sum(r["successes"]==12 for r in group)==l["full"]
        for field,key in [("missions","missions"),("successes","successes"),("prevented_conflicts","blocked")]:
            assert sum(r[field] for r in group)==l[key]
