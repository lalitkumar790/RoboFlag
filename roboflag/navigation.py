"""Deterministic four-connected grid planner."""
from heapq import heappop, heappush

def plan(start, goal, width, height, walls=(), congestion=None):
    blocked = set(walls)
    congestion = congestion or {}
    def valid(p):
        return 0 <= p[0] < width and 0 <= p[1] < height and p not in blocked
    if not valid(start) or not valid(goal):
        return []
    def h(p):
        return abs(p[0]-goal[0])+abs(p[1]-goal[1])
    queue = [(h(start), 0, start)]
    costs = {start: 0}
    parents = {}
    while queue:
        _, g, p = heappop(queue)
        if g != costs[p]:
            continue
        if p == goal:
            path = [p]
            while p in parents:
                p = parents[p]
                path.append(p)
            return path[::-1]
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            q = (p[0]+dx,p[1]+dy)
            if not valid(q):
                continue
            n = g + 1 + max(0, congestion.get(q,0))
            if n < costs.get(q,float("inf")):
                costs[q] = n
                parents[q] = p
                heappush(queue,(n+h(q),n,q))
    return []
