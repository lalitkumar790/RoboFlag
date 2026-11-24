import pytest
from roboflag.reconcile import reconcile

def test_numeric_reconciliation():
    local={"control":{"n":88,"sum":55.0,"sum_squares":40.0},"adaptive":{"n":112,"sum":110.0,"sum_squares":109.0}}
    metric={"metric_id":405,"variants":{k:dict(v) for k,v in local.items()},"inference":{"adaptive":None}}
    remote={"results":{"payload":{"metrics":[metric]}}}
    assert reconcile(local,remote)=={"adaptive":None}
    metric["variants"]["control"]["sum_squares"]=41
    with pytest.raises(ValueError,match="mismatch"):
        reconcile(local,remote)
