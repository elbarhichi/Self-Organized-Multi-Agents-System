# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from agents import RobotAgent, GreenRobot, YellowRobot, RedRobot
from objects import WasteAgent, RadioactivityAgent, WasteDisposalZone
import actions as act

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
                 nb_green_robots=2,
                 nb_yellow_robots=2,
                 nb_red_robots=2,
                 nb_green_wastes=6,
                 nb_yellow_wastes=1,
                 nb_red_wastes=1, 
                 width=10, 
                 height=10, 
                 max_steps=20, 
                 seed=None):
        """Initialize a RobotMission instance.
    
        Args:
            N: The number of agents per radioactivity zone.
            width: width of the grid.
            height: Height of the grid.
        """
        super().__init__(seed=seed)
        self.nb_green_robots = nb_green_robots
        self.nb_yellow_robots = nb_yellow_robots
        self.nb_red_robots = nb_red_robots
        self.nb_green_wastes = nb_green_wastes
        self.nb_yellow_wastes = nb_yellow_wastes
        self.nb_red_wastes = nb_red_wastes
        self.width = width
        self.height = height
        self.max_steps = max_steps
        self.zone_bounds = {
            'green' : [(0, width // 3 - 1), (0, height - 1)],
            'yellow' : [(width // 3, 2 * width // 3 - 1), (0, height - 1)],
            'red' : [(2 * width // 3, width - 1), (0, height - 1)]
            }
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        
        self.robot_agents = [] # list of RobotAgents that interact in the RobotMission
        self.wastes = [] # list of WasteAgent to eliminate
        self.disposal_zones = [] # list of WasteDisposalZone tiles

        # Initialize each zone
        for zone, nb_wastes in zip(self.zone_bounds, [nb_green_wastes, nb_yellow_wastes, nb_red_wastes]):
            bounds = self.zone_bounds[zone]
            x_min, x_max = bounds[0]
            y_min, y_max = bounds[1]
        
            # Fill each tile of the zone with a RadioactivityAgent
            self.fill_radiactivity(zone, x_min, x_max, y_min, y_max)
            
            # Create and place WasteAgents in the zone
            self.create_and_place_wastes(nb_wastes, zone, x_min, x_max, y_min, y_max)
            
            # Set up the waste disposal zone
            self.set_up_disposal_zone()

            # Create agents
            if zone == 'green':
                nb_robots = nb_green_robots
                agents = GreenRobot.create_agents(model=self, n=nb_robots)
            elif zone == 'yellow':
                nb_robots = nb_yellow_robots
                agents = YellowRobot.create_agents(model=self, n=nb_robots)
            elif zone == 'red':
                nb_robots = nb_red_robots
                agents = RedRobot.create_agents(model=self, n=nb_robots)
            self.robot_agents += agents
            
            # Create x and y positions for agents
            x = self.rng.integers(x_min, x_max + 1, size=(nb_robots,))
            y = self.rng.integers(y_min, y_max + 1, size=(nb_robots,))
            
            for a, i, j in zip(agents, x, y):
                # Add the agent to a random grid cell
                self.grid.place_agent(a, (i, j))
        
        # DEBUG
        # for agent in self.agents:
        #     print(agent)

        self.datacollector = mesa.DataCollector(model_reporters={"Nb_wastes": get_nb_wastes})
        
    def fill_radiactivity(self, zone_type, x_min, x_max, y_min, y_max):
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
                radiactivity_agent = RadioactivityAgent(self, zone_type)
                self.grid.place_agent(radiactivity_agent, (x, y))
                
    def create_and_place_wastes(self, nb_wastes, waste_type, x_min, x_max, y_min, y_max):
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
            
    def set_up_disposal_zone(self):
        for y in range(self.height):
            disposal_tile = WasteDisposalZone(self)
            self.grid.place_agent(disposal_tile, (self.width - 1, y))
        
    def add_waste(self, waste:WasteAgent):
        """keep track of the new WasteAgents"""
        self.wastes.append(waste)
        
    def add_disposal_zone(self, disposal_zone:WasteDisposalZone):
        """keep track of the new WasteDisposalZone"""
        self.disposal_zones.append(disposal_zone)

    def step(self):
        """do one step of the model"""
        if self.steps == 1:
            # Initial state of the RobotMission
            self.datacollector.collect(self)

        for agent in self.random.sample(self.robot_agents, len(self.robot_agents)):  
            action, *action_desc = agent.do()
            self.do(agent, action, *action_desc)
        
        self.datacollector.collect(self)
        
    def do(self, agent:RobotAgent, action:callable, *action_desc:int|float|None):
        if action == "move":
            if len(action_desc) < 1:
                return
            direction = action_desc[0]
            new_pos = act.sim_move(agent, direction)
            # CHECK IF THE ACTION IS FEASIBLE
            if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] <0 or new_pos[1] >= self.height:
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