from roboflag.fleet import simulate, scenario
from roboflag.benchmark import benchmark

def test_reproducible():
    assert simulate(7,6)==simulate(7,6)

def test_no_vertex_or_swap_conflicts():
    result=simulate(4,12,"congestion_aware")
    initial=[start for start,goal in scenario(4,12)[3]]
    previous=initial
    for frame in result["trace"]:
        positions=[tuple(p) for p in frame["positions"]]
        assert len(set(positions))==12
        assert not set(positions)&set(result["walls"])
        assert not set(positions)&set(frame["obstacles"])
        for i,p in enumerate(positions):
            assert p==previous[i] or p not in previous
        previous=positions

def test_identity_resolution():
    calls=[]
    def resolve(identity):
        calls.append(identity)
        return "congestion_aware","test"
    r=simulate(2,4,resolve=resolve)
    assert len(set(calls))==4
    assert all(m["strategy"]=="congestion_aware" and m["source"]=="test" for m in r["missions"])

def test_benchmark_counts():
    r=benchmark(2,4)
    assert all(v["missions"]==8 and 0<=v["success_rate"]<=1 for v in r.values())
