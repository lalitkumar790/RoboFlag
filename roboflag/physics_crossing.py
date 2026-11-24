"""Native prescribed moving cart crossing with a common conservative swept-envelope gate."""
import json
import math
import mujoco
import numpy as np
from .physics import model_xml,pose,drive,contact_pairs,DT
from .physics_tracking import command
from .fleet import scenario

# Seed 4000 places robot at (9,8), clear eastward route to (10,8).
# Cart moves north along x=9.5, then parks at y=9.5.
# Swept envelope across robot corridor is reserved until cart clears.
def cart_y(t):
    return 6.5+min(max(t,0.),6.)*.5

def build_crossing():
    _,_,walls,missions,_=scenario(4000,1)
    assert missions[0][0]==(9,8)
    assert (10,8) not in walls
    xml=model_xml(4000,1).replace("</worldbody>",'<body name="crossing_cart" mocap="true" pos="9.5 6.5 .20"><geom name="crossing_cart_geom" type="box" size=".16 .16 .18"/></body></worldbody>')
    m=mujoco.MjModel.from_xml_string(xml)
    d=mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    return m,d

def crossing_trial(protected=True):
    m,d=build_crossing()
    initial=pose(m,d,0)
    goal=(10.,8.)
    mocap=int(m.body("crossing_cart").mocapid[0])
    previous=set(); observed=set(); episodes=0;trace=[]
    wait_steps=0; arrival=None; settled=0; work=0.
    # Fixed 15-second clock for both arms. Observe the entire cart schedule.
    for k in range(3000):
        t=k*DT
        d.mocap_pos[mocap]=[9.5,cart_y(t),.20]
        # Reserve whole crossing corridor until cart is >=0.65 m beyond it.
        # Both chassis/wheel envelope and cart width fit within this buffer.
        hold=protected and cart_y(t)<8.65
        if hold:
            v,w=0.,0.
            wait_steps+=1
        else:
            v,w=command(pose(m,d,0),goal)
        drive(m,d,0,v,w)
        mujoco.mj_step(m,d)
        mujoco.mj_forward(m,d)
        pairs=contact_pairs(m,d)
        episodes+=len(pairs-previous);previous=pairs;observed.update(pairs)
        work+=float(np.sum(np.abs(d.actuator_force*d.actuator_velocity)))*DT
        x,y,yaw=pose(m,d,0)
        error=math.hypot(x-goal[0],y-goal[1])
        settled=settled+1 if error<=.05 and v==0 and w==0 and not hold else 0
        if settled>=40 and arrival is None:arrival=float(d.time)
        if k%20==0:trace.append({"time_s":float(d.time),"robot_pose":[x,y,yaw],"cart_position":d.xpos[m.body("crossing_cart").id].tolist(),"held":hold})
        if not np.isfinite(d.qpos).all():raise RuntimeError("Nonfinite state")
    return {"protected":protected,"engine":mujoco.__version__,"deadline_s":15.,"arrival_s":arrival,"success":arrival is not None and error<=.05 and episodes==0,"final_error_m":error,"wait_s":wait_steps*DT,"external_contact_episodes":episodes,"contact_pairs":sorted(observed),"work_proxy_j":work,"trace":trace}

if __name__=="__main__":
    print(json.dumps([crossing_trial(False),crossing_trial(True)],indent=2))
