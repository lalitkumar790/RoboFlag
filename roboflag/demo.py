import json
from .config import resolve
from .navigation import plan

def main():
    strategy, source = resolve("robot-demo-001")
    traffic = {(x,2): 5 for x in range(1,7)}
    path = plan((0,2),(7,2),8,5,congestion=traffic if strategy=="congestion_aware" else {})
    print(json.dumps({"strategy":strategy,"source":source,"path":path,"steps":max(0,len(path)-1),"congestion_cost":sum(traffic.get(p,0) for p in path[1:])},indent=2))

if __name__ == "__main__":
    main()
