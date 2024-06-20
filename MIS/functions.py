import time
import datetime
import rustworkx as rx
import pandas as pd
from os import walk

from .MIS_exact import MIS_exact
from .MIS_heuristic import MIS_heuristic
from .MIS_local_search import MIS_local_search
from .MIS_ILS import MIS_ILS
from .MIS_tabu_search import MIS_tabu_search
from .MIS_simulated_annealing import MIS_simulated_annealing
from .MIS_genetic import MIS_genetic
from .MIS_GRASP import MIS_GRASP
from .MIS_ACO import MIS_ACO

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
        print(
            "---- {funcName} -> Max Time ({time} s) Exceeded".format(funcName=func.__name__, time=time))
        return set(), 0, False, time, "TIMEOUT"
    except Exception as e:
        print(
            "---- {funcName} -> Something went wrong: {error}".format(funcName=func.__name__, error=e))
        return set(), 0, False, time, e
    else:
        # Reset the alarm
        signal.alarm(0)
        # print results
        is_mis = is_MIS(args[0], res)
        print("---- {funcName} -> MIS size: {misSize} MIS: {mis} isMIS: {isMIS} -> Execution time: {duration}".format(
            funcName=func.__name__, misSize=len(res), mis=res, isMIS=is_mis, duration=duration))

        return res, len(res), is_mis, duration, ""


def is_MIS(G, S):
    """
    Funcion que recibe un grafo G y un conjunto S de indices de nodos y determina si S es un conjunto independiente maximal

    :param G: grafo dado
    :param S: posible conjunto independiente maximal de G
    :return: true si S es MIS para G, false si no
    """
    for node in S:
        if any((neighbor in S) for neighbor in G.neighbors(node)):
            return False
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
    :param duration: tiempo (en segundos) que toma en ejecutarse funcName
    """
    print("---- {funcName} -> MIS size: {misSize} MIS: {mis} isMIS: {isMIS} -> Execution time: {duration}".format(
        funcName=funcName, misSize=len(mis), mis=mis, isMIS=isMis, duration=duration))


def test_benchmark(time, project_part=1):
    """
    Funcion para testear todos los files del benchmark para el primer corte

    :param time: tiempo maximo para ejecutar una funcion
    """
    dirname = "benchmark"
    filenames = next(walk(dirname), (None, None, []))[2]

    print("---------TESTS---------")

    data = []
    indexes = []
    columns = ["Result", "Size Result", "Is MIS", "Time", "Warnings"]

    for filename in filenames:

        graph = load_graph(
            "{dirname}/{filename}".format(dirname=dirname, filename=filename))

        print("FILE -> ", filename)
        print("GRAPH -> nodes: {nodesNumber} edges {edgesNumber}".format(
            nodesNumber=graph.num_nodes(), edgesNumber=graph.num_edges()))
        indexes.append("{filename} n={n} e={e}".format(
            filename=filename, n=graph.num_nodes(), e=graph.num_edges()))

        if (project_part == 1):
            exact_res, size_exact_res, is_mis_exact_res, exact_duration, exact_warning = timeout(
                time, MIS_exact, graph)
            heuristic_res, size_heuristic_res, is_mis_heuristic_res, heuristic_duration, heuristic_warning = timeout(
                time, MIS_heuristic, graph)
            local_search_res, size_local_search_res, is_mis_local_search_res, local_search_duration, local_search_warning = timeout(
                time, MIS_local_search, graph, heuristic_res, len(heuristic_res) - 1)

            index = ["exact", "heuristic", "local search"]
            times = [exact_duration, heuristic_duration, local_search_duration]
            result = [exact_res, heuristic_res, local_search_res]
            is_mis_result = [is_mis_exact_res,
                             is_mis_heuristic_res, is_mis_local_search_res]
            result_size = [size_exact_res,
                           size_heuristic_res, size_local_search_res]
            warnings = [exact_warning, heuristic_warning, local_search_warning]

        elif (project_part == 2):
            ils_res, size_ils_res, is_mis_ils_res, ils_duration, ils_warning = timeout(
                time, MIS_ILS, graph)
            tabu_res, size_tabu_res, is_mis_tabu_res, tabu_duration, tabu_warning = timeout(
                time, MIS_tabu_search, graph)
            sa_res, size_sa_res, is_mis_sa_res, sa_duration, sa_warning = timeout(
                time, MIS_simulated_annealing, graph)
            grasp_res, size_grasp_res, is_mis_grasp_res, grasp_duration, grasp_warning = timeout(
                time, MIS_GRASP, graph)
            genetic_res, size_genetic_res, is_mis_genetic_res, genetic_duration, genetic_warning = timeout(
                time, MIS_genetic, graph, 500, 10, 500)

            index = ["ils", "tabu", "sa", "grasp", "genetic"]
            times = [ils_duration, tabu_duration,
                     sa_duration, grasp_duration, genetic_duration]
            result = [ils_res, tabu_res, sa_res, grasp_res, genetic_res]
            is_mis_result = [is_mis_ils_res, is_mis_tabu_res,
                             is_mis_sa_res, is_mis_grasp_res, is_mis_genetic_res]
            result_size = [size_ils_res, size_tabu_res,
                           size_sa_res, size_grasp_res, size_genetic_res]
            warnings = [ils_warning, tabu_warning,
                        sa_warning, grasp_warning, genetic_warning]
        else:
            aco1_res, size_aco1_res, is_mis_aco1_res, aco1_duration, aco1_warning = timeout(
                time, MIS_ACO, graph)

            aco2_res, size_aco2_res, is_mis_aco2_res, aco2_duration, aco2_warning = timeout(
                time, MIS_ACO, graph, 150)

            aco3_res, size_aco3_res, is_mis_aco3_res, aco3_duration, aco3_warning = timeout(
                time, MIS_ACO, graph, 10, 50, 0.2, 0.8, 0.3, 1)

            aco4_res, size_aco4_res, is_mis_aco4_res, aco4_duration, aco4_warning = timeout(
                time, MIS_ACO, graph, 150, 50, 0.2, 0.8, 0.3, 1)

            index = ["aco1", "aco2", "aco3", "aco4"]
            times = [aco1_duration, aco2_duration, aco3_duration, aco4_duration]
            result = [aco1_res, aco2_res, aco3_res, aco4_res]
            is_mis_result = [is_mis_aco1_res, is_mis_aco2_res, is_mis_aco3_res, is_mis_aco4_res]
            result_size = [size_aco1_res, size_aco2_res, size_aco3_res, is_mis_aco4_res]
            warnings = [aco1_warning, aco2_warning, aco3_warning, aco4_warning]
        data.append(result + result_size + is_mis_result + times + warnings)

        print("\n-----------------------")

    df = pd.DataFrame(data=data, index=indexes)
    df.columns = pd.MultiIndex.from_product([columns, index])
    df.to_csv("res/{project_part}_corte_res_{time}min.csv".format(
        project_part=project_part, time=time // 60))


def load_cubical_graph():
    """
    Funcion que carga un grafo cubico

    :return: grafo cargado
    """
    G = rx.PyGraph()

    G.add_nodes_from(list(range(8)))
    G.add_edges_from_no_data([(0, 1), (1, 2), (2, 3), (3, 0), (4, 5),
                              (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)])

    return "CUBICAL", G


def load_p3_graph():
    """
    Funcion que carga un grafo p3

    :return: grafo cargado
    """
    G = rx.PyGraph()

    G.add_nodes_from(list(range(3)))
    G.add_edges_from_no_data([(0, 1), (1, 2)])

    return "P3", G


def load_k3_graph():
    """
    Funcion que carga un grafo k3

    :return: grafo cargado
    """
    G = rx.PyGraph()

    G.add_nodes_from(list(range(6)))
    G.add_edges_from_no_data(
        [(0, 1), (1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])

    return "K3", G


def load_square_triangle_graph():
    """
    Funcion que carga un grafo que une un cuadrado con un triangulo

    :return: grafo cargado
    """
    G = rx.PyGraph()

    G.add_nodes_from(list(range(6)))
    G.add_edges_from_no_data(
        [(0, 1), (1, 2), (2, 3), (3, 1), (2, 4), (4, 5), (5, 3)])

    return "SQUARE_TRIANGLE", G


def test_defined_graphs(time, project_part=1):
    """
    Funcion para testear algunos grafos definidos

    :param time: tiempo maximo para ejecutar una funcion
    """

    defined_graphs = [load_cubical_graph(), load_k3_graph(
    ), load_p3_graph(), load_square_triangle_graph()]
    data = []
    indexes = []
    columns = ["Result", "Size Result", "Is MIS", "Time", "Warnings"]

    print("---------TESTS---------")
    for graph_data in defined_graphs:
        graph = graph_data[1]
        print("NAME -> ", graph_data[0])
        print("GRAPH -> nodes: {nodesNumber} edges {edgesNumber}".format(
            nodesNumber=graph.num_nodes(), edgesNumber=graph.num_edges()))

        indexes.append("{graphName} n={n} e={e}".format(
            graphName=graph_data[0], n=graph.num_nodes(), e=graph.num_edges()))

        if (project_part == 1):
            exact_res, size_exact_res, is_mis_exact_res, exact_duration, exact_warning = timeout(
                time, MIS_exact, graph)
            heuristic_res, size_heuristic_res, is_mis_heuristic_res, heuristic_duration, heuristic_warning = timeout(
                time, MIS_heuristic, graph)
            local_search_res, size_local_search_res, is_mis_local_search_res, local_search_duration, local_search_warning = timeout(
                time, MIS_local_search, graph, heuristic_res, len(heuristic_res) - 1)

            index = ["exact", "heuristic", "local search"]
            times = [exact_duration, heuristic_duration, local_search_duration]
            result = [exact_res, heuristic_res, local_search_res]
            is_mis_result = [is_mis_exact_res,
                             is_mis_heuristic_res, is_mis_local_search_res]
            result_size = [size_exact_res,
                           size_heuristic_res, size_local_search_res]
            warnings = [exact_warning, heuristic_warning, local_search_warning]

        else:
            ils_res, size_ils_res, is_mis_ils_res, ils_duration, ils_warning = timeout(
                time, MIS_ILS, graph)
            tabu_res, size_tabu_res, is_mis_tabu_res, tabu_duration, tabu_warning = timeout(
                time, MIS_tabu_search, graph)
            sa_res, size_sa_res, is_mis_sa_res, sa_duration, sa_warning = timeout(
                time, MIS_simulated_annealing, graph)
            grasp_res, size_grasp_res, is_mis_grasp_res, grasp_duration, grasp_warning = timeout(
                time, MIS_GRASP, graph)
            genetic_res, size_genetic_res, is_mis_genetic_res, genetic_duration, genetic_warning = timeout(
                time, MIS_genetic, graph, 500, 10, 500)

            index = ["ils", "tabu", "sa", "grasp", "genetic"]
            times = [ils_duration, tabu_duration,
                     sa_duration, grasp_duration, genetic_duration]
            result = [ils_res, tabu_res, sa_res, grasp_res, genetic_res]
            is_mis_result = [is_mis_ils_res, is_mis_tabu_res,
                             is_mis_sa_res, is_mis_grasp_res, is_mis_genetic_res]
            result_size = [size_ils_res, size_tabu_res,
                           size_sa_res, size_grasp_res, size_genetic_res]
            warnings = [ils_warning, tabu_warning,
                        sa_warning, grasp_warning, genetic_warning]

        data.append(result + result_size + is_mis_result + times + warnings)

        print("\n-----------------------")
