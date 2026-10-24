"""Depth-first search: retorna el primer camí trobat."""


def search(graph, start, end):
    adj = graph["adj"]
    visited = set()
    previous = {start: None}
    events = []
    found = False
    stack = [start]

    while stack:
        node = stack.pop()

        if node in visited:
            continue

        visited.add(node)
        events.append((node, "current"))

        if node == end:
            found = True
            break

        # Invertim els veïns perquè l'ordre sigui estable amb una pila.
        for neighbor in reversed(list(adj[node])):
            if neighbor not in visited and neighbor not in previous:
                previous[neighbor] = node
                events.append((neighbor, "visited"))
                stack.append(neighbor)

    if not found:
        return events, None

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return events, path
