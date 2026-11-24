from roboflag.navigation import plan

def test_baseline():
    assert len(plan((0,2),(7,2),8,5)) == 8

def test_congestion():
    traffic = {(x,2):5 for x in range(1,7)}
    route = plan((0,2),(7,2),8,5,congestion=traffic)
    assert len(route) == 10
    assert not set(route).intersection(traffic)

def test_unreachable():
    assert plan((0,0),(2,0),3,1,walls={(1,0)}) == []

def test_same_cell():
    assert plan((0,0),(0,0),1,1) == [(0,0)]
