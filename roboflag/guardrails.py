"""Conservative local recommendation; no remote mutation or safety certification."""
def decide(control, treatment, min_fleets=20, max_regression=.05):
    if not control or not treatment:
        return "HOLD"
    if any(not 0<=v<=1 for v in [*control,*treatment]):
        raise ValueError("completion rates must lie in [0,1]")
    if len(control)<min_fleets or len(treatment)<min_fleets:
        return "HOLD"
    gap=sum(treatment)/len(treatment)-sum(control)/len(control)
    return "ROLLBACK_RECOMMENDED" if gap < -max_regression else "HOLD_FOR_STATISTICAL_REVIEW"
