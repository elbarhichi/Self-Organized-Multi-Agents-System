# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import RobotMission
from agents.agents_base import GreenRobot, YellowRobot, RedRobot
from objects import WasteDisposalZone, WasteAgent

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

        if isinstance(agent, GreenRobot):
            portrayal["color"] = "seagreen"
        elif isinstance(agent, YellowRobot):
            portrayal["color"] = "yellow"
        elif isinstance(agent, RedRobot):
            portrayal["color"] = "red"

    elif isinstance(agent, WasteDisposalZone):
        portrayal["size"] = 90
        portrayal["zorder"] = 1
        portrayal["marker"] = "X"
        portrayal["color"] = "tab:grey"
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

model1 = RobotMission(robot_type="No communication",
                      nb_green_robots=2,
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
    "robot_type": {
        "type": "Select",
        "value": model1.robot_type,
        "label": "Robot type:",
        "values": ["No communication", "With communication"],
    },
    "nb_green_robots": {
        "type": "SliderInt",
        "value": model1.nb_green_robots,
        "label": "Number of greeen robots:",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "nb_yellow_robots": {
        "type": "SliderInt",
        "value": model1.nb_yellow_robots,
        "label": "Number of yellow robots:",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "nb_red_robots": {
        "type": "SliderInt",
        "value": model1.nb_red_robots,
        "label": "Number of red robots:",
        "min": 0,
        "max": 12,
        "step": 1,
    },
    "nb_green_wastes": {
        "type": "SliderInt",
        "value": model1.nb_green_wastes,
        "label": "Number of green wastes:",
        "min": 0,
        "max": 12,
        "step": 1,
    },
    "nb_yellow_wastes": {
        "type": "SliderInt",
        "value": model1.nb_yellow_wastes,
        "label": "Number of yellow wastes:",
        "min": 0,
        "max": 12,
        "step": 1,
    },
    "nb_red_wastes": {
        "type": "SliderInt",
        "value": model1.nb_red_wastes,
        "label": "Number of red wastes:",
        "min": 0,
        "max": 10,
        "step": 1,
    },
}

def plot_post_process(ax):
    ax.set_ylim(ymin=0)
    ax.set_facecolor((0.9, 0.9, 0.9, 0.5))
    ax.legend(facecolor=(0.95, 0.95, 0.95, 0.5)) 

# Visualization component (only robots, no environment coloring)
SpaceGraph = make_space_component(agent_portrayal, {'rad_lvl' : {"colormap":'coolwarm', 'alpha':.25, "colorbar":True}})
NbWastesPlot = make_plot_component({"Nb_green_wastes":"green", "Nb_yellow_wastes":"gold", "Nb_red_wastes":"red"}, post_process=plot_post_process)

page = SolaraViz(
    model1,
    components=[SpaceGraph, NbWastesPlot],
    model_params=model_params,
    name="Robot Waste Cleanup Simulation",
)

page

# to start : "solara run MAS/server.py"