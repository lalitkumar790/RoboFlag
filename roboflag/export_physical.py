"""Generate browser replay from native MuJoCo, never synthetic paths."""
import json
from pathlib import Path
from .physics_dynamic_fleet import simulate
from .fleet import scenario

def main():
    target=Path("dashboard/physical-data")
    target.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for count,seed in [(6,4700),(12,4700),(24,4700)]:
        w,h,walls,missions,_=scenario(seed,count)
        arms={}
        for mode in ("congestion_aware","progress_aware"):
            r=simulate(seed,count,mode)
            frames=r.pop("trace")
            # Preserve measured planar pose and heading; 3D chassis height is nominal.
            r["trace"]=[{"time_s":round(f["time_s"],4),"poses":[[round(v,5) for v in p] for p in f["poses"]],"cart":[round(v,5) for v in f["cart"]]} for f in frames]
            arms[mode]=r
        name=f"fleet-{count}.json"
        (target/name).write_text(json.dumps({"seed":seed,"width":w,"height":h,"walls":sorted(walls),"missions":missions,"arms":arms},separators=(",",":")))
        manifest.append({"robots":count,"seed":seed,"file":name})
    (target/"manifest.json").write_text(json.dumps({"kind":"native_mujoco_pose_replay","scenarios":manifest}))

if __name__=="__main__":
    main()
