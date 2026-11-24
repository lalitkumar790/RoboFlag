from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from roboflag.experiment import run, FLAG
from roboflag.guardrails import decide

def client(enrolled=True):
    c=Mock()
    f=c.get_identity_flags.return_value
    f.is_feature_enabled.return_value=True
    f.get_flag.return_value=SimpleNamespace(value="congestion_aware",variant="adaptive",
        experiment=SimpleNamespace(in_experiment=enrolled))
    return c

def test_native_attribution():
    c=client()
    r=run(c,7,4,"fleet-123")
    c.track_exposure_event.assert_called_once_with(FLAG,identifier="fleet-123",value="adaptive")
    c.track_event.assert_any_call("fleet_completion_rate",identifier="fleet-123",value=r["successes"]/4)
    assert r["strategy"]=="congestion_aware"
    assert c.method_calls[1].__str__().startswith("call.track_exposure_event")

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
    c.close.assert_called_once_with()
    rows=[json.loads(line) for line in lines]
    assert len({r["identity"] for r in rows})==2
    assert [r["seed"] for r in rows]==[1000,1001]
    assert c.method_calls[-1].__str__()=="call.close()"

def test_batch_closes_on_submission_failure():
    from roboflag.experiment import run_batch
    c=client()
    c.track_event.side_effect=RuntimeError("submission failure")
    with pytest.raises(RuntimeError,match="submission failure"):
        run_batch(c,2,4,1000,emit=lambda _: None)
    c.close.assert_called_once_with()
    c.track_exposure_event.assert_called_once()
