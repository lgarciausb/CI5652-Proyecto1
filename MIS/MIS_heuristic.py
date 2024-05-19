from random import randint
import rustworkx as rx

def MIS_heuristic(G):
    """
    Solucion heuristica para encontrar el conjunto maximo independiente de un grafo G.

    :param G: grafo G
    :return: indices del grafo que conforman un conjunto independiente maximal
    """ 

    S = []

    # ordenamos los nodos del grafo en orden de su cantidad de vecinos
    nodes = []
    for node in G.node_indices():
        nodes.append({"index": node, "neighbors": G.neighbors(node)})
    nodes.sort(key=lambda x: len(x["neighbors"]))

    # se recorre la lista ordenada de nodos
    # y se agrega un nodo al conjunto si no es adyacente
    # a algun nodo que haya sido agregado previamente
    for node in nodes:
        valid = True
        for neighbor in node["neighbors"]:
            if G[neighbor] == 1:
                valid = False
                break

        if valid:
            G[node["index"]] = 1
            S.append(node["index"])

    return S
