"""Native experiment: randomize whole fleets to avoid cross-arm interference."""
import argparse
import json
import os
from uuid import uuid4
from .fleet import simulate

FLAG = "fleet_navigation_experiment"
MODES = {"control":"astar","astar":"astar","congestion_aware":"congestion_aware"}

def run(client, seed, count, identity):
    flags = client.get_identity_flags(identity)
    flag = flags.get_flag(FLAG)
    if not flags.is_feature_enabled(FLAG) or flag.value not in MODES:
        raise RuntimeError("Experiment flag disabled or invalid")
    if not flag.experiment or not flag.experiment.in_experiment or not flag.variant:
        raise RuntimeError("Identity not enrolled in keyed experiment")
    strategy = MODES[flag.value]
    client.track_exposure_event(FLAG, identifier=identity, value=flag.variant)
    result = simulate(seed,count,strategy)
    successes = sum(m["success"] for m in result["missions"])
    rate = successes/count
    client.track_event("fleet_completion_rate", identifier=identity, value=rate)
    client.track_event("fleet_mean_duration", identifier=identity,
                       value=sum(m["duration"] for m in result["missions"])/count)
    if successes==count:
        client.track_event("fleet_all_missions_completed", identifier=identity, value=1)
    return {"identity":identity,"seed":seed,"strategy":strategy,"variant":flag.variant,
            "successes":successes,"missions":count,"completion_rate":rate,
            "prevented_conflicts":result["prevented_conflicts"],
            "delivery":"sdk_called_not_confirmed"}

def main():
    from dotenv import load_dotenv
    from flagsmith import Flagsmith, EventProcessorConfig
    load_dotenv()
    p=argparse.ArgumentParser()
    p.add_argument("--fleets",type=int,default=4)
    p.add_argument("--robots",type=int,default=12)
    p.add_argument("--seed-start",type=int,default=1000)
    a=p.parse_args()
    if not 1<=a.fleets<=200 or not 1<=a.robots<=99:
        p.error("fleets 1..200; robots 1..99")
    client=Flagsmith(environment_key=os.environ["FLAGSMITH_ENVIRONMENT_KEY"],
                     enable_events=True,event_processor_config=EventProcessorConfig(max_buffer_items=1))
    batch=uuid4().hex
    for i in range(a.fleets):
        print(json.dumps(run(client,a.seed_start+i,a.robots,f"roboflag-{batch}-{i}")),flush=True)

if __name__=="__main__":
    main()
