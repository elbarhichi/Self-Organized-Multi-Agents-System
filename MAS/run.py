from objects import RadioactivityAgent, WasteDisposalZone, WasteAgent
from agents import GreenRobot, YellowRobot, RedRobot
from model import RobotMission
import seaborn as sns

#Create RobotMission instance
model = RobotMission(n=2, width=12, height=4)

# Create radioactivity agents for different zones
r1 = RadioactivityAgent(model, "green")
r2 = RadioactivityAgent(model, "yellow")
r3 = RadioactivityAgent(model, "red")

# Create a waste disposal zone in a grid of width 10
disposal_zone = WasteDisposalZone(model, grid_width=10)

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

robot_agents = model.robot_agents
for a in robot_agents:
    print(f'Robot {type(a)} at position ({a.pos[0]}, {a.pos[1]})')
        
model.step()
print('\n One step done ! \n')

robot_agents = model.robot_agents
for a in robot_agents:
    print(f'Robot {type(a)} at position ({a.pos[0]}, {a.pos[1]})')
    
nb_wastes = model.datacollector.get_model_vars_dataframe()

print(nb_wastes)