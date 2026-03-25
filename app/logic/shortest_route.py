import networkx as nx
def shortest_route(graph, start, end):
    try:
        return nx.shortest_path(graph, source=start, target=end, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None