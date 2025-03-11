from objects import RadioactivityAgent, WasteDisposalZone, WasteAgent
from agents import GreenRobot, YellowRobot, RedRobot
from model import RobotMission

#Create RobotMission instance
model = RobotMission(n=1, width=12, height=4)

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