import pytest
pytest.importorskip("mujoco")
from roboflag.physics_fleet import simulate_physics

@pytest.mark.parametrize("mode",["astar","congestion_aware"])
def test_native_fleet_short_horizon(mode):
    r=simulate_physics(4100,6,mode,horizon=2)
    assert r["tracking_failure"] is None,r["tracking_failure"]
    assert r["external_contact_episodes"]==0
    assert r["simulated_seconds"]>0
    assert sum(r["steps"])>0
