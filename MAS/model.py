# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from agents import GreenRobot, YellowRobot, RedRobot
from objects import WasteAgent, RadioactivityAgent

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

    def __init__(self, num_robots=2, width=10, height=10, max_steps=20, seed=None):
        """Initialize a RobotMission instance.
    
        Args:
            N: The number of agents per radioactivity zone.
            width: width of the grid.
            height: Height of the grid.
        """
        super().__init__(seed=seed)
        self.num_robots = num_robots
        self.width = width
        self.height = height
        self.max_steps = max_steps
        self.zone_bounds = {
            'green' : [(0, width // 3), (0, height - 1)],
            'yellow' : [(width // 3 + 1, 2 * width // 3), (0, height - 1)],
            'red' : [(2 * width // 3 + 1, width - 1), (0, height - 1)]
            }
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        
        self.robot_agents = [] # list of RobotAgents that interact in the RobotMission
        self.wastes = [] # list of WasteAgent to eliminate

        # Initialize each zone
        for zone in self.zone_bounds:
            bounds = self.zone_bounds[zone]
            x_min, x_max = bounds[0]
            y_min, y_max = bounds[1]
        
            # Create agents
            if zone == 'green':
                agents = GreenRobot.create_agents(model=self, n=num_robots)
                self.fill_radiactivity('green', x_min, x_max, y_min, y_max)
            elif zone == 'yellow':
                agents = YellowRobot.create_agents(model=self, n=num_robots)
                self.fill_radiactivity('yellow', x_min, x_max, y_min, y_max)
            elif zone == 'red':
                agents = RedRobot.create_agents(model=self, n=num_robots)
                self.fill_radiactivity('red', x_min, x_max, y_min, y_max)
            self.robot_agents += agents
        
            # Create x and y positions for agents
            x = self.rng.integers(x_min, x_max + 1, size=(num_robots,))
            y = self.rng.integers(y_min, y_max + 1, size=(num_robots,))
            
            for a, i, j in zip(agents, x, y):
                # Add the agent to a random grid cell
                self.grid.place_agent(a, (i, j))

        self.datacollector = mesa.DataCollector(model_reporters={"Nb_wastes": get_nb_wastes})
        
    def fill_radiactivity(self, zone_type, x_min, x_max, y_min, y_max):
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                radiactivity_agent = RadioactivityAgent(self, zone_type)
                self.grid.place_agent(radiactivity_agent, (x, y))
        
    def add_waste(self, waste:WasteAgent):
        self.wastes.append(waste)

    def step(self):
        """do one step of the model"""
        if self.steps == 1:
            # Initial state of the RobotMission
            self.datacollector.collect(self)

        for agent in self.random.sample(self.robot_agents, len(self.robot_agents)):  
            agent.do()
        self.datacollector.collect(self)