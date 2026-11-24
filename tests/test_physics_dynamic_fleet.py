import pytest
pytest.importorskip("mujoco")
from roboflag.physics_dynamic_fleet import cart_y,swept_interval,edge_allowed,build

def test_sweep_covers_turning_point():
    assert swept_interval(16,4)==(9.,10.)
    assert swept_interval(34,4)==(1.,2.)
    for t in range(72):
        lo,hi=swept_interval(t)
        assert all(lo-1e-9<=cart_y(t+k/10)<=hi+1e-9 for k in range(121))

def test_crossing_gate():
    assert not edge_allowed((6,5),(7,5),(3,6))
    assert edge_allowed((6,9),(7,9),(3,6))
    assert edge_allowed((6,5),(6,6),(3,6))

def test_model_build():
    m,d=build(4600,6)
    assert m.nmocap==1
    assert m.geom("fleet_cart_geom").id>=0


def test_cycle_penalty_is_conditional():
    from roboflag.physics_dynamic_fleet import cycle_penalty
    assert cycle_penalty([(0,0),(1,0)])==0
    assert cycle_penalty([(0,0),(1,0),(0,0)])==3
    assert cycle_penalty([(0,0),(1,0),(0,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,2)])==0
