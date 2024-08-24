from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random

GRID_WIDTH = 8
GRID_HEIGHT = 6
INITIAL_FIRE_LOCATIONS = [(2, 2), (2, 3), (3, 2),(3, 3),(3,4),(3,5),(4,4),(5,6),(5,7),(6,6)]
POI_LOCATIONS = [(2, 4), (5, 8), (5, 1)]

class FlashPointModel(Model):
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.walls = {}
        self.doors = {}
        self.damage_markers = 0
        self.rescued_victims = 0
        self.lost_victims = 0
        self.total_victims = 0
        self.max_victims = 12
        self.max_false_alarms = 6 

        # Ambient variables
        self.fire = set()
        self.smoke = set()
        self.pois = {}
        
        self.setup_board()

    def setup_board(self):
        for pos in INITIAL_FIRE_LOCATIONS:
            self.fire.add(pos)
        
        for idx, pos in enumerate(POI_LOCATIONS):
            is_victim = random.choice([True, False])
            self.pois[pos] = is_victim
            if is_victim:
                self.total_victims += 1

        self.walls = {
            ((3, 3), (3, 4)): "intact",
            ((4, 5), (5, 5)): "intact",
            ((5, 5), (5, 6)): "intact",
        }
        self.doors = {
            ((1, 2), (1, 3)): "closed",
            ((4, 2), (5, 2)): "closed",
        }

    def place_smoke(self, pos):
        if pos in self.fire:
            self.handle_explosion(pos)
        elif pos in self.smoke:
            self.convert_smoke_to_fire(pos)
        else:
            self.add_new_smoke(pos)

    def convert_smoke_to_fire(self, pos):
        self.smoke.remove(pos)
        self.fire.add(pos)
        if pos in self.pois and self.pois[pos]:
            self.lose_victim(pos)

    def add_new_smoke(self, pos):
        self.smoke.add(pos)

    def handle_explosion(self, pos):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if new_pos[0] < 0 or new_pos[0] >= self.grid.width or new_pos[1] < 0 or new_pos[1] >= self.grid.height:
                continue
            
            if self.wall_in_direction(pos, new_pos):
                self.break_wall(pos, new_pos) #que la dane
            elif self.door_in_direction(pos, new_pos):
                self.destroy_door(pos, new_pos)
            else:
                self.place_smoke(new_pos)
        
        self.damage_markers += 1
        self.check_game_over()

    def wall_in_direction(self, pos, new_pos):
        return ((pos, new_pos) in self.walls and self.walls[(pos, new_pos)] == "intact") or \
               ((new_pos, pos) in self.walls and self.walls[(new_pos, pos)] == "intact")

    def door_in_direction(self, pos, new_pos):
        return ((pos, new_pos) in self.doors) or ((new_pos, pos) in self.doors)

    def break_wall(self, pos, new_pos):
        if (pos, new_pos) in self.walls:
            self.walls[(pos, new_pos)] = "broken"
        elif (new_pos, pos) in self.walls:
            self.walls[(new_pos, pos)] = "broken"

    def destroy_door(self, pos, new_pos):
        if (pos, new_pos) in self.doors:
            del self.doors[(pos, new_pos)]
        elif (new_pos, pos) in self.doors:
            del self.doors[(new_pos, pos)]

    def lose_victim(self, pos):
        del self.pois[pos]
        self.lost_victims += 1
        print(f"A victim has been lost! Total lost: {self.lost_victims}")

    def check_game_over(self):
        if self.damage_markers >= 24:
            print("Game Over: Building has collapsed!")
            self.running = False
        elif self.lost_victims >= 4:
            print("Game Over: Too many victims lost!")
            self.running = False
        elif self.rescued_victims == 7:
            print("Victory: All victims have been rescued!")
            self.running = False

    def advance_fire(self):
        fire_roll = random.randint(1, 6) + random.randint(1, 6)
        fire_pos = (fire_roll % self.grid.width, fire_roll // self.grid.width)
        self.place_smoke(fire_pos)

    def step(self):
        #step de agente
        self.advance_fire()
        #reroll de poi
        self.schedule.step()
        self.check_game_over()

model = FlashPointModel()


model.step()


