"""Native experiment: randomize whole fleets to avoid cross-arm interference."""
import argparse
import json
import os
import logging
from uuid import uuid4
from .fleet import simulate

FLAG = "fleet_navigation_experiment"
MODES = {"control":"astar","astar":"astar","congestion_aware":"congestion_aware"}

def run(client, seed, count, identity):
    flag = client.get_experiment_flag(FLAG, identifier=identity)
    if not flag.enabled or flag.value not in MODES:
        raise RuntimeError("Experiment flag disabled or invalid")
    if not flag.experiment or not flag.experiment.in_experiment or not flag.variant:
        raise RuntimeError("Identity not enrolled in keyed experiment")
    if flag.experiment.id != 440:
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
    return {"identity":identity,"seed":seed,"strategy":strategy,"variant":flag.variant,
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

def run_batch(client, fleets, count, seed_start, emit=print, delivery_warnings=None):
    batch=uuid4().hex
    try:
        for i in range(fleets):
            identity=f"roboflag-{batch}-{i}"
            try:
                result=run(client,seed_start+i,count,identity)
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
    a=p.parse_args()
    if not 1<=a.fleets<=200 or not 1<=a.robots<=99:
        p.error("fleets 1..200; robots 1..99")
    client=Flagsmith(environment_key=os.environ["FLAGSMITH_ENVIRONMENT_KEY"],
                     enable_events=True,event_processor_config=EventProcessorConfig(max_buffer_items=1000))
    try:
        run_batch(client,a.fleets,a.robots,a.seed_start,emit=lambda line: print(line,flush=True), delivery_warnings=delivery_warnings)
    finally:
        sdk_logger.removeHandler(delivery_warnings)

if __name__=="__main__":
    main()
