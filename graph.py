from random import randint
import rustworkx as rx

#funcion que recibe un grafo G y un conjunto S de indices de nodos y determina si
#S es un conjunto independiente maximal
def is_MIS(G, S):
    for node in G.node_indices():
        if node not in S and not any((neighbor in S) for neighbor in G.neighbors(node)): return False
    return True

#funcion que recibe dos enteros n y e, y retorna un Grafo 
#con n nodos y e lados
def randomGraph(n, e):
    G = rx.PyGraph()
    for i in range(n):
        G.add_node(0)
    for i in range(e):
        G.add_edge(randint(0,n-1), randint(0,n-1), None)
    
    return G

#funcion que recibe un grafo G y retorna un conjunto de
#indices del grafo que conforman un conjunto independiente maximal
def MIS_heuristic(G):

    S = []

    #ordenamos los nodos del grafo en orden de su cantidad de vecinos
    nodes = []
    for node in G.node_indices():
        nodes.append({"index":node, "neighbors":G.neighbors(node)})
    nodes.sort(key=lambda x: len(x["neighbors"]))

    #se recorre la lista ordenada de nodos 
    #y se agrega un nodo al conjunto si no es adyacente
    #a algun nodo que haya sido agregado previamente
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


n = 1000
e = int(n**2/8)
G = randomGraph(n,e)
S = MIS_heuristic(G)
print(is_MIS(G, S))





