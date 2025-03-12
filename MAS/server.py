# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

from mesa.visualization import SolaraViz, make_space_component
from model import RobotMission
from agents import GreenRobot, YellowRobot, RedRobot
from objects import RadioactivityAgent

# Define agent portrayal function (only colors robots, no environment coloring)
def agent_portrayal(agent):
    portrayal = {
            "size": 50,
            "linewidths": 1,
            "zorder": 1,
            }
    
    if isinstance(agent, (GreenRobot, YellowRobot, RedRobot)):
        portrayal["marker"] = "s"
        portrayal["zorder"] = 2

        robot_type = type(agent).__name__

        if robot_type == "GreenRobot":
            portrayal["color"] = "green"
        elif robot_type == "YellowRobot":
            portrayal["color"] = "yellow"
        elif robot_type == "RedRobot":
            portrayal["color"] = "red"

    elif isinstance(agent, RadioactivityAgent):
        portrayal["size"] = 100
        portrayal["marker"] = "x"
        portrayal["color"] = 1 - agent.radioactivity_level
        portrayal["linewidths"] = 0.5

    return portrayal

model1 = RobotMission(num_robots=2, width=11, height=10)

model_params = {
    "width": model1.width,
    "height": model1.height,
    "num_robots": {
        "type": "SliderInt",
        "value": model1.num_robots,
        "label": "Number of robots:",
        "min": 1,
        "max": 15,
        "step": 1,
    },
}

# Visualization component (only robots, no environment coloring)
SpaceGraph = make_space_component(agent_portrayal)

page = SolaraViz(
    model1,
    components=[SpaceGraph],
    model_params=model_params,
    name="Robot Waste Cleanup Simulation",
)

page

# to start : "solara run MAS/server.py"