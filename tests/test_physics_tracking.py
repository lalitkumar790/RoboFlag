import pytest
pytest.importorskip("mujoco")
from roboflag.physics_tracking import tracking_trial,command

def test_heading_gate():
    assert command((0,0,0),(0,1))[0]==0
    assert command((0,0,0),(1,0))[0]>0

def test_native_square_tracking():
    r=tracking_trial()
    assert r["success"],r["waypoints"]
    assert r["external_contact_episodes"]==0
    assert max(p["error_m"] for p in r["waypoints"])<=.05
