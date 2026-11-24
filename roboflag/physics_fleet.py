"""Paired physical fleet development benchmark, static racks, no remote events."""
import argparse
import json
import math
from collections import Counter
import mujoco
import numpy as np
from .fleet import scenario
from .navigation import plan
from .physics_planner import plan_physics
from .physics import build, pose, drive, contact_pairs, DT
from .physics_tracking import command

def simulate_physics(seed=4100,count=6,strategy="astar",horizon=100):
    if strategy not in ("astar","congestion_aware","physics_aware"):
        raise ValueError("Unknown planner")
    width,height,walls,missions,_=scenario(seed,count)
    m,d=build(seed,count)
    cells=[s for s,g in missions]
    goals=[g for s,g in missions]
    histories=[[s] for s in cells]
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
            if strategy=="physics_aware":
                route=plan_physics(cells[i],goals[i],width,height,walls,congestion,occupied|reserved,pose(m,d,i)[2])
            else:
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
            if target!=cells[i]:histories[i].append(target)
            cells[i]=target
            if completed[i] is None and cells[i]==goals[i]:completed[i]=float(d.time)
        if all(t is not None for t in completed):break
    diagnostics=[]
    for i,path in enumerate(histories):
        distances=[abs(x-goals[i][0])+abs(y-goals[i][1]) for x,y in path]
        diagnostics.append({"moves":len(path)-1,"revisits":len(path)-len(set(path)),"immediate_reversals":sum(path[j]==path[j-2] for j in range(2,len(path))),"nonprogress_moves":sum(b>=a for a,b in zip(distances,distances[1:])),"initial_manhattan":distances[0],"final_manhattan":distances[-1],"path":path})
    return {"progress_diagnostics":diagnostics,"seed":seed,"robots":count,"strategy":strategy,"engine":mujoco.__version__,"static_obstacles_only":True,"successes":sum(t is not None for t in completed),"completion_rate":sum(t is not None for t in completed)/count,"mission_completion_seconds":completed,"simulated_seconds":float(d.time),"blocked_proposals":blocked,"external_contact_episodes":episodes,"actuator_work_proxy_j":work,"tracking_failure":tracking_failure,"steps":steps,"waits":waits,"trace":trace}

def benchmark(seeds=(4100,4101,4102),count=6,horizon=100,modes=("astar","congestion_aware")):
    return [simulate_physics(seed,count,mode,horizon) for seed in seeds for mode in modes]

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--robots",type=int,default=6)
    p.add_argument("--seeds",type=int,nargs="+",default=[4100,4101,4102])
    p.add_argument("--horizon",type=int,default=100)
    p.add_argument("--modes",nargs="+",choices=["astar","congestion_aware","physics_aware"],default=["astar","congestion_aware"])
    a=p.parse_args()
    print(json.dumps(benchmark(a.seeds,a.robots,a.horizon,a.modes)))
