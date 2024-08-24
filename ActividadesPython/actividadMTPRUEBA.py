import numpy as np
from mesa import Model, Agent
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from collections import deque
from typing import Tuple, List


class Pastor(Agent):
    def __init__(self, unique_id: int, model: Model, strategy: str = "random"):
        super().__init__(unique_id, model)
        self.carrying_sheep = False
        self.strategy = strategy
        self.target = None

    def step(self):
        if self.strategy == "random":
            self.random_move()
        else:
            self.coordinated_move()
        self.interact_with_sheep()

    def random_move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty_steps = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
        if empty_steps:
            new_position = self.random.choice(empty_steps)
            self.model.grid.move_agent(self, new_position)

    def coordinated_move(self):
        if not self.target or self.pos == self.target:
            self.target = self.find_best_target()

        if self.target:
            path = self.find_path(self.pos, self.target)
            if path and len(path) > 1:
                next_pos = path[1]
                if self.model.grid.is_cell_empty(next_pos):
                    self.model.grid.move_agent(self, next_pos)
                else:
                    self.random_move()
            else:
                self.random_move()
        else:
            self.random_move()

    def find_best_target(self) -> Tuple[int, int]:
        sheep_density_map = self.model.sheep_layer
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, radius=7)
        return max(neighborhood, key=lambda pos: sheep_density_map[pos[0]][pos[1]])

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        queue = deque([(start, [start])])
        visited = set([start])

        while queue:
            vertex, path = queue.popleft()
            if vertex == goal:
                return path

            for next_pos in self.model.grid.get_neighborhood(vertex, moore=False, include_center=False):
                if next_pos not in visited and self.model.grid.is_cell_empty(next_pos):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        return []

    def interact_with_sheep(self):
        x, y = self.pos
        if not self.carrying_sheep and self.model.sheep_layer[x][y] > 0:
            self.pick_up_sheep()
        elif self.carrying_sheep:
            self.drop_sheep()

    def pick_up_sheep(self):
        x, y = self.pos
        self.model.sheep_layer[x][y] -= 1
        self.carrying_sheep = True

    def drop_sheep(self):
        nearby_positions = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty_positions = [pos for pos in nearby_positions if self.model.sheep_layer[pos[0]][pos[1]] == 0]
        if empty_positions:
            drop_pos = self.random.choice(empty_positions)
            self.model.sheep_layer[drop_pos[0]][drop_pos[1]] += 1
            self.carrying_sheep = False


class Rancho(Model):
    def __init__(self, width: int = 30, height: int = 30, initial_sheep: int = 150, num_pastores: int = 5, strategy: str = "random"):
        super().__init__()
        self.grid = SingleGrid(width, height, False)
        self.num_pastores = num_pastores
        self.initial_sheep = initial_sheep
        self.schedule = RandomActivation(self)
        self.strategy = strategy

        self.sheep_layer = np.zeros((width, height), dtype=int)
        sheep_positions = self.random.sample([(x, y) for x in range(width) for y in range(height)], initial_sheep)
        for x, y in sheep_positions:
            self.sheep_layer[x][y] = 1

        for i in range(self.num_pastores):
            x, y = self.random_position()
            pastor = Pastor(i, self, strategy)
            self.grid.place_agent(pastor, (x, y))
            self.schedule.add(pastor)

        self.datacollector = DataCollector(
            model_reporters={
                "Efficiency": "efficiency",
                "Sheep Count": lambda m: np.sum(m.sheep_layer)
            }
        )
        self.efficiency = self.calculate_efficiency()

    def random_position(self) -> Tuple[int, int]:
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            if self.grid.is_cell_empty((x, y)) and self.sheep_layer[x][y] == 0:
                return x, y

    def calculate_efficiency(self) -> float:
        total_spaces = self.grid.width * self.grid.height
        sheep_count = np.sum(self.sheep_layer)
        empty_spaces = np.sum([
            (self.sheep_layer[x, y] == 0) and
            all(self.sheep_layer[nx, ny] == 0 for nx, ny in self.grid.get_neighborhood((x, y), moore=True, include_center=False))
            for x in range(self.grid.width) for y in range(self.grid.height)
        ])
        return empty_spaces / (total_spaces - sheep_count) if total_spaces > sheep_count else 0

    def step(self) -> bool:
        self.schedule.step()
        self.efficiency = self.calculate_efficiency()
        self.datacollector.collect(self)
        return self.efficiency > 0.85


def run_simulation(strategy: str, max_steps: int = 1000):
    model = Rancho(strategy=strategy)

    for _ in range(max_steps):
        if model.step():
            break

    return model.datacollector.get_model_vars_dataframe()


# Run the simulation with different strategies
random_results = run_simulation("random")
coordinated_results = run_simulation("coordinated")

print("Random Strategy Final Efficiency:", random_results["Efficiency"].iloc[-1])
print("Coordinated Strategy Final Efficiency:", coordinated_results["Efficiency"].iloc[-1])

# Print additional statistics
print("\nRandom Strategy:")
print("Max Efficiency:", random_results["Efficiency"].max())
print("Mean Efficiency:", random_results["Efficiency"].mean())
print("Final Sheep Count:", random_results["Sheep Count"].iloc[-1])

print("\nCoordinated Strategy:")
print("Max Efficiency:", coordinated_results["Efficiency"].max())
print("Mean Efficiency:", coordinated_results["Efficiency"].mean())
print("Final Sheep Count:", coordinated_results["Sheep Count"].iloc[-1])
