# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from objects import RadioactivityAgent

def get_rad_lvl_from_knowledge(ngb_knowledge):
    for a in ngb_knowledge:
        if isinstance(a, RadioactivityAgent):
            return a.radioactivity_level
    return None

class RobotAgent(mesa.Agent):
    def __init__(self, model:mesa.Model):
        """initialize a RobotAgent instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.knowledge = {
            "actions" : [],
            "perceptions" : [],
            "grid_width" : self.model.width,
            "grid_height" : self.model.height,
        }

    def percepts(self):
        # TODO : change perception to be lighter -> rad_grid
        # Percieve the surronding environment and update its knowledge
        perception = {}
        # Perception of current cell
        current_contents = self.model.grid.get_cell_list_contents([self.pos])
        perception[self.pos] = current_contents
        # Perception of surronding cells
        neighbour_cells = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
        for ngb_pos in neighbour_cells:
            perception[ngb_pos] = self.model.grid.get_cell_list_contents([ngb_pos])
        # Update perception history
        self.knowledge["perceptions"].append(perception)

    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        # Specific to the Robot type
        pass

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
        
    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        cellmates_knowledge = self.knowledge["perceptions"][-1]
        safe_steps = [pos for pos in possible_steps if get_rad_lvl_from_knowledge(cellmates_knowledge[pos]) <= 0.33]
        new_position = self.random.choice(safe_steps)
        self.model.grid.move_agent(self, new_position)

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
        
    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        # Random move in green or yellow zone
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        cellmates_knowledge = self.knowledge["perceptions"][-1]
        safe_steps = [pos for pos in possible_steps if get_rad_lvl_from_knowledge(cellmates_knowledge[pos]) <= 0.66]
        new_position = self.random.choice(safe_steps)
        self.model.grid.move_agent(self, new_position)

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
        
    def deliberate(self):
        # Based on the current knowledge, choose an action to perform
        # Random move in green, yellow or red zone
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        cellmates_knowledge = self.knowledge["perceptions"][-1]
        safe_steps = possible_steps
        new_position = self.random.choice(safe_steps)
        self.model.grid.move_agent(self, new_position)

    def __repr__(self):
        return f'Red robot at position ({self.pos[0]}, {self.pos[1]})'