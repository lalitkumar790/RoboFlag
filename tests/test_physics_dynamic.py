import pytest
pytest.importorskip("mujoco")
from roboflag.physics_dynamic import trial

def test_prescribed_cart_motion_without_contact():
    r=trial(False)
    assert r["measured_cart_travel_m"]==pytest.approx(.30,abs=1e-6)
    assert r["external_contact_episodes"]==0
    assert r["max_robot_displacement_m"]<.05

def test_positive_control_detects_cart_contact():
    r=trial(True)
    assert r["measured_cart_travel_m"]==pytest.approx(.80,abs=1e-6)
    assert r["external_contact_episodes"]>=1
    assert ["moving_cart_geom","robot:0"] in [list(p) for p in r["contact_pairs"]]
