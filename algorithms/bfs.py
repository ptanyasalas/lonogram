"""Breadth-first search: minimitza el nombre d'arestes, no la distància."""


from collections import deque


def search(graph, start, end):
    adj = graph["adj"]
    queue = deque([start])
    previous = {start: None}
    events = []

    while queue:
        node = queue.popleft()
        events.append((node, "current"))

        if node == end:
            break

        for neighbor in adj[node]:
            if neighbor not in previous:
                previous[neighbor] = node
                events.append((neighbor, "visited"))
                queue.append(neighbor)

    if end not in previous:
        return events, None

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()

    return events, path
