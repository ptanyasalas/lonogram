"""Visualització interactiva d'un graf geogràfic amb Pygame."""

import math
import pygame

from algorithms import bfs, dfs, dijkstra
from graphs import path_cost


WIDTH = 1200
HEIGHT = 800
PANEL_HEIGHT = 90
BACKGROUND = (17, 24, 39)
ROAD_COLOR = (76, 91, 112)
ROAD_HIGHLIGHT = (180, 100, 255)
NODE_COLOR = (115, 132, 154)
VISITED_COLOR = (245, 171, 63)
CURRENT_COLOR = (56, 189, 248)
START_COLOR = (34, 197, 94)
END_COLOR = (239, 68, 68)
TEXT_COLOR = (240, 244, 250)


class MapViewer:
    def __init__(self, graph, place):
        pygame.init()
        pygame.display.set_caption(f"Lonogram — {place}")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 17)
        self.small_font = pygame.font.SysFont("arial", 13)
        self.title_font = pygame.font.SysFont("arial", 24)

        self.graph = graph
        self.nodes = graph["nodes"]
        self.adj = graph["adj"]
        self.place = place

        self.algorithm_name = "Dijkstra"
        self.algorithm_fn = dijkstra.search
        self.start = None
        self.end = None
        self.path = None
        self.path_cost_value = None
        self.events = []
        self.event_index = 0
        self.states = {}
        self.animating = False
        self.last_step = 0
        self.step_delay = 18

        self.dragging = False
        self.drag_last = None
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        xs = [data["x"] for data in self.nodes.values()]
        ys = [data["y"] for data in self.nodes.values()]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
        self.center_x = (self.min_x + self.max_x) / 2
        self.center_y = (self.min_y + self.max_y) / 2

        # Aproximació local per evitar deformacions massa grans.
        self.cos_lat = max(0.2, math.cos(math.radians(self.center_y)))
        self.world = {}
        for node, data in self.nodes.items():
            self.world[node] = (
                (data["x"] - self.center_x) * self.cos_lat * 111_320,
                (self.center_y - data["y"]) * 111_320,
            )

        self.fit_map()

    def fit_map(self):
        points = list(self.world.values())
        if not points:
            return

        width = max(p[0] for p in points) - min(p[0] for p in points)
        height = max(p[1] for p in points) - min(p[1] for p in points)
        available_w = self.screen.get_width() - 70
        available_h = self.screen.get_height() - PANEL_HEIGHT - 50

        scale_x = available_w / max(width, 1)
        scale_y = available_h / max(height, 1)
        self.base_scale = min(scale_x, scale_y)
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

    def screen_pos(self, node):
        x, y = self.world[node]
        scale = self.base_scale * self.zoom
        cx = self.screen.get_width() / 2 + self.offset_x
        cy = (self.screen.get_height() + PANEL_HEIGHT) / 2 + self.offset_y
        return int(cx + x * scale), int(cy + y * scale)

    def nearest_node(self, pos):
        best_node = None
        best_dist = 22

        for node in self.nodes:
            x, y = self.screen_pos(node)
            dist = math.hypot(x - pos[0], y - pos[1])
            if dist < best_dist:
                best_node = node
                best_dist = dist

        return best_node

    def choose_algorithm(self, key):
        options = {
            pygame.K_1: ("BFS", bfs.search),
            pygame.K_2: ("DFS", dfs.search),
            pygame.K_3: ("Dijkstra", dijkstra.search),
        }
        if key in options:
            self.algorithm_name, self.algorithm_fn = options[key]
            self.reset_route()

    def reset_route(self):
        self.start = None
        self.end = None
        self.path = None
        self.path_cost_value = None
        self.events = []
        self.event_index = 0
        self.states.clear()
        self.animating = False

    def calculate_route(self):
        if self.start is None or self.end is None:
            return

        self.events, self.path = self.algorithm_fn(
            self.graph, self.start, self.end
        )
        self.path_cost_value = path_cost(self.graph, self.path) if self.path else None
        self.event_index = 0
        self.states.clear()
        self.animating = True
        self.last_step = pygame.time.get_ticks()

    def handle_click(self, pos):
        node = self.nearest_node(pos)
        if node is None:
            return

        if self.start is None or (self.start is not None and self.end is not None):
            self.start = node
            self.end = None
            self.path = None
            self.path_cost_value = None
            self.events = []
            self.states.clear()
            self.animating = False
        else:
            self.end = node
            self.calculate_route()

    def draw(self):
        self.screen.fill(BACKGROUND)

        # Draw each undirected road segment once.
        path_edges = set()
        if self.path:
            path_edges = {
                frozenset((a, b)) for a, b in zip(self.path, self.path[1:])
            }

        for node, neighbors in self.adj.items():
            x1, y1 = self.screen_pos(node)
            for neighbor in neighbors:
                if node >= neighbor:
                    continue
                x2, y2 = self.screen_pos(neighbor)
                selected = frozenset((node, neighbor)) in path_edges
                pygame.draw.line(
                    self.screen,
                    ROAD_HIGHLIGHT if selected else ROAD_COLOR,
                    (x1, y1),
                    (x2, y2),
                    4 if selected else 1,
                )

        # Mostra punts d'intersecció importants i els nodes seleccionats.
        for node, neighbors in self.adj.items():
            if len(neighbors) < 3 and node not in (self.start, self.end):
                continue

            x, y = self.screen_pos(node)
            color = NODE_COLOR

            if self.states.get(node) == "visited":
                color = VISITED_COLOR
            elif self.states.get(node) == "current":
                color = CURRENT_COLOR
            if node == self.start:
                color = START_COLOR
            if node == self.end:
                color = END_COLOR

            radius = 6 if len(neighbors) >= 3 else 8
            pygame.draw.circle(self.screen, color, (x, y), radius)

        panel = pygame.Rect(0, 0, self.screen.get_width(), PANEL_HEIGHT)
        pygame.draw.rect(self.screen, (25, 34, 51), panel)

        title = self.title_font.render(f"LONOGRAM  |  {self.place}", True, TEXT_COLOR)
        self.screen.blit(title, (18, 10))

        line1 = (
            "1 BFS   2 DFS   3 Dijkstra     "
            "Click: origen y destino     Enter: calcular     R: reiniciar"
        )
        self.screen.blit(self.font.render(line1, True, TEXT_COLOR), (18, 43))

        if self.start is None:
            status = "Selecciona el punt d'origen fent clic al mapa."
        elif self.end is None:
            status = f"Origen seleccionat ({self.start}). Ara selecciona la destinació."
        elif self.path is None:
            status = "Calculant ruta..." if self.animating else "No s'ha trobat cap ruta."
        else:
            if self.path_cost_value is None:
                status = f"Ruta trobada amb {len(self.path) - 1} trams."
            else:
                status = (
                    f"Ruta: {len(self.path) - 1} trams  |  "
                    f"Distància: {self.path_cost_value:.0f} m"
                )

        self.screen.blit(self.font.render(status, True, TEXT_COLOR), (18, 66))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )
                    self.fit_map()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_route()
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.choose_algorithm(event.key)
                    elif event.key == pygame.K_RETURN:
                        self.calculate_route()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                    elif event.button == 3:
                        self.dragging = True
                        self.drag_last = event.pos
                    elif event.button == 4:
                        self.zoom *= 1.15
                    elif event.button == 5:
                        self.zoom /= 1.15

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.dragging = False
                        self.drag_last = None

                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    if self.drag_last:
                        dx = event.pos[0] - self.drag_last[0]
                        dy = event.pos[1] - self.drag_last[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.drag_last = event.pos

            if self.animating and now - self.last_step >= self.step_delay:
                if self.event_index < len(self.events):
                    node, status = self.events[self.event_index]
                    self.states[node] = status
                    self.event_index += 1
                    self.last_step = now
                else:
                    self.animating = False

            self.draw()
            self.clock.tick(60)

        pygame.quit()


def run_viewer(graph, place):
    MapViewer(graph, place).run()
