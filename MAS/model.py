# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import numpy as np
import warnings
import mesa
from objects import WasteAgent, Radioactivity, WasteDisposalZone
import actions as act

from agents.agents_base import RobotAgent, GreenRobot, YellowRobot, RedRobot

from agents.agents_no_comm import GreenRobotNoComm, YellowRobotNoComm, RedRobotNoComm
from agents.agents_with_comm import GreenRobotWithComm, YellowRobotWithComm, RedRobotWithComm

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

ROBOT_TYPE_TO_CLASSES = {
    "No communication": {
        "green": GreenRobotNoComm,
        "yellow": YellowRobotNoComm,
        "red": RedRobotNoComm
    },
    "With communication": {
        "green": GreenRobotWithComm,
        "yellow": YellowRobotWithComm,
        "red": RedRobotWithComm
    }
}

def get_nb_wastes(model):
    nb_green, nb_yellow, nb_red = 0, 0, 0
    for waste_agent in model.wastes:
        if waste_agent.waste_type == "green":
            nb_green += 1
        elif waste_agent.waste_type == "yellow":
            nb_yellow += 1
        elif waste_agent.waste_type == "red":
            nb_red += 1
    return (nb_green, nb_yellow, nb_red)

class RobotMission(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, 
                 robot_type="No communication",
                 nb_green_robots:int = 2,
                 nb_yellow_robots:int = 2,
                 nb_red_robots:int = 2,
                 nb_green_wastes:int = 6,
                 nb_yellow_wastes:int = 1,
                 nb_red_wastes:int = 1,
                 width:int = 10,
                 height:int = 10,
                 seed:int = None
                 ) -> None:
        """Initialize a RobotMission instance.
    
        Args:
            N: The number of agents per radioactivity zone.
            width: width of the grid.
            height: Height of the grid.
        """
        super().__init__(seed=seed)
        assert robot_type in ROBOT_TYPE_TO_CLASSES, f"robot_type must be in {ROBOT_TYPE_TO_CLASSES.keys()}"
        self.robot_type = robot_type
        self.nb_green_robots = nb_green_robots
        self.nb_yellow_robots = nb_yellow_robots
        self.nb_red_robots = nb_red_robots
        self.nb_green_wastes = nb_green_wastes
        self.nb_yellow_wastes = nb_yellow_wastes
        self.nb_red_wastes = nb_red_wastes
        self.width = width
        self.height = height
        self.zone_bounds = {
            'green' : [(0, width // 3 - 1), (0, height - 1)],
            'yellow' : [(width // 3, 2 * width // 3 - 1), (0, height - 1)],
            'red' : [(2 * width // 3, width - 1), (0, height - 1)]
            }
        
        self.reset()
    
    def reset(self) -> None:
        """Reset the model to its initial state."""
        
        self.rad_levels = mesa.space.PropertyLayer('rad_lvl', self.width, self.height, 0.0, dtype=float)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False, property_layers=[self.rad_levels])
        
        self.datacollector = mesa.DataCollector(model_reporters={"Nb_green_wastes": self.get_nb_green_wastes,
                                                                 "Nb_yellow_wastes": self.get_nb_yellow_wastes,
                                                                 "Nb_red_wastes": self.get_nb_red_wastess})
        
        self.is_cleaned = False
        self.robot_agents = [] # list of RobotAgents that interact in the RobotMission
        self.wastes = [] # list of WasteAgent to eliminate
        self.disposal_zones = [] # list of WasteDisposalZone tiles
        self.rad_map = np.full((self.height, self.width), None, dtype=Radioactivity) # grid of Radiactivity objects
        
        # Initialize each zone
        for zone, nb_wastes in zip(self.zone_bounds, [self.nb_green_wastes, self.nb_yellow_wastes, self.nb_red_wastes]):
            bounds = self.zone_bounds[zone]
            x_min, x_max = bounds[0]
            y_min, y_max = bounds[1]
        
            # Fill each tile of the zone with a Radioactivity
            self.fill_radioactivity(zone, x_min, x_max, y_min, y_max)

            # Create and place WasteAgents in the zone
            self.create_and_place_wastes(nb_wastes, zone, x_min, x_max, y_min, y_max)
            
            # Set up the waste disposal zone
            self.set_up_disposal_zone()

            # Create agents
            if zone == 'green':
                nb_robots = self.nb_green_robots
                agents = ROBOT_TYPE_TO_CLASSES[self.robot_type]["green"].create_agents(model=self, n=nb_robots)
            elif zone == 'yellow':
                nb_robots = self.nb_yellow_robots
                agents = ROBOT_TYPE_TO_CLASSES[self.robot_type]["yellow"].create_agents(model=self, n=nb_robots)
            elif zone == 'red':
                nb_robots = self.nb_red_robots
                agents = ROBOT_TYPE_TO_CLASSES[self.robot_type]["red"].create_agents(model=self, n=nb_robots)
            self.robot_agents += agents
            
            # Create x and y positions for agents
            x = self.rng.integers(x_min, x_max + 1, size=(nb_robots,))
            y = self.rng.integers(y_min, y_max + 1, size=(nb_robots,))
            
            for a, i, j in zip(agents, x, y):
                # Add the agent to a random grid cell
                self.grid.place_agent(a, (i, j))
        
        self.steps = 0
        
    def is_mission_terminated(self) -> bool:
        return self.is_cleaned
    
    def get_steps(self) -> int:
        return self.steps
      
    def set_radioactivity(self, pos:tuple[int, int], radiactivity:Radioactivity) -> None:
        x, y = pos
        i, j = y, self.height - 1 - x
        self.rad_map[i, j] = radiactivity
        
    def get_radioactivity(self, pos:tuple[int, int]) -> Radioactivity:
        x, y = pos
        i, j = y, self.height - 1 - x
        return self.rad_map[i, j]
    
    def get_nb_green_wastes(self) -> int:
        return sum(waste.waste_type == "green" for waste in self.wastes)
    
    def get_nb_yellow_wastes(self) -> int:
        return sum(waste.waste_type == "yellow" for waste in self.wastes)

    def get_nb_red_wastess(self) -> int:
        return sum(waste.waste_type == "red" for waste in self.wastes)
          
    def fill_radioactivity(self, zone_type:str, x_min:int, x_max:int, y_min:int, y_max:int) -> None:
        """Fill each of tiles in RobotMission grid[x_min:x_max + 1, y_min:y_max + 1] with RadioactivityAgents.
    
        Args:
            zone_type: The type of zone, inducing the random radioactivity_level.
            x_min: lower bound of the sliced grid x axis.
            x_max: upper bound (included) of the sliced grid x axis.
            y_min: lower bound of the sliced grid y axis.
            y_max: upper bound (included) of the sliced grid y axis.
        """
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                radiactivity = Radioactivity(self, zone_type)
                self.rad_levels.set_cell((x, y), radiactivity.radioactivity_level)
                self.set_radioactivity((x, y), radiactivity)
                
    def create_and_place_wastes(self, nb_wastes:int, waste_type:str, x_min:int, x_max:int, y_min:int, y_max:int) -> None:
        """Create nb_wastes WasteAgents and place them randomly in grid[x_min:x_max + 1, y_min:y_max + 1].
    
        Args:
            nb_wastes: The number of WasteAgents to create.
            waste_type: The type of waste ("green", "yellow" or "red").
            x_min: lower bound of the sliced grid x axis.
            x_max: upper bound (included) of the sliced grid x axis.
            y_min: lower bound of the sliced grid y axis.
            y_max: upper bound (included) of the sliced grid y axis.
        """
        for _ in range(nb_wastes):
            x = self.rng.integers(x_min, x_max + 1)
            y = self.rng.integers(y_min, y_max + 1)
            waste_agent = WasteAgent(self, waste_type)
            self.grid.place_agent(waste_agent, (x, y))
            
    def set_up_disposal_zone(self) -> None:
        """Set WasteDisposalZone agents on the rightmost column of the grid."""
        for y in range(self.height):
            disposal_tile = WasteDisposalZone(self)
            self.grid.place_agent(disposal_tile, (self.width - 1, y))
        
    def add_waste(self, waste:WasteAgent) -> None:
        """keep track of the new WasteAgents"""
        self.wastes.append(waste)
        
    def remove_waste(self, waste:WasteAgent) -> None:
        """Delete the WasteAgent"""
        self.wastes.remove(waste)
        
    def add_disposal_zone(self, disposal_zone:WasteDisposalZone) -> None:
        """keep track of the new WasteDisposalZone"""
        self.disposal_zones.append(disposal_zone)

    def step(self) -> None:
        """do one step of the model"""
        if self.steps == 1:
            # Initial state of the RobotMission
            self.datacollector.collect(self)

        for agent in self.random.sample(self.robot_agents, len(self.robot_agents)):
            action, *action_desc = agent.do()
            self.do(agent, action, *action_desc)
        
        if get_nb_wastes(self) == (0, 0, 0):
            self.is_cleaned = True
        
        self.datacollector.collect(self)
        
    def do(self, agent:RobotAgent, action:str, *action_desc:int | float | None) -> None:
        if action == "move":
            if len(action_desc) < 1:
                return
            direction = action_desc[0]
            new_pos = act.sim_move(agent, direction)
            # CHECK IF THE ACTION IS FEASIBLE
            if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[1] >= self.height:
                return
            ## IF FEASIBLE, PERFORM THE ACTION 
            # TODO : destroy agent if agent in wrong zone
            act.ACTIONS["move"](self, agent, direction)
                
        elif action == "pick_up":
            if len(action_desc) < 1:
                return
            target_waste_type = action_desc[0]
            # CHECK IF THE ACTION IS FEASIBLE
            if len(agent.collected_wastes) >= 2:
                return
            if (target_waste_type == "red" and isinstance(agent, (GreenRobot))):
                return
            ## IF FEASIBLE, PERFORM THE ACTION 
            for other_agent in self.grid.get_cell_list_contents([agent.pos]):
                if isinstance(other_agent, WasteAgent) and other_agent.waste_type == target_waste_type:
                    act.ACTIONS["pick_up"](self, agent, other_agent)
                    
        elif action == "combine_wastes":
            if len(action_desc) < 2:
                return
            waste_type_1, waste_type_2 = action_desc[0], action_desc[1]
            # CHECK IF THE ACTION IS FEASIBLE
            if waste_type_1 != waste_type_2 or waste_type_1 == "red":
                return
            target_waste_type = waste_type_1
            target_wastes_index = [i for i, waste in enumerate(agent.collected_wastes) if waste.waste_type == target_waste_type][:2]
            if len(target_wastes_index) < 2:
                return
            ## IF FEASIBLE, PERFORM THE ACTION 
            if target_waste_type == "green":
                combined_waste_type = "yellow"
            else:
                combined_waste_type = "red"
            waste_1 = agent.collected_wastes[target_wastes_index[0]]
            waste_2 = agent.collected_wastes[target_wastes_index[1]]
            act.ACTIONS["combine_wastes"](self, agent, waste_1, waste_2, combined_waste_type)
            
        elif action == "drop":
            if len(action_desc) < 1:
                return
            target_waste_type = action_desc[0]
            # CHECK IF THE ACTION IS FEASIBLE
            target_wastes_index = [i for i, waste in enumerate(agent.collected_wastes) if waste.waste_type == target_waste_type][:1]
            if len(target_wastes_index) < 1:
                return
            ## IF FEASIBLE, PERFORM THE ACTION
            waste = agent.collected_wastes[target_wastes_index[0]]
            act.ACTIONS["drop"](self, agent, waste)
            
            # Delete the red wastes in the disposal zone
            if target_waste_type == "red" and any(waste.pos == disposal_zone.pos for disposal_zone in self.disposal_zones):
                self.grid.remove_agent(waste)
                self.remove_waste(waste)