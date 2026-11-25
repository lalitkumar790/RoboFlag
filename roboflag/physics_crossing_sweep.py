"""Prespecified timing sweep; both arms share each cart schedule."""
import json
from .physics_crossing import crossing_trial
PHASES=(-2.,-1.,0.,.5,1.,1.5,2.,2.5,3.,4.)
def sweep():
    return [crossing_trial(protected,phase) for phase in PHASES for protected in (False,True)]
if __name__=="__main__":
    print(json.dumps(sweep()))
