# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

from mesa.visualization import SolaraViz, make_space_component
from model import RobotMission
from agents import GreenRobot, YellowRobot, RedRobot
from objects import RadioactivityAgent, WasteAgent

# REFERENCE FOR COLORS : https://matplotlib.org/stable/gallery/color/named_colors.html

# Define agent portrayal function (only colors robots, no environment coloring)
def agent_portrayal(agent):
    portrayal = {
            "color": "tab:blue",
            "size": 50,
            "linewidths": 1,
            "edgecolors":"black",
            "zorder": 0,
            }
    
    if isinstance(agent, (GreenRobot, YellowRobot, RedRobot)):
        portrayal["marker"] = "s"
        portrayal["zorder"] = 2

        robot_type = type(agent).__name__

        if robot_type == "GreenRobot":
            portrayal["color"] = "seagreen"
        elif robot_type == "YellowRobot":
            portrayal["color"] = "yellow"
        elif robot_type == "RedRobot":
            portrayal["color"] = "red"

    elif isinstance(agent, RadioactivityAgent):
        portrayal["size"] = 200
        portrayal["zorder"] = 1
        portrayal["marker"] = "s"
        portrayal["color"] = 1 - agent.radioactivity_level
        portrayal["linewidths"] = 0
        
    elif isinstance(agent, WasteAgent):
        portrayal["marker"] = "o"
        waste_type = agent.waste_type
        if waste_type == "green":
            portrayal["color"] = "darkgreen"
        elif waste_type == "yellow":
            portrayal["color"] = "gold"
        elif waste_type == "red":
            portrayal["color"] = "firebrick"
        portrayal["zorder"] = 2

    return portrayal

model1 = RobotMission(nb_green_robots=2,
                      nb_yellow_robots=2,
                      nb_red_robots=2,
                      nb_green_wastes=6,
                      nb_yellow_wastes=3,
                      nb_red_wastes=3,
                      width=12,
                      height=8)

model_params = {
    "width": model1.width,
    "height": model1.height,
    "nb_green_robots": {
        "type": "SliderInt",
        "value": model1.nb_green_robots,
        "label": "Number of greeen robots:",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "nb_yellow_robots": {
        "type": "SliderInt",
        "value": model1.nb_yellow_robots,
        "label": "Number of yellow robots:",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "nb_red_robots": {
        "type": "SliderInt",
        "value": model1.nb_red_robots,
        "label": "Number of red robots:",
        "min": 1,
        "max": 10,
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