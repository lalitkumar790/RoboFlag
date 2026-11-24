import json
from pathlib import Path
from math import comb, isclose

def test_native_snapshot_reconciliation():
    d=json.loads((Path(__file__).resolve().parents[1]/"roboflag"/"experiment_442.json").read_text())
    m=d["native"]["payload"]["metrics"][0]
    assert d["experiment_id"]==442 and m["metric_id"]==401
    assert sum(v["n"] for v in m["variants"].values())==200
    for arm,v in m["variants"].items():
        l=d["local"][arm]
        assert (v["n"],v["sum"])==(l["fleets"],l["full"])
        assert l["missions"]==12*l["fleets"]
    assert m["inference"]["adaptive"] is None
    assert d["native"]["last_error_at"] is None

def test_independent_exact_statistics():
    d=json.loads((Path(__file__).resolve().parents[1]/"roboflag"/"experiment_442.json").read_text())
    # Hypergeometric fixed-margin two-sided Fisher test.
    weights=[comb(90,k)*comb(110,88-k) for k in range(max(0,88-110),min(90,88)+1)]
    p=sum(w for w in weights if w<=weights[2])/comb(200,88)
    q=2*sum(comb(200,k) for k in range(89))/2**200
    assert isclose(p,d["independent"]["fisher_two_sided"],rel_tol=1e-10)
    assert isclose(q,d["independent"]["allocation_binomial_two_sided"],rel_tol=1e-10)
