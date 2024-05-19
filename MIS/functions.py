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
    """
    Funcion que calcula el tiempo de ejecucion de otra

    :param func: funcion a ejecutar
    :param *args: argumentos de func
    :return: Retorna el resultado de la funcion y el tiempo de ejecucion
    """ 
    start = time.time()
    result = func(*args)
    duration = time.time() - start
    return result, duration

def timeout(time, func, *args):
    """
    Funcion que dada otra funcion de calculo de MIS determina si se excedio a un limite de tiempo dado o tuvo otro error

    :param G: grafo dado
    :param time: timepo limite
    :param funcName: nombre de la funcion a ejecutar
    :param func: funcion a ejecutar
    :param *args: argumentos de func
    :return: Si func finalizó antes del maximo tiempo de ejecución retorna la respuesta, de lo contrario retorna un conjunto vacío. Retorna en todo caso el tiempo de ejecución
    """ 
    signal.alarm(time)
    try:
        res, duration = timer(func, *args)
    except TimeoutException:
        print("---- {funcName} -> Max Time ({time} s) Exceeded".format(funcName = func.__name__, time = time))
        return set(), time
    except Exception as e:
        print("---- {funcName} -> Something went wrong: {error}".format(funcName = func.__name__, error = e))
        return set(), time
    else:
        # Reset the alarm
        signal.alarm(0)
        #print results
        print("---- {funcName} -> MIS size: {misSize} MIS: {mis} isMIS: {isMIS} -> Execution time: {duration}".format(
        funcName=func.__name__, misSize=len(res), mis=res, isMIS=is_MIS(args[0], res), duration=duration))
        
        return res, duration

def is_MIS(G, S):
    """
    Funcion que recibe un grafo G y un conjunto S de indices de nodos y determina si S es un conjunto independiente maximal

    :param G: grafo dado
    :param S: posible conjunto independiente maximal de G
    :return: true si S es MIS para G, false si no
    """ 
    for node in S:
        if any((neighbor in S) for neighbor in G.neighbors(node)): return False
    for node in G.node_indices():
        if node not in S and not any((neighbor in S) for neighbor in G.neighbors(node)):
            return False
    return True

def randomGraph(n, e):
    """
    Funcion que recibe dos enteros n y e, y retorna un Grafo con n nodos y e lados

    :param n: numero de nodos
    :param e: numero de edges
    :return: grafo random con n nodos y e lados
    """ 
    G = rx.PyGraph()
    for i in range(n):
        G.add_node(0)
    for i in range(e):
        G.add_edge(randint(0, n-1), randint(0, n-1), None)

    return G


def load_graph(filename):
    """
    Funcion que carga un grafo en formato DIMACS dado el nombre de un archivo

    :param filename: nombre/path del archivo
    :return: grafo cargado
    """ 
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
    """
    Funcion que dada otra funcion de calculo de MIS determina si se excedio a un limite de tiempo dado o tuvo otro error

    :param funcName: nombre de la funcion a ejecutar
    :param mis: posible conjunto independiente maximal
    :param isMis: booleano que indica si mis es realmente maximal
    :paran duration: tiempo (en segundos) que toma en ejecutarse funcName
    """ 
    print("---- {funcName} -> MIS size: {misSize} MIS: {mis} isMIS: {isMIS} -> Execution time: {duration}".format(
        funcName=funcName, misSize=len(mis), mis=mis, isMIS=isMis, duration=duration))


def test_benchmark(time):
    """
    Funcion para testear todos los files del benchmark
    """ 
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