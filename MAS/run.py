# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

from objects import Radioactivity, WasteDisposalZone, WasteAgent
from agents.agents_no_comm import GreenRobot, YellowRobot, RedRobot
from model import RobotMission
import seaborn as sns

#Create RobotMission instance
model = RobotMission(nb_green_robots=1, nb_yellow_robots=1, nb_red_robots=1, width=12, height=4)

# Create radioactivity agents for different zones
r1 = Radioactivity(model, "green")
r2 = Radioactivity(model, "yellow")
r3 = Radioactivity(model, "red")

# Create a waste disposal zone in a grid of width 10
disposal_zone = WasteDisposalZone(model)

# Create waste agents
w1 = WasteAgent(model, "green")
w2 = WasteAgent(model, "yellow")
w3 = WasteAgent(model, "red")

print(r1)
print(r2)
print(r3)
print(disposal_zone)
print(w1)
print(w2)
print(w3)

for step in range(3):
    robot_agents = model.robot_agents
    for a in robot_agents:
        print(a)
            
    model.step()
    print('\nOne step done ! \n')
    
df_nb_wastes = model.datacollector.get_model_vars_dataframe()
print(df_nb_wastes)

print(model.steps)

for _ in range(20):
    model.step()

print(model.steps)

for robot in model.robot_agents:
    print('robot name :', robot.unique_id)