"""Dijkstra: minimitza el cost total de les arestes (metres)."""


import heapq


def search(graph, start, end):
    adj = graph["adj"]
    distances = {node: float("inf") for node in adj}
    previous = {node: None for node in adj}
    distances[start] = 0.0

    queue = [(0.0, start)]
    settled = set()
    events = []

    while queue:
        cost, node = heapq.heappop(queue)

        if node in settled or cost > distances[node]:
            continue

        settled.add(node)
        events.append((node, "current"))

        if node == end:
            break

        for neighbor, weight in adj[node].items():
            new_cost = cost + weight

            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous[neighbor] = node
                heapq.heappush(queue, (new_cost, neighbor))

                if neighbor not in settled:
                    events.append((neighbor, "visited"))

    if distances[end] == float("inf"):
        return events, None

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return events, path
