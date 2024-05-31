from numpy.random import choice

from .MIS_heuristic import MIS_heuristic
from .MIS_local_search import MIS_local_search


def greedy_solution(G, S, alpha=0.1):
    """
    Funcion que retorna una solucion greedy para MIS basandose en un RCL, anadiendo un vertice cada vez

    :pram G: grafo del que se quiere obtener solucion
    :param S: solucion 
    :param alpha: parámetro candidato restringido. alpha > 0
    :return: un posible conjunto independiente
    """
    _S = S.copy()
    _G = G.copy()
    
    # Obtenemos los nodos del grafo y sus vecinos
    nodes = []
    node_indexes = G.node_indexes()
                    
    if (len(node_indexes) > 0):
        for node in node_indexes:
            neighbors = list(G.neighbors(node))
            nodes.append({"index": node, "neighbors": neighbors, "degree": len(neighbors)})

        # Obtenemos el menor grado entre los vertices
        min_degree = min(nodes, key=lambda n: n["degree"])["degree"]

        # Construimos una solucion greedy con RCL = (v in Vk | dv < (1 + alpha) * P or dv == 0) donde
        # min_degree es el grado mas pequeno de vertices en Vk distinto a 0 
        RCL = [node_data for node_data in nodes if node_data["degree"] < ((1 + alpha) * min_degree) or node_data["degree"] == 0]

        # Elegimos un vertice al azar y lo incluimos en la solucion
        v = choice(RCL)
        _S.add(v["index"])

        # Inducimos un grafo del vertice elegido
        for u in v["neighbors"]:
            _G.remove_node(u)
        _G.remove_node(v["index"])
    return _S, _G


def MIS_GRASP(G, max_iter=10, alpha=0.1):
    """
    GRASP para encontrar el conjunto maximo independiente de un grafo G haciendo busqueda local de k-exchanges con 
    k = len(S) - 1 para un S obtenido con el RCL.

    :param G: grafo G
    :param S: conjunto independiente de G
    :param alpha: parámetro candidato restringido. alpha > 0
    :return: indices del grafo que conforman un conjunto independiente maximo
    """ 
    S = set()
    _G = G.copy()
    for _ in range(max_iter):
        S, _G = greedy_solution(_G, S, alpha)
        _S = set(MIS_local_search(G, S, len(S) - 1))

        if len(S) < len(_S):
            S = _S.copy()
    return list(S)
