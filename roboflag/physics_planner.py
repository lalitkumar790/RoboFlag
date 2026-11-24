"""Exploratory heading-aware A*: distance, congestion and turning proxy."""
import math
from heapq import heappop, heappush

DIRECTIONS=((1,0),(0,1),(-1,0),(0,-1))

def plan_physics(start,goal,width,height,walls,congestion,occupied,yaw):
    walls=set(walls)
    occupied=set(occupied)-{start}
    heading=int(round(yaw/(math.pi/2)))%4
    initial=(start,heading)
    def heuristic(p):
        return abs(p[0]-goal[0])+abs(p[1]-goal[1])
    if start in walls or goal in walls:return []
    costs={initial:0.}
    parents={}
    queue=[(heuristic(start),0.,initial)]
    while queue:
        _,cost,state=heappop(queue)
        if cost!=costs[state]:continue
        p,h=state
        if p==goal:
            path=[p]
            while state in parents:
                state=parents[state];path.append(state[0])
            return path[::-1]
        for k,(dx,dy) in enumerate(DIRECTIONS):
            q=(p[0]+dx,p[1]+dy)
            if not (0<=q[0]<width and 0<=q[1]<height) or q in walls:continue
            if state==initial and q in occupied:continue
            turns=min((k-h)%4,(h-k)%4)
            # Provisional dimensionless weights, not calibrated energy estimates.
            new=cost+1+0.35*congestion.get(q,0)+0.6*turns
            nxt=(q,k)
            if new<costs.get(nxt,float("inf")):
                costs[nxt]=new;parents[nxt]=state
                heappush(queue,(new+heuristic(q),new,nxt))
    return []
