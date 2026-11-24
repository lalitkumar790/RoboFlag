from roboflag.rollout import cohort, rehearse, STAGES

def test_nested_cohorts():
    for i in range(100):
        identity=f"robot-{i:03d}"
        assignments=[cohort(identity,s) for s in (0,*STAGES)]
        assert assignments==sorted(assignments)
        assert not assignments[0] and assignments[-1]

def test_rehearsal_accounting():
    r=rehearse(seeds=(20,),count=12)
    assert not r["remote_flags_modified"]
    for stage in r["history"]:
        assert stage["missions"]==12
        assert stage["injected_losses"]==0
        assert stage["effective_success_rate"]==stage["raw_successes"]/12
    if r["history"][-1]["decision"]=="ROLLBACK":
        assert r["final_candidate_percentage"]==0

def test_fault_injection_accounting():
    r=rehearse(seeds=(20,),count=12,inject_fault=True,regression_limit=0)
    for stage in r["history"]:
        assert 0<=stage["injected_losses"]<=stage["assigned"]
        assert stage["effective_success_rate"]==(stage["raw_successes"]-stage["injected_losses"])/12
    assert not r["remote_flags_modified"]
