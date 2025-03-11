# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa

class RobotAgent(mesa.Agent):
    def __init__(self, model:mesa.Model):
        """initialize a RobotAgent instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.knowledge = {
            "actions" : [],
            "percept" : [],
            "grid_width" : self.model.width,
            "grid_height" : self.model.height,
        }

    def percepts(self):
        # Percieve the surronding environment and update its knowledge
        contents = self.model.grid.get_cell_list_contents([self.pos])
        self.knowledge.update()

    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def do(self):
        # Inform the environment about the chosen action
        self.percepts()
        action = self.deliberate()

class GreenRobot(RobotAgent):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model):
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)

    def __repr__(self):
        return f'Green robot at position ({self.pos[0]}, {self.pos[1]})'

class YellowRobot(RobotAgent):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""

    def __init__(self, model:mesa.Model):
        """initialize a YellowRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)

    def __repr__(self):
        return f'Yellow robot at position ({self.pos[0]}, {self.pos[1]})'

class RedRobot(RobotAgent):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model:mesa.Model):
        """initialize a RedRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)

    def __repr__(self):
        return f'Red robot at position ({self.pos[0]}, {self.pos[1]})'