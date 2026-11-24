"""Seeded discrete-time warehouse simulation, not a physical model."""
from dataclasses import dataclass
from collections import Counter
from random import Random
from .navigation import plan

@dataclass
class Robot:
    identity: str
    position: tuple
    goal: tuple
    strategy: str
    steps: int = 0
    waits: int = 0
    completed_at: int | None = None

def scenario(seed, count=12):
    rng = Random(seed)
    width, height = 18, 12
    walls = {(x,y) for x in (4,8,12) for y in range(2,10) if y not in (5,6)}
    cells = [(x,y) for x in range(width) for y in range(height) if (x,y) not in walls]
    if not 1 <= count <= len(cells)//2:
        raise ValueError("invalid fleet size")
    picks = rng.sample(cells, count*2)
    obstacles = {tick: set(rng.sample(cells, 5)) for tick in range(1,101)}
    return width,height,walls,list(zip(picks[:count],picks[count:])),obstacles

def simulate(seed=1, count=12, strategy="astar", resolve=None, horizon=100):
    width,height,walls,missions,obstacles = scenario(seed,count)
    robots = []
    sources = {}
    for i,(start,goal) in enumerate(missions):
        identity = f"robot-{i:03d}"
        mode,source = resolve(identity) if resolve else (strategy,"benchmark")
        if mode not in ("astar","congestion_aware"):
            raise ValueError("unknown strategy")
        robots.append(Robot(identity,start,goal,mode))
        sources[identity] = source
    conflicts = 0
    trace = []
    for tick in range(1,horizon+1):
        occupied = {r.position for r in robots}
        assert len(occupied)==len(robots)
        blocked = obstacles.get(tick,set()) - occupied
        reserved = set()
        # Rotating priority reduces starvation; no move into a cell occupied
        # at the beginning of the tick (also prevents swaps).
        order = robots[(tick-1)%count:] + robots[:(tick-1)%count]
        congestion = Counter()
        for r in robots:
            for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
                congestion[(r.position[0]+dx,r.position[1]+dy)] += 2
        for r in order:
            if r.completed_at is not None:
                continue
            route = plan(r.position,r.goal,width,height,walls|blocked,
                         congestion if r.strategy=="congestion_aware" else {})
            if len(route)>1 and route[1] not in occupied and route[1] not in reserved:
                r.position = route[1]
                reserved.add(r.position)
                r.steps += 1
            else:
                r.waits += 1
                if len(route)>1 and (route[1] in occupied or route[1] in reserved):
                    conflicts += 1
            if r.position == r.goal:
                r.completed_at = tick
        assert len({r.position for r in robots})==count
        trace.append({"tick":tick,"positions":[list(r.position) for r in robots],
                      "obstacles":sorted(blocked),"completed":sum(r.completed_at is not None for r in robots)})
        if all(r.completed_at is not None for r in robots):
            break
    return {"seed":seed,"width":width,"height":height,"walls":sorted(walls),
            "missions":[{"identity":r.identity,"strategy":r.strategy,"source":sources[r.identity],
                         "success":r.completed_at is not None,"duration":r.completed_at or horizon,
                         "steps":r.steps,"waits":r.waits,"goal":r.goal} for r in robots],
            "prevented_conflicts":conflicts,"trace":trace}
