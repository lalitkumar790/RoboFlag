"""Closed-loop wheel-driven waypoint feasibility; no state teleportation."""
import argparse
import json
import math
import mujoco
import numpy as np
from .physics import build, pose, drive, contact_pairs, DT

def angle_error(a,b):
    return math.atan2(math.sin(a-b),math.cos(a-b))

def command(current,target):
    x,y,yaw=current
    dx,dy=target[0]-x,target[1]-y
    distance=math.hypot(dx,dy)
    if distance<=.035:
        return 0.,0.
    error=angle_error(math.atan2(dy,dx),yaw)
    w=max(-1.5,min(1.5,3*error))
    v=min(.5,1.5*distance)*max(0.,math.cos(error)) if abs(error)<.25 else 0.
    return v,w

def tracking_trial():
    m,d=build(4000,1)
    start=pose(m,d,0)[:2]
    targets=[(start[0]+1,start[1]),(start[0]+1,start[1]+1),start]
    # Last diagonal intentionally replaced by a cardinal path, like A*.
    targets.insert(2,(start[0],start[1]+1))
    results=[];trace=[];episodes=0;previous=set();effort=0.
    for target in targets:
        reached=False;settled=0
        for step in range(2400):
            current=pose(m,d,0)
            v,w=command(current,target)
            drive(m,d,0,v,w)
            mujoco.mj_step(m,d)
            contacts=contact_pairs(m,d)
            episodes+=len(contacts-previous);previous=contacts
            effort+=float(np.sum(np.abs(d.actuator_force*d.actuator_velocity)))*DT
            if not np.isfinite(d.qpos).all():
                raise RuntimeError("Nonfinite physics state")
            actual=pose(m,d,0)
            error=math.hypot(actual[0]-target[0],actual[1]-target[1])
            if step%20==0:trace.append([float(d.time),*actual])
            settled=settled+1 if error<=.05 and v==0 and w==0 else 0
            if settled>=40:
                reached=True;break
        results.append({"target":target,"actual":actual,"error_m":error,"reached":reached,"time_s":float(d.time)})
        if not reached:break
    return {"engine":mujoco.__version__,"waypoints":results,"success":len(results)==len(targets) and all(r["reached"] for r in results),"external_contact_episodes":episodes,"actuator_work_proxy_j":effort,"trace":trace}

if __name__=="__main__":
    print(json.dumps(tracking_trial(),indent=2))
