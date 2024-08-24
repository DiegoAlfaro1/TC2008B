from mesa import Agent, Model 
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class Trash(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class RobotAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.basura_guardada = 0
        self.celdas_recorridas = 0

    def step(self):
        posibles_movimientos = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        nueva_posicion = self.random.choice(posibles_movimientos)

        if self.model.grid.is_cell_empty(nueva_posicion):
            self.model.grid.move_agent(self, nueva_posicion)
            self.celdas_recorridas += 1
        else:
            contents = self.model.grid.get_cell_list_contents([nueva_posicion])
            trash = next((obj for obj in contents if isinstance(obj, Trash)), None)
            if trash:
                self.model.grid.remove_agent(trash)
                self.basura_guardada += 1

class RoomModel(Model):
    def __init__(self, width, height, agents, trash_percentage):
        self.grid = SingleGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.trash_percentage = trash_percentage
        self.steps_taken = 0

        cantidad_basura = int(width * height * trash_percentage)
        for i in range(cantidad_basura):
            y = self.random.randrange(self.grid.height)
            x = self.random.randrange(self.grid.width)
            if self.grid.is_cell_empty((x, y)):
                trash = Trash(None, self)
                self.grid.place_agent(trash, (x, y))

        for i in range(agents):
            aspiradora = RobotAgent(i, self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            while not self.grid.is_cell_empty((x, y)):
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            
            self.grid.place_agent(aspiradora, (x, y))
            self.schedule.add(aspiradora)

        self.datacollector = DataCollector(
            agent_reporters={
                "Efficiency": lambda a: (a.basura_guardada / a.celdas_recorridas) if a.celdas_recorridas > 0 else 0,
                "Cells_Cleaned": lambda a: a.basura_guardada,
                "Steps_Taken": lambda a: a.model.steps_taken
            },
            model_reporters={
                "Total_Cleaned_Cells": lambda m: sum(agent.basura_guardada for agent in m.schedule.agents),
                "Total_Steps_Taken": lambda m: m.steps_taken
            }
        )

    def step(self):
        self.steps_taken += 1
        self.datacollector.collect(self)
        self.schedule.step()

# Batch run for a single simulation
def batch_run(num_simulations, width, height, agents, trash_percentage, steps):
    all_agent_data = pd.DataFrame()
    all_model_data = pd.DataFrame()

    for run in range(num_simulations):
        model = RoomModel(width, height, agents, trash_percentage)
        
        for i in range(steps):
            model.step()

        agent_data = model.datacollector.get_agent_vars_dataframe()
        agent_data['Run'] = run
        model_data = model.datacollector.get_model_vars_dataframe()
        model_data['Run'] = run

        all_agent_data = pd.concat([all_agent_data, agent_data])
        all_model_data = pd.concat([all_model_data, model_data])
    
    return all_agent_data, all_model_data

# Parameters
num_simulations = 2
width, height = 20, 20
agents = 5
trash_percentage = 0.5
steps = 1500

# Run batch of simulations
agent_data, model_data = batch_run(num_simulations, width, height, agents, trash_percentage, steps)

np.savetxt('agent_data.csv', agent_data)
np.savetxt('model_data.csv', model_data)

# Plotting Efficiency over Steps for all simulations
sns.lineplot(data=agent_data.reset_index(), x='Step', y='Efficiency', hue='AgentID')
plt.title('Efficiency of the Agent Over Time')
plt.show()

# Plotting Total Cells Cleaned over Steps for all simulations
sns.lineplot(data=model_data.reset_index(), x='Total_Steps_Taken', y='Total_Cleaned_Cells')
plt.title('Total Cleaned Cells Over Time')
plt.show()
