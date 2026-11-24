"""Paired physical fleet development benchmark, static racks, no remote events."""
import argparse
import json
import math
from collections import Counter
import mujoco
import numpy as np
from .fleet import scenario
from .navigation import plan
from .physics import build, pose, drive, contact_pairs, DT
from .physics_tracking import command

def simulate_physics(seed=4100,count=6,strategy="astar",horizon=100):
    if strategy not in ("astar","congestion_aware"):
        raise ValueError("Unknown planner")
    width,height,walls,missions,_=scenario(seed,count)
    m,d=build(seed,count)
    cells=[s for s,g in missions]
    goals=[g for s,g in missions]
    completed=[None]*count
    waits=[0]*count
    steps=[0]*count
    blocked=0;episodes=0;previous=set();work=0.;trace=[]
    tracking_failure=None
    for tick in range(1,horizon+1):
        occupied=set(cells)
        if len(occupied)!=count:raise RuntimeError("Duplicate reserved cell")
        congestion=Counter()
        for x,y in cells:
            for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
                congestion[x+dx,y+dy]+=2
        reserved=set()
        targets=list(cells)
        for i in [(tick-1+j)%count for j in range(count)]:
            if completed[i] is not None:continue
            route=plan(cells[i],goals[i],width,height,walls,congestion if strategy=="congestion_aware" else {})
            if len(route)>1 and route[1] not in occupied and route[1] not in reserved:
                targets[i]=route[1];reserved.add(route[1])
            else:
                waits[i]+=1
                blocked+=int(len(route)>1)
        # Synchronous reservation barrier: do not release cells until the whole fleet settles.
        settled=[0]*count
        for sub in range(2400):
            for i,target in enumerate(targets):
                v,w=command(pose(m,d,i),target)
                drive(m,d,i,v,w)
            mujoco.mj_step(m,d)
            contacts=contact_pairs(m,d)
            episodes+=len(contacts-previous);previous=contacts
            work+=float(np.sum(np.abs(d.actuator_force*d.actuator_velocity)))*DT
            if not np.isfinite(d.qpos).all():raise RuntimeError("Nonfinite physics state")
            if sub%40==0:
                trace.append({"time_s":float(d.time),"poses":[list(pose(m,d,i)) for i in range(count)]})
            for i,target in enumerate(targets):
                actual=pose(m,d,i)
                error=math.hypot(actual[0]-target[0],actual[1]-target[1])
                settled[i]=settled[i]+1 if error<=.05 and command(actual,target)==(0.,0.) else 0
            if min(settled)>=40:break
        else:
            tracking_failure={"tick":tick,"targets":targets,"poses":[pose(m,d,i) for i in range(count)]}
            break
        for i,target in enumerate(targets):
            steps[i]+=int(target!=cells[i])
            cells[i]=target
            if completed[i] is None and cells[i]==goals[i]:completed[i]=float(d.time)
        if all(t is not None for t in completed):break
    return {"seed":seed,"robots":count,"strategy":strategy,"engine":mujoco.__version__,"static_obstacles_only":True,"successes":sum(t is not None for t in completed),"completion_rate":sum(t is not None for t in completed)/count,"mission_completion_seconds":completed,"simulated_seconds":float(d.time),"blocked_proposals":blocked,"external_contact_episodes":episodes,"actuator_work_proxy_j":work,"tracking_failure":tracking_failure,"steps":steps,"waits":waits,"trace":trace}

def benchmark(seeds=(4100,4101,4102),count=6,horizon=100):
    return [simulate_physics(seed,count,mode,horizon) for seed in seeds for mode in ("astar","congestion_aware")]

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--robots",type=int,default=6)
    p.add_argument("--seeds",type=int,nargs="+",default=[4100,4101,4102])
    p.add_argument("--horizon",type=int,default=100)
    a=p.parse_args()
    print(json.dumps(benchmark(a.seeds,a.robots,a.horizon)))
