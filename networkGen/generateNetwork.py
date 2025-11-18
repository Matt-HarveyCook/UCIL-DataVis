import sys
import json
import time
import linecache
from collections import defaultdict

execution_log = []
last_time = None
firstLine = None

def trace_func(frame, event, arg):
    global last_time
    global firstLine

    if event == "line":
        if not firstLine:
            firstLine = frame.f_lineno
        code = frame.f_code
        lineno = frame.f_lineno
        filename = code.co_filename
        line = linecache.getline(filename, lineno).strip()

        current_time = time.perf_counter()
        if last_time is not None:
            duration = current_time - last_time
        else:
            duration = 0

        execution_log.append({
            "file": filename,
            "line_no": lineno-firstLine,
            "code": line,
            "duration_since_last": duration,
        })
        last_time = current_time

    return trace_func


def run_with_trace(func, *args, **kwargs):
    """Run a function with line-level tracing."""
    sys.settrace(trace_func)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(None)
    return result

def calculateExecutionPercent(exec_log):
    lineToTime = defaultdict(int)
    totalTime = 0
    for log in exec_log:
        totalTime += log['duration_since_last']
        lineToTime[log['line_no']] += log['duration_since_last']
    for k in lineToTime:
        lineToTime[k] /= totalTime
    return lineToTime
    print(lineToTime)

def calculateExecutionCount(exec_log):
    lineToCount = defaultdict(int)
    totalCount = 0
    for log in exec_log:
        totalCount += 1
        lineToCount[log['line_no']] += 1
    for k in lineToCount:
        lineToCount[k] /= totalCount
    return lineToCount
    print(lineToCount)

def calculateConnections(exec_log):
    linePairCount = defaultdict(int)
    totalCount = 0
    for i in range(1, len(exec_log)):
        lineA = exec_log[i-1]['line_no']
        lineB = exec_log[i]['line_no']
        linePairCount[(lineA, lineB)] += 1
        totalCount += 1

    for k in linePairCount:
        linePairCount[k] /= totalCount

    return linePairCount
    print(linePairCount)

import numpy as np
def spreadOutPoints(execPercent, i):
    arr = []
    for k in execPercent:
        arr.append(execPercent[k])

    arr = np.array(arr)
    arr_norm = (arr - arr.min()) / (arr.max() - arr.min())

    return arr_norm[i]

# def percentToRgb(p):
#     res = {}
#     res['r'] = 255 * p
#     res['g'] = 255 * (1 - p)
#     res['b'] = 0
#     res['opacity'] = 1
#     return res

def percentToRgb(p):
    c1 = {}
    c1['r'] = 247 
    c1['g'] = 169
    c1['b'] = 168

    c2 = {}
    c2['r'] = 60 
    c2['g'] = 0 
    c2['b'] = 0

    return {
        'r': int(c1['r'] * (1 - p) + c2['r'] * p),
        'g': int(c1['g'] * (1 - p) + c2['g'] * p),
        'b': int(c1['b'] * (1 - p) + c2['b'] * p),
        'opacity': 1
    }

# def generateNodes(execPercent, execCount):
#     res = []
#     for lineNum in execPercent:
#         currNode = {}
#         currNode['id'] = str(lineNum)
#         currNode['size'] = 1000 * execCount[int(lineNum)]
#         currNode['color'] = percentToRgb(execPercent[lineNum])
#         res.append(currNode)
#     return res

def generateNodes(execPercent, execCount):
    res = []
    for i, lineNum in enumerate(execPercent):
        rgb = percentToRgb(spreadOutPoints(execPercent, i))
        currNode = {
            'id': str(lineNum),
            'line': int(lineNum),   # IMPORTANT for highlighting
            'size': 1000 * execCount[int(lineNum)],
            'color': f"rgba({rgb['r']},{rgb['g']},{rgb['b']},{rgb['opacity']})"
        }
        res.append(currNode)
    return res

def generateConnections(connections):
    res = []
    for pair in connections:
        currConnection = {}
        currConnection['source'] = str(pair[0])
        currConnection['target'] = str(pair[1])
        currConnection['length'] = 10000 * connections[pair]
        res.append(currConnection)
    return res



def displayNodes(nodes):
    for node in nodes:
        print(node, ',')
    print('')

def displayConnections(connections):
    for link in connections:
        print(link, ',')

def export_to_json(nodes, connections, filename="../d3/graph_data.json"):
    displayNodes(nodes)
    displayConnections(connections)
    data = {
        "nodes": nodes,
        "links": connections
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[OK] Exported graph data to {filename}")

# Example code to trace
def main():
    grid = [[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,0,0,0,0,0,0,1,1,0,0,0,0]]
    seen = set()
    ROW = len(grid)
    COL = len(grid[0])
    def dfs(r, c):
        if r < 0 or r >= ROW or c < 0 or c >= COL:
            return 0
        if grid[r][c] == 0:
            return 0
        if (r,c) in seen:
            return 0
        seen.add((r,c))
        up = dfs(r-1, c)
        down = dfs(r+1, c)
        left = dfs(r, c-1)
        right = dfs(r, c+1)
        return up + down + left + right + 1
    res = 0
    for r in range(ROW):
        for c in range(COL):
            res = max(res, dfs(r,c))
    return res



if __name__ == "__main__":
    run_with_trace(main)
    execPercent = calculateExecutionPercent(execution_log)
    execCount = calculateExecutionCount(execution_log)
    connectionDict = calculateConnections(execution_log)

    nodes = generateNodes(execPercent, execCount)
    connections = generateConnections(connectionDict)
    export_to_json(nodes, connections)



    # const nodes = [
    #   { id: "A", size: 10, color: "red" },
    #   { id: "B", size: 20, color: "blue" },
    #   { id: "C", size: 15, color: "green" },
    #   { id: "D", size: 25, color: "orange" }
    # ];

    # const links = [
    #   { source: "A", target: "B", length: 100 },
    #   { source: "A", target: "C", length: 150 },
    #   { source: "B", target: "D", length: 2000 },
    #   { source: "C", target: "D", length: 120 }
    # ];
