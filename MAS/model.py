# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from agents import GreenRobot, YellowRobot, RedRobot

class RobotMission(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, n=2, width=10, height=10, seed=None):
        """Initialize a RobotMission instance.
    
        Args:
            N: The number of agents per radioactivity zone.
            width: width of the grid.
            height: Height of the grid.
        """
        super().__init__(seed=seed)
        self.num_agents = n
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        self.zones = {
            'green' : 
                {
                    'bounds' : [(0, width // 3), (0, height)],
                    'agents' : []
                },
            'yellow' : 
                {
                    'bounds' : [(width // 3 + 1, 2 * width // 3), (0, height)],
                    'agents' : []
                },
            'red' : 
                {
                    'bounds' : [(2 * width // 3 + 1, width), (0, height)],
                    'agents' : []
                }
            }

        # Initialize each zone
        for zone in self.zones:
            bounds = self.zones[zone]
            x_min, x_max = bounds[0]
            y_min, y_max = bounds[1]
        
            # Create agents
            if zone == 'green':
                agents = GreenRobot.create_agents(model=self, n=n)
            elif zone == 'yellow':
                agents = YellowRobot.create_agents(model=self, n=n)
            elif zone == 'red':
                agents = RedRobot.create_agents(model=self, n=n)
        
            # Create x and y positions for agents
            x = self.rng.integers(x_min, x_max, size=(n,))
            y = self.rng.integers(y_min, y_max, size=(n,))
            
            for a, i, j in zip(agents, x, y):
                # Add the agent to a random grid cell
                self.grid.place_agent(a, (i, j))

        self.datacollector = mesa.DataCollector()
        self.datacollector.collect(self)

    def step(self):
        """do one step of the model"""
        self.agents.shuffle_do("do")
        self.datacollector.collect(self)