from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from roboflag.experiment import run, FLAG
from roboflag.guardrails import decide

def client(enrolled=True):
    c=Mock()
    c.get_experiment_flag.return_value=SimpleNamespace(enabled=True,value="congestion_aware",variant="adaptive",
        experiment=SimpleNamespace(id=440,in_experiment=enrolled))
    return c

def test_native_attribution():
    c=client()
    r=run(c,7,4,"fleet-123")
    c.get_experiment_flag.assert_called_once_with(FLAG,identifier="fleet-123")
    c.track_exposure_event.assert_not_called()
    c.track_event.assert_any_call("fleet_completion_rate",identifier="fleet-123",value=r["successes"]/4)
    assert r["strategy"]=="congestion_aware"
    assert c.method_calls[0].__str__().startswith("call.get_experiment_flag")

def test_unenrolled_rejected():
    c=client(False)
    with pytest.raises(RuntimeError):
        run(c,7,4,"fleet-123")
    c.track_event.assert_not_called()
    c.track_exposure_event.assert_not_called()

def test_guardrails():
    assert decide([1]*20,[.8]*20)=="ROLLBACK_RECOMMENDED"
    assert decide([1],[0])=="HOLD"
    assert decide([.8]*20,[1]*20)=="HOLD_FOR_STATISTICAL_REVIEW"

def test_batch_closes_and_uses_unique_identities():
    import json
    from roboflag.experiment import run_batch
    c=client()
    lines=[]
    run_batch(c,2,4,1000,emit=lines.append)
    c.close.assert_called_once_with(timeout_seconds=30)
    rows=[json.loads(line) for line in lines]
    assert len({r["identity"] for r in rows})==2
    assert [r["seed"] for r in rows]==[1000,1001]
    assert c.flush_events.call_count==2
    assert c.method_calls[-1].__str__()=="call.close(timeout_seconds=30)"

def test_batch_closes_on_submission_failure():
    from roboflag.experiment import run_batch
    c=client()
    c.track_event.side_effect=RuntimeError("submission failure")
    with pytest.raises(RuntimeError,match="submission failure"):
        run_batch(c,2,4,1000,emit=lambda _: None)
    c.close.assert_called_once_with(timeout_seconds=30)
    c.get_experiment_flag.assert_called_once()

def test_delivery_warning_aborts_batch():
    import logging
    from roboflag.experiment import run_batch, DeliveryWarnings
    c=client()
    warnings=DeliveryWarnings()
    c.flush_events.side_effect=lambda: warnings.emit(logging.LogRecord("flagsmith.analytics",logging.WARNING,"",0,"Event buffer was full: dropped the 14 oldest events",(),None))
    with pytest.raises(RuntimeError,match="SDK delivery warning"):
        run_batch(c,4,4,1010,delivery_warnings=warnings)
    c.get_experiment_flag.assert_called_once()
    c.close.assert_called_once_with(timeout_seconds=30)

def test_real_sdk_buffer_and_flush(monkeypatch):
    import json
    from flagsmith import Flagsmith, EventProcessorConfig
    from flagsmith.models import Flag, ExperimentMetadata
    from flagsmith.analytics import EventProcessor
    payloads=[]
    def post(self,payload):
        payloads.extend(json.loads(payload)["events"])
        return SimpleNamespace(status_code=202)
    monkeypatch.setattr(EventProcessor,"_post",post)
    sdk=Flagsmith(environment_key="test-key",enable_events=True,event_processor_config=EventProcessorConfig(max_buffer_items=1000))
    flag=Flag(enabled=True,value="congestion_aware",feature_id=303042,feature_name=FLAG,variant="adaptive",experiment=ExperimentMetadata(id=440,name="test",in_experiment=True))
    monkeypatch.setattr(sdk,"get_identity_flags",lambda *a,**k:SimpleNamespace(get_flag=lambda _:flag))
    from roboflag.experiment import run_batch
    run_batch(sdk,4,1,1010,emit=lambda _:None)
    exposures=[p for p in payloads if p["event"]=="$flag_exposure"]
    assert len(exposures)==4
    assert len({p["identifier"] for p in exposures})==4
    assert all(p["metadata"]["experiment_id"]==440 for p in exposures)
    assert len([p for p in payloads if p["event"]=="fleet_completion_rate"])==4
    assert len([p for p in payloads if p["event"]=="fleet_mean_duration"])==4

def test_confirmatory_id_and_mismatch():
    c=client()
    c.get_experiment_flag.return_value.experiment.id=442
    assert run(c,2000,4,"new",experiment_id=442)["experiment_id"]==442
    c.reset_mock()
    with pytest.raises(RuntimeError,match="Unexpected experiment ID"):
        run(c,2001,4,"wrong",experiment_id=440)
    c.track_event.assert_not_called()

def test_ledger_refuses_reused_seed(tmp_path):
    from roboflag.experiment import Ledger
    ledger=Ledger(tmp_path,442)
    ledger.reserve(2000,"first")
    with pytest.raises(FileExistsError):
        ledger.reserve(2000,"second")
    ledger.record('{"seed":2000,"identity":"first","experiment_id":442}')
    assert len((tmp_path/"442"/"2000.jsonl").read_text().splitlines())==2

def test_followup_protocol():
    from roboflag.experiment import valid_protocol
    assert valid_protocol(445,12,3000,100)
    assert valid_protocol(445,12,3100,100)
    assert not valid_protocol(442,12,2000,100)
    assert not valid_protocol(445,12,3199,2)
    assert not valid_protocol(445,11,3000,100)
    assert not valid_protocol(445,12,3000,0)

def test_followup_numeric_event():
    c=client()
    c.get_experiment_flag.return_value.experiment.id=445
    row=run(c,3000,12,"followup",experiment_id=445)
    assert row["experiment_id"]==445
    c.track_event.assert_any_call("fleet_completion_rate",identifier="followup",value=row["successes"]/12)
