import rustworkx as rx

def MIS_exact(G):
    """
    Solucion exacta para encontrar el conjunto maximo independiente de un grafo G.

    :param G: grafo G
    :return: indices del grafo que conforman un conjunto independiente maximo
    """ 
    node_indexes = list(G.node_indices())
    
    # Caso Base: Si solo hay un nodo, ese es el conjunto maximo independiente. Si no hay nodos, es trivial.
    if G.num_nodes() <= 1:
        return node_indexes

    v = node_indexes[0]
    v_neighbors = list(G.neighbors(v))

    # Caso 1: v pertenece al conjunto maximo independiente. Sus vecinos no.
    _G = G.copy()
    v_neighbors.append(v)
    _G.remove_nodes_from(list(v_neighbors))
    v_inc = [v] + MIS_exact(_G)

    # Caso 2: v no pertenece al conjunto maximo independiente. Sus vecinos puede que si.
    _G = G.copy()
    _G.remove_node(v)
    v_exc = MIS_exact(_G)

    if len(v_inc) > len(v_exc):
        return v_inc
    else:
        return v_exc
