"""Native experiment: randomize whole fleets to avoid cross-arm interference."""
import argparse
import json
import os
import logging
from uuid import uuid4
from pathlib import Path
from .fleet import simulate

FLAG = "fleet_navigation_experiment"
MODES = {"control":"astar","astar":"astar","congestion_aware":"congestion_aware"}

def run(client, seed, count, identity, experiment_id=440):
    flag = client.get_experiment_flag(FLAG, identifier=identity)
    if not flag.enabled or flag.value not in MODES:
        raise RuntimeError("Experiment flag disabled or invalid")
    if not flag.experiment or not flag.experiment.in_experiment or not flag.variant:
        raise RuntimeError("Identity not enrolled in keyed experiment")
    if flag.experiment.id != experiment_id:
        raise RuntimeError("Unexpected experiment ID")
    strategy = MODES[flag.value]
    result = simulate(seed,count,strategy)
    successes = sum(m["success"] for m in result["missions"])
    rate = successes/count
    client.track_event("fleet_completion_rate", identifier=identity, value=rate)
    client.track_event("fleet_mean_duration", identifier=identity,
                       value=sum(m["duration"] for m in result["missions"])/count)
    if successes==count:
        client.track_event("fleet_all_missions_completed", identifier=identity, value=1)
    return {"experiment_id":experiment_id,"identity":identity,"seed":seed,"strategy":strategy,"variant":flag.variant,
            "successes":successes,"missions":count,"completion_rate":rate,
            "prevented_conflicts":result["prevented_conflicts"],
            "delivery":"sdk_called_not_confirmed"}

class DeliveryWarnings(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())

    def check(self):
        if self.messages:
            raise RuntimeError("SDK delivery warning; stop batch and reconcile: " + "; ".join(self.messages))

def run_batch(client, fleets, count, seed_start, emit=print, delivery_warnings=None, experiment_id=440, reserve=None):
    batch=uuid4().hex
    try:
        for i in range(fleets):
            identity=f"roboflag-{batch}-{i}"
            try:
                if reserve:
                    reserve(seed_start+i, identity)
                result=run(client,seed_start+i,count,identity,experiment_id)
                client.flush_events()
                if delivery_warnings:
                    delivery_warnings.check()
                emit(json.dumps(result))
            except Exception:
                logging.exception("Fleet submission failed: identity=%s seed=%s; delivery may be partial", identity, seed_start+i)
                raise
    finally:
        client.close(timeout_seconds=30)
    if delivery_warnings:
        delivery_warnings.check()

class Ledger:
    """Exclusive per-seed reservation; never silently retry uncertain delivery."""
    def __init__(self, root, experiment_id):
        self.root=Path(root)/str(experiment_id)
        self.root.mkdir(parents=True,exist_ok=True)
        self.experiment_id=experiment_id

    def reserve(self, seed, identity):
        with (self.root/f"{seed}.jsonl").open("x",encoding="utf-8") as f:
            f.write(json.dumps({"state":"reserved","experiment_id":self.experiment_id,"seed":seed,"identity":identity})+"\n")

    def record(self, line):
        row=json.loads(line)
        with (self.root/f"{row['seed']}.jsonl").open("a",encoding="utf-8") as f:
            f.write(line+"\n")
        print(line,flush=True)

def valid_protocol(experiment_id, robots, seed_start, fleets):
    return experiment_id == 445 and robots == 12 and 1 <= fleets <= 200 and 3000 <= seed_start <= seed_start+fleets-1 <= 3199

def main():
    from dotenv import load_dotenv
    from flagsmith import Flagsmith, EventProcessorConfig
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    delivery_warnings = DeliveryWarnings()
    sdk_logger = logging.getLogger("flagsmith.analytics")
    sdk_logger.addHandler(delivery_warnings)
    p=argparse.ArgumentParser()
    p.add_argument("--fleets",type=int,default=4)
    p.add_argument("--robots",type=int,default=12)
    p.add_argument("--seed-start",type=int,default=1010)
    p.add_argument("--experiment-id",type=int,required=True)
    p.add_argument("--ledger-dir",default="experiment-ledger")
    a=p.parse_args()
    if not 1<=a.fleets<=200 or not 1<=a.robots<=99:
        p.error("fleets 1..200; robots 1..99")
    if not valid_protocol(a.experiment_id,a.robots,a.seed_start,a.fleets):
        p.error("Active protocol requires experiment 445, 12 robots and seeds 3000–3199")
    ledger=Ledger(a.ledger_dir,a.experiment_id)
    if any((ledger.root/f"{seed}.jsonl").exists() for seed in range(a.seed_start,a.seed_start+a.fleets)):
        p.error("Seed already reserved; reconcile before proceeding")
    client=Flagsmith(environment_key=os.environ["FLAGSMITH_ENVIRONMENT_KEY"],
                     enable_events=True,event_processor_config=EventProcessorConfig(max_buffer_items=1000))
    try:
        run_batch(client,a.fleets,a.robots,a.seed_start,emit=ledger.record, delivery_warnings=delivery_warnings, experiment_id=a.experiment_id, reserve=ledger.reserve)
    finally:
        sdk_logger.removeHandler(delivery_warnings)

if __name__=="__main__":
    main()
