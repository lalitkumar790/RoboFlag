from roboflag.export_dashboard import build
def test_export_matches_real_simulation():
    d=build(seeds=(3,),count=4)
    assert d["kind"]=="offline_simulation"
    arms=d["replays"][0]["arms"]
    for arm in arms.values():
        assert arm["seed"]==3
        assert arm["trace"][-1]["completed"]==sum(m["success"] for m in arm["missions"])
    assert arms["astar"]["walls"]==arms["congestion_aware"]["walls"]
