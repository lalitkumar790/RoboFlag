from roboflag.physics_planner import plan_physics

def test_first_step_avoids_occupied():
    p=plan_physics((0,0),(2,0),3,3,set(),{}, {(1,0)},0)
    assert p[0]==(0,0) and p[1]==(0,1) and p[-1]==(2,0)

def test_heading_prefers_straight():
    p=plan_physics((0,0),(2,2),3,3,set(),{},set(),0)
    assert p==[(0,0),(1,0),(2,0),(2,1),(2,2)]

def test_no_route():
    assert plan_physics((0,0),(2,0),3,1,{(1,0)},{},set(),0)==[]


def test_progress_penalty_avoids_repeated_cell():
    p=plan_physics((0,0),(2,0),3,3,set(),{},set(),0, {(1,0):10})
    assert p[1]==(0,1) and p[-1]==(2,0)
