import pytest
pytest.importorskip("mujoco")
from roboflag.physics_crossing import crossing_trial,cart_y

def test_cart_schedule_is_fixed():
    assert cart_y(0)==6.5
    assert cart_y(3)==8
    assert cart_y(6)==9.5
    assert cart_y(15)==9.5

def test_protected_crossing():
    r=crossing_trial(True)
    assert r["success"],{k:v for k,v in r.items() if k!="trace"}
    assert r["external_contact_episodes"]==0
    assert 4.29<=r["wait_s"]<=4.31
    assert r["arrival_s"]<15
