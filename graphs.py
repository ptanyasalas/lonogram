"""Càrrega i conversió de xarxes de carrers d'OpenStreetMap."""

import osmnx as ox


def load_graph(place_name, network_type="walk"):
    """Descarrega un graf de carrers i el converteix al format de Lonogram.

    Cada node conserva les coordenades geogràfiques x/y d'OSM.
    Cada aresta té com a pes la longitud del tram en metres.
    """
    raw_graph = ox.graph_from_place(
        place_name,
        network_type=network_type,
        simplify=False
    )

    nodes = {}
    for node_id, data in raw_graph.nodes(data=True):
        nodes[node_id] = {
            "x": float(data["x"]),  # longitud
            "y": float(data["y"]),  # latitud
        }

    adj = {node_id: {} for node_id in nodes}

    # OSMnx retorna un MultiDiGraph: poden existir diverses arestes
    # entre dos nodes. En aquesta primera versió guardem el tram més curt.
    for u, v, data in raw_graph.edges(data=True):
        if u == v:
            continue

        length = float(data.get("length", 1.0))

        old_uv = adj[u].get(v)
        if old_uv is None or length < old_uv:
            adj[u][v] = length

        old_vu = adj[v].get(u)
        if old_vu is None or length < old_vu:
            adj[v][u] = length

    if not nodes or not any(adj.values()):
        raise ValueError("OpenStreetMap no ha retornat una xarxa de carrers útil.")

    return {
        "place": place_name,
        "nodes": nodes,
        "adj": adj,
    }


def path_cost(graph, path):
    """Calcula el cost d'un camí en metres."""
    if not path:
        return float("inf")

    return sum(
        graph["adj"][a][b]
        for a, b in zip(path, path[1:])
    )
