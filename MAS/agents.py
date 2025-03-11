# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from model import RobotMission

class GreenRobot(mesa.Agent):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:RobotMission):
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.knwoledge = {}

    def percepts(self):
        # Percieve the surronding environment and update its knowledge
        pass

    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        pass

    def do(self):
        # Inform the environment about the chosen action
        self.percepts()
        action = self.deliberate()
        return action

class YellowRobot(mesa.Agent):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""

    def __init__(self, model:RobotMission):
        """initialize a YellowRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.knwoledge = {}

    def percepts(self):
        # Percieve the surronding environment and update its knowledge
        pass

    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        pass

    def do(self):
        # Inform the environment about the chosen action
        self.percepts()
        action = self.deliberate()
        return action

class RedRobot(mesa.Agent):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model:RobotMission):
        """initialize a RedRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.knwoledge = {}

    def percepts(self):
        # Percieve the surronding environment and update its knowledge
        pass

    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        pass

    def do(self):
        # Inform the environment about the chosen action
        self.percepts()
        action = self.deliberate()
        return action