import pytest
pytest.importorskip("mujoco")
from roboflag.physics import build,smoke

def test_native_model():
    m,d=build(4000,6)
    assert m.nu==12
    assert m.nq==54
    assert d.time==0

def test_wheel_actuation_and_braking():
    r=smoke()
    assert r["finite"]
    assert .10<r["forward_displacement"]<.65
    assert r["lateral_drift"]<.08
    assert r["braking_displacement"]<.15
    assert not r["external_contact_pairs"]
