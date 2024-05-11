import rustworkx as rx

def MIS_exact(G):
    if G.num_nodes() <= 1:
        return list(G.nodes())

    node_indexes = G.node_indices()
    v = node_indexes[0]
    v_neighbors = set(G.neighbors(v))

    v_neighbors.add(v)
    v_inc = [G.get_node_data(v)] + MIS_exact(G.subgraph(list(set(node_indexes).difference(v_neighbors))))
    v_exc = MIS_exact(G.subgraph(list(set(node_indexes).difference([v]))))
    
    if len(v_inc) > len(v_exc):
        return v_inc
    else:
        return v_exc
