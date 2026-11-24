"""Dynamic fleet development: known periodic cart trajectory, conservative lane reservation."""
import argparse
import json
import math
from collections import Counter
import mujoco
import numpy as np
from .fleet import scenario
from .navigation import plan
from .physics_planner import plan_physics
from .physics import model_xml,pose,drive,contact_pairs,DT
from .physics_tracking import command

# Cart travels along the gap between two integer columns, avoiding integer cell centers.
# At x=6.5, y in [1,10], it crosses horizontal robot edges between columns 6 and 7.
# Reserve these edges for the entire upcoming 12-second barrier using its swept interval.
def cart_y(t):
    q=(t*.5)%18.
    return 1.+min(q,18.-q)

def swept_interval(t,duration=12.):
    end=t+duration
    values=[cart_y(t),cart_y(end)]
    for k in range(math.floor(t/18.)+1,math.floor(end/18.)+1):
        values.append(cart_y(k*18.))
    return min(values),max(values)

def edge_allowed(a,b,interval):
    lo,hi=interval
    if {a[0],b[0]}=={6,7} and a[1]==b[1]:
        return not lo-.65<=a[1]<=hi+.65
    return True

def build(seed,count):
    xml=model_xml(seed,count).replace("</worldbody>",'<body name="fleet_cart" mocap="true" pos="6.5 1 .20"><geom name="fleet_cart_geom" type="box" size=".16 .16 .18"/></body></worldbody>')
    m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    return m,d

def simulate(seed,count,strategy,deadline=300.):
    if strategy not in ("congestion_aware","progress_aware"):raise ValueError(strategy)
    width,height,walls,missions,_=scenario(seed,count)
    m,d=build(seed,count)
    mocap=int(m.body("fleet_cart").mocapid[0])
    cells=[a for a,b in missions];goals=[b for a,b in missions]
    histories=[[a] for a in cells];completed=[None]*count
    waits=0;gate_rejections=0;episodes=0;cart_episodes=0;previous=set();work=0.;tick=0
    tracking_failure=None;trace=[];deadline_reached=False
    limit=round(deadline/DT)
    while round(d.time/DT)<limit and not all(t is not None for t in completed):
        tick+=1
        occupied=set(cells);reserved=set();targets=list(cells)
        interval=swept_interval(float(d.time))
        congestion=Counter()
        for x,y in cells:
            for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):congestion[x+dx,y+dy]+=2
        for j in range(count):
            i=(tick-1+j)%count
            if completed[i] is not None:continue
            if strategy=="progress_aware":
                route=plan_physics(cells[i],goals[i],width,height,walls,congestion,occupied|reserved,pose(m,d,i)[2],Counter(histories[i][:-1]))
            else:
                route=plan(cells[i],goals[i],width,height,walls,congestion)
            if len(route)>1 and route[1] not in occupied|reserved:
                if edge_allowed(cells[i],route[1],interval):
                    targets[i]=route[1];reserved.add(route[1]);continue
                gate_rejections+=1
            waits+=1
        settled=[0]*count
        for sub in range(2400):
            if round(d.time/DT)>=limit:
                deadline_reached=True;break
            d.mocap_pos[mocap]=[6.5,cart_y(float(d.time)+DT),.20]
            for i,target in enumerate(targets):
                v,w=command(pose(m,d,i),target);drive(m,d,i,v,w)
            mujoco.mj_step(m,d);mujoco.mj_forward(m,d)
            pairs=contact_pairs(m,d);new=pairs-previous;previous=pairs
            episodes+=len(new);cart_episodes+=sum("fleet_cart_geom" in p for p in new)
            work+=float(np.sum(np.abs(d.actuator_force*d.actuator_velocity)))*DT
            if not np.isfinite(d.qpos).all():raise RuntimeError("Nonfinite state")
            if sub%40==0:trace.append({"time_s":float(d.time),"poses":[pose(m,d,i) for i in range(count)],"cart":[6.5,cart_y(float(d.time))]})
            for i,target in enumerate(targets):
                actual=pose(m,d,i)
                settled[i]=settled[i]+1 if math.hypot(actual[0]-target[0],actual[1]-target[1])<=.05 and command(actual,target)==(0.,0.) else 0
            if min(settled)>=40:break
        else:
            tracking_failure=tick;break
        if deadline_reached:break
        for i,target in enumerate(targets):
            if target!=cells[i]:histories[i].append(target)
            cells[i]=target
            if completed[i] is None and target==goals[i]:completed[i]=float(d.time)
    return {"seed":seed,"robots":count,"strategy":strategy,"deadline_s":deadline,"simulated_seconds":float(d.time),"successes":sum(t is not None for t in completed),"mission_completion_seconds":completed,"external_contact_episodes":episodes,"cart_contact_episodes":cart_episodes,"tracking_failure":tracking_failure,"gate_rejections":gate_rejections,"waits":waits,"work_proxy_j":work,"reversals":sum(sum(p[j]==p[j-2] for j in range(2,len(p))) for p in histories),"trace":trace}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--robots",type=int,default=6);p.add_argument("--seed",type=int,default=4600)
    a=p.parse_args()
    print(json.dumps([simulate(a.seed,a.robots,s) for s in ("congestion_aware","progress_aware")]))
