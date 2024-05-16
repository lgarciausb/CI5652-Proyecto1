from random import randint
import rustworkx as rx

# funcion que recibe un grafo G y retorna un conjunto de
# indices del grafo que conforman un conjunto independiente maximal
def MIS_heuristic(G):

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
