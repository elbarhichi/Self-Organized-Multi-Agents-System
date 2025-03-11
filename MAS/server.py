# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

from mesa.visualization import SolaraViz, make_space_component
from model import RobotMission

# Define agent portrayal function (only colors robots, no environment coloring)
def agent_portrayal(agent):
    portrayal = {
        "size": 20,
        "shape": "circle",
    }

    robot_type = type(agent).__name__

    if robot_type == "GreenRobot":
        portrayal["color"] = "green"
    elif robot_type == "YellowRobot":
        portrayal["color"] = "yellow"
    elif robot_type == "RedRobot":
        portrayal["color"] = "red"

    return portrayal

model_params = {
    "width": 10,
    "height": 10,
    "num_robots": {
        "type": "SliderInt",
        "value": 10,
        "label": "Number of robots:",
        "min": 1,
        "max": 30,
        "step": 1,
    },
}

model1 = RobotMission(n=10, width=10, height=10)

# Visualization component (only robots, no environment coloring)
SpaceGraph = make_space_component(agent_portrayal)

page = SolaraViz(
    model1,
    components=[SpaceGraph],
    model_params=model_params,
    name="Robot Waste Cleanup Simulation",
)

page