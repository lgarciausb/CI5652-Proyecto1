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

#funcion que recibe una funcion y una serie de argumentos correspondientes 
# a esa funcion, y calcula el tiempo de ejecucion de dicha funcion.
# retorna el resultado de la funcion y el tiempo de ejecucion


def timer(func, *args):
    start = time.time()
    result = func(*args)
    duration = time.time() - start
    return result, duration

#funcion que recibe un enetero time, una funcion func, y una serie de argumentos *args
#que ejecuta func con *args como argumentos con un maximo limite de tiempo de ejecucion time segundos.
#Si func finalizó antes del maximo tiempo de ejecución retorna la respuesta, de lo contrario
#retorna un conjunto vacío. Retorna en todo caso el tiempo de ejecución


def timeout(time, func, *args):
    signal.alarm(time)
    try:
        res, duration = timer(func, *args)
    except TimeoutException:
        print("---- {funcName} -> Max Time ({time} s) Exceeded".format(funcName = func.__name__, time = time))
        return set(), time
    except Exception as e:
        print("---- {funcName} -> Something went wrong: {error}".format(funcName = func.__name__,, error = e))
        return set(), time
    else:
        # Reset the alarm
        signal.alarm(0)
        #print results
        print("---- {funcName} -> MIS size: {misSize} MIS: {mis} isMIS: {isMIS} -> Execution time: {duration}".format(
        funcName=func.__name__, misSize=len(res), mis=res, isMIS=is_MIS(args[0], res), duration=duration))
        
        return res, duration


# funcion que recibe un grafo G y un conjunto S de indices de nodos y determina si
# S es un conjunto independiente maximal


def is_MIS(G, S):
    for node in G.node_indices():
        if node not in S and not any((neighbor in S) for neighbor in G.neighbors(node)):
            return False
    return True

#funcion que carga un grafo definido en un archivo de texto

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

#funcion que corre un benchmark sobre tres funciones, una solucion exacta a MIS,
#una heuristica para MIS, y una busqueda local de un MIS.
#carga varios archivos de grafos y corre dichas funciones sobre cada grafo, 
#reportando por consola el resultado y tiempo de ejecucion de cada funcion.
#recibe un entero time que determina el maximo tiempo de ejecucion para
#las funciones


def test_benchmark(time):
    dirname = "benchmark"
    filenames = next(walk(dirname), (None, None, []))[2]

    print("---------TESTS---------")

    for filename in filenames:

        graph = load_graph(
            "{dirname}/{filename}".format(dirname=dirname, filename=filename))

        print("FILE -> ", filename)
        print("GRAPH -> nodes: {nodesNumber} edges {edgesNumber}".format(
            nodesNumber=graph.num_nodes(), edgesNumber=graph.num_edges()))
        
        exactRes, exactDuration = timeout(time, MIS_exact, graph)
        heuristicRes, heuristicDuration = timeout(time, MIS_heuristic, graph)
        localSearchRes, localSearchDuration = timeout(time, MIS_local_search, graph, heuristicRes, len(heuristicRes) - 1)
        
        print("\n-----------------------")