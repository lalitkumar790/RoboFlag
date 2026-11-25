import pytest
pytest.importorskip("mujoco")
from roboflag.physics_crossing_sweep import sweep,PHASES
def test_sweep():
    rows=sweep()
    assert len(rows)==2*len(PHASES)
    assert all(r["success"] and r["external_contact_episodes"]==0 for r in rows if r["protected"])
    assert any(r["external_contact_episodes"]>0 for r in rows if not r["protected"]), "Sweep did not exercise collision hazard"
