"""Prescribed-motion physical obstacle feasibility; no fleet/controller comparison."""
import json
import math
import mujoco
import numpy as np
from .physics import model_xml,pose,drive,contact_pairs,DT
from .fleet import scenario

def build_dynamic(seed=4000):
    width,height,walls,missions,_=scenario(seed,1)
    x,y=missions[0][0]
    if x+1>=width or (x+1,y) in walls:
        raise ValueError("Smoke scenario requires clear east neighbour")
    xml=model_xml(seed,1).replace("</worldbody>",f'<body name="moving_cart" mocap="true" pos="{x+1} {y} .20"><geom name="moving_cart_geom" type="box" size=".16 .16 .18" friction=".8 .005 .0001"/></body></worldbody>')
    m=mujoco.MjModel.from_xml_string(xml)
    d=mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    return m,d

def trial(positive_control=False):
    m,d=build_dynamic()
    start=pose(m,d,0)
    mocap=m.body("moving_cart").mocapid[0]
    if mocap<0:raise RuntimeError("Missing mocap body")
    # Fixed simulation-clock trajectory. Positive control intentionally contacts robot.
    initial_x=start[0]+1.
    travel=.80 if positive_control else .30
    episodes=0
    previous=set()
    observed=set()
    max_displacement=0.
    trace=[]
    for step in range(401):
        t=step*DT
        x=initial_x-travel*min(t/2.,1.)
        d.mocap_pos[mocap]=[x,start[1],.20]
        drive(m,d,0,0,0)
        mujoco.mj_step(m,d)
        # Refresh geometry/contact state at the integrated configuration.
        mujoco.mj_forward(m,d)
        contacts=contact_pairs(m,d)
        episodes+=len(contacts-previous)
        previous=contacts
        observed.update(contacts)
        actual=pose(m,d,0)
        max_displacement=max(max_displacement,math.hypot(actual[0]-start[0],actual[1]-start[1]))
        if step%20==0:
            trace.append({"time_s":float(d.time),"robot_pose":actual,"cart_position":d.xpos[m.body("moving_cart").id].tolist()})
        if not np.isfinite(d.qpos).all():
            raise RuntimeError("Nonfinite state")
    return {"positive_control":positive_control,"engine":mujoco.__version__,"commanded_cart_travel_m":travel,"measured_cart_travel_m":initial_x-float(d.xpos[m.body("moving_cart").id,0]),"external_contact_episodes":episodes,"contact_pairs":sorted(observed),"max_robot_displacement_m":max_displacement,"trace":trace}

if __name__=="__main__":
    print(json.dumps([trial(False),trial(True)],indent=2))
