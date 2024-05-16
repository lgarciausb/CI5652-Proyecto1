import time
import datetime
import rustworkx as rx
from os import walk

from .MIS_exact import MIS_exact
from .MIS_heuristic import MIS_heuristic
from .MIS_local_search import MIS_local_search

import signal


class TimeoutException(Exception):   # Custom exception class
    pass


def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException


signal.signal(signal.SIGALRM, timeout_handler)


def timer(func, *args):
    start = time.time()
    result = func(*args)
    duration = time.time() - start
    return result, duration

def timeout(graph, time, funcName, func, *args):
    signal.alarm(time)
    try:
        res, duration = timer(func, *args)
    except TimeoutException:
        print("---- {funcName} -> Max Time ({time} s) Exceeded".format(funcName = funcName, time = time))
        return set(), time
    else:
        # Reset the alarm
        signal.alarm(0)
        print_test_result(funcName, res, is_MIS(
            graph, res), duration)
        
        return res, duration


# funcion que recibe un grafo G y un conjunto S de indices de nodos y determina si
# S es un conjunto independiente maximal


def is_MIS(G, S):
    for node in G.node_indices():
        if node not in S and not any((neighbor in S) for neighbor in G.neighbors(node)):
            return False
    return True

# funcion que recibe dos enteros n y e, y retorna un Grafo
# con n nodos y e lados


def randomGraph(n, e):
    G = rx.PyGraph()
    for i in range(n):
        G.add_node(0)
    for i in range(e):
        G.add_edge(randint(0, n-1), randint(0, n-1), None)

    return G


def load_graph(filename):
    G = rx.PyGraph()

    with open(filename) as f:
        for _line in f:
            line = _line.rstrip()
            tokens = line.split()

            if tokens[0] == "p":
                G.add_nodes_from(list(range(int(tokens[2]))))
            if tokens[0] == "e":
                nodef, nodet = int(tokens[1]) - 1, int(tokens[2]) - 1
                nodes = set(G.nodes())
                G.add_edge(nodef, nodet, 0)

    return G


def print_test_result(funcName, mis, isMis, duration):
    print("---- {funcName} -> MIS size: {misSize} MIS: {mis} isMIS: {isMIS} -> Execution time: {duration}".format(
        funcName=funcName, misSize=len(mis), mis=mis, isMIS=isMis, duration=duration))


def test_benchmark():
    dirname = "benchmark"
    filenames = next(walk(dirname), (None, None, []))[2]

    print("---------TESTS---------")

    for filename in filenames:

        graph = load_graph(
            "{dirname}/{filename}".format(dirname=dirname, filename=filename))

        print("FILE -> ", filename)
        print("GRAPH -> nodes: {nodesNumber} edges {edgesNumber}".format(
            nodesNumber=graph.num_nodes(), edgesNumber=graph.num_edges()))
        
        exactRes, exactDuration = timeout(graph, 60 * 20, "MIS_exact", MIS_exact, graph)
        heuristicRes, heuristicDuration = timeout(graph, 60 * 20, "MIS_heuristic", MIS_heuristic, graph)
        localSearchRes, localSearchDuration = timeout(graph, 60 * 20, "MIS_local_search", MIS_local_search, graph, heuristicRes, len(heuristicRes) - 1)
        
        print("\n-----------------------")