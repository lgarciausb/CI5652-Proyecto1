import rustworkx as rx

def MIS_exact(G):
    node_indexes = list(G.node_indices())
    if G.num_nodes() <= 1:
        return node_indexes

    v = node_indexes[0]
    v_neighbors = list(G.neighbors(v))

    _G = G.copy()
    v_neighbors.append(v)
    _G.remove_nodes_from(list(v_neighbors))
    v_inc = [v] + MIS_exact(_G)

    _G = G.copy()
    _G.remove_node(v)
    v_exc = MIS_exact(_G)

    if len(v_inc) > len(v_exc):
        return v_inc
    else:
        return v_exc
