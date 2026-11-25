"""Native MuJoCo wheel-drive feasibility tests. No Flagsmith traffic."""
import argparse
import json
import math
from collections import Counter
import mujoco
import numpy as np
from .fleet import scenario

DT = .005
RADIUS = .08
TRACK = .36
MAX_WHEEL = 9.5

def model_xml(seed=4000,count=6):
    width,height,walls,missions,_=scenario(seed,count)
    pieces=['<mujoco model="RoboFlag physics"><compiler angle="radian"/><option timestep="0.005" integrator="implicitfast"/><worldbody><geom name="floor" type="plane" size="20 20 .1" friction="1 .005 .0001"/>']
    for x,y in sorted(walls):
        pieces.append(f'<geom name="rack_{x}_{y}" type="box" pos="{x} {y} .5" size=".49 .49 .5"/>')
    for name,x,y,sx,sy in [('west',-.55,5.5,.05,6.1),('east',17.55,5.5,.05,6.1),('south',8.5,-.55,9.1,.05),('north',8.5,11.55,9.1,.05)]:
        pieces.append(f'<geom name="{name}" type="box" pos="{x} {y} .3" size="{sx} {sy} .3"/>')
    for i,(start,goal) in enumerate(missions):
        x,y=start
        pieces.append(f'<body name="r{i}" pos="{x} {y} .08"><freejoint name="root{i}"/><geom name="chassis{i}" type="cylinder" size=".155 .045" pos="0 0 .035" mass="8.6"/>')
        for side,offset in [('l',.18),('r',-.18)]:
            pieces.append(f'<body name="wheel_{i}_{side}" pos="0 {offset} 0"><joint name="joint_{i}_{side}" type="hinge" axis="0 1 0" damping=".02"/><geom name="tire_{i}_{side}" type="cylinder" size=".08 .035" euler="1.57079632679 0 0" mass=".5" priority="1" friction="1.2 .005 .0001"/></body>')
        for end,offset in [('f',.115),('b',-.115)]:
            pieces.append(f'<geom name="caster_{i}_{end}" type="sphere" pos="{offset} 0 -.05" size=".03" mass=".2" priority="1" friction=".005 .001 .0001"/>')
        pieces.append('</body>')
    pieces.append('</worldbody><actuator>')
    for i in range(count):
        for side in ('l','r'):
            pieces.append(f'<velocity name="motor_{i}_{side}" joint="joint_{i}_{side}" kv="1.5" ctrlrange="-9.5 9.5" forcerange="-4 4"/>')
    pieces.append('</actuator></mujoco>')
    return ''.join(pieces)

def build(seed=4000,count=6):
    m=mujoco.MjModel.from_xml_string(model_xml(seed,count))
    d=mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    return m,d

def pose(m,d,i):
    body=m.body(f"r{i}").id
    x,y=d.xpos[body,:2]
    mat=d.xmat[body].reshape(3,3)
    return float(x),float(y),math.atan2(mat[1,0],mat[0,0])

def drive(m,d,i,v,w):
    for side,speed in [('l',(v-w*TRACK/2)/RADIUS),('r',(v+w*TRACK/2)/RADIUS)]:
        d.ctrl[m.actuator(f"motor_{i}_{side}").id]=np.clip(speed,-MAX_WHEEL,MAX_WHEEL)

def contact_pairs(m,d):
    """Count only distinct external robot contact pairs, excluding ground/self."""
    owners={}
    for i in range(m.nu//2):
        for name in [f"chassis{i}",f"tire_{i}_l",f"tire_{i}_r",f"caster_{i}_f",f"caster_{i}_b"]:
            owners[m.geom(name).id]=i
    pairs=set()
    for c in d.contact[:d.ncon]:
        a,b=int(c.geom1),int(c.geom2)
        if a==m.geom("floor").id or b==m.geom("floor").id: continue
        oa,ob=owners.get(a),owners.get(b)
        if oa is None and ob is None: continue
        if oa is not None and oa==ob: continue
        if c.dist<=0:
            pairs.add(tuple(sorted((f"robot:{oa}" if oa is not None else m.geom(a).name,f"robot:{ob}" if ob is not None else m.geom(b).name))))
    return pairs

def smoke():
    # Select a deterministic starting cell with a clear +x neighbour.
    for seed in range(4000,4100):
        w,h,walls,missions,_=scenario(seed,1)
        x,y=missions[0][0]
        if x+1<w and (x+1,y) not in walls: break
    m,d=build(seed,1)
    initial=pose(m,d,0)
    contacts=set()
    for _ in range(200):
        drive(m,d,0,.35,0)
        mujoco.mj_step(m,d)
        contacts.update(contact_pairs(m,d))
    moved=pose(m,d,0)
    diagnostics={"wheel_velocity":[float(d.qvel[m.jnt_dofadr[m.joint(f"joint_0_{side}").id]]) for side in ("l","r")],"motor_force":d.actuator_force.tolist(),"ground_contacts":[{"geoms":[m.geom(int(c.geom1)).name,m.geom(int(c.geom2)).name],"friction":c.friction.tolist()} for c in d.contact[:d.ncon] if m.geom("floor").id in (c.geom1,c.geom2)]}
    for _ in range(200):
        drive(m,d,0,0,0)
        mujoco.mj_step(m,d)
        contacts.update(contact_pairs(m,d))
    stopped=pose(m,d,0)
    result={"drive_diagnostics":diagnostics,"engine_version":mujoco.__version__,"seed":seed,"initial":initial,"after_drive":moved,"after_brake":stopped,"forward_displacement":moved[0]-initial[0],"lateral_drift":abs(moved[1]-initial[1]),"braking_displacement":math.hypot(stopped[0]-moved[0],stopped[1]-moved[1]),"external_contact_pairs":sorted(contacts),"finite":bool(np.isfinite(d.qpos).all()),"physics_seconds":float(d.time)}
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--smoke",action="store_true",required=True)
    p.parse_args()
    print(json.dumps(smoke(),indent=2))
