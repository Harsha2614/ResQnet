import json
from heapq import heappush, heappop

GRID_W = 32
GRID_H = 32

def in_bounds(x, y): return 0 <= x < GRID_W and 0 <= y < GRID_H

def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal, blocked):
    if start == goal: return [start]
    if start in blocked or goal in blocked: return []
    frontier = []
    heappush(frontier, (0, start))
    came = {start: None}
    cost = {start: 0}
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    while frontier:
        _, cur = heappop(frontier)
        if cur == goal: break
        for dx, dy in moves:
            nx, ny = cur[0]+dx, cur[1]+dy
            nxt = (nx, ny)
            if not in_bounds(nx, ny) or nxt in blocked: continue
            nc = cost[cur] + 1
            if nxt not in cost or nc < cost[nxt]:
                cost[nxt] = nc
                heappush(frontier, (nc + manhattan(nxt, goal), nxt))
                came[nxt] = cur
    if goal not in came: return []
    # reconstruct
    path = []
    c = goal
    while c is not None:
        path.append(c)
        c = came[c]
    path.reverse()
    return path

def path_to_instructions(path):
    if not path or len(path) < 2:
        return ""
    mapping = {(0,-1): "North", (0,1): "South", (1,0): "East", (-1,0): "West"}
    out_dirs = []
    prev = path[0]
    for cur in path[1:]:
        dx, dy = cur[0]-prev[0], cur[1]-prev[1]
        out_dirs.append(mapping.get((dx,dy), "?"))
        prev = cur
    # compress consecutive runs into counts
    phrases = []
    last = out_dirs[0]; cnt = 1
    for d in out_dirs[1:]:
        if d == last:
            cnt += 1
        else:
            phrases.append(f"Move {cnt} step{'s' if cnt!=1 else ''} towards {last}")
            last, cnt = d, 1
    phrases.append(f"Move {cnt} step{'s' if cnt!=1 else ''} towards {last}")
    # Join with commas and 'then'
    if len(phrases) == 1:
        return phrases[0]
    return ", then ".join(phrases)

def path_json(path): return json.dumps(path)
