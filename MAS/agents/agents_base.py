# GROUP : 23
# DATE : 21.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa

class RobotAgent(mesa.Agent):
    def __init__(self, model:mesa.Model) -> None:
        """initialize a RobotAgent instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.collected_wastes = []
        self.knowledge = {
            "current_pos" : None,
            "actions" : [],
            "perceptions" : {},
            "collected_wastes": [],
            "grid_width" : self.model.width,
            "grid_height" : self.model.height,
        }

    def percepts(self) -> None:
        # Percieve the surronding environment and update its knowledge
        # Update agent knowledge regarding the collected wastes
        self.knowledge["collected_wastes"] = self.collected_wastes.copy()
        current_pos = self.pos
        self.knowledge["current_pos"] = current_pos
       
        # Perception of surronding cells
        neighbour_cells = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=True
            )
        for ngb_pos in neighbour_cells:
            if not ngb_pos in self.knowledge["perceptions"]:
                self.knowledge["perceptions"][ngb_pos] = {
                    'rad_level' : float(self.model.get_radioactivity(ngb_pos)),
                    'content' : [],
                    'nb_times_visited' : 0,
                    }
           
            # Update the perception of the cell
            new_content = []
            for other_agent in self.model.grid.get_cell_list_contents([ngb_pos]):
                new_content.append(other_agent)
               
            self.knowledge["perceptions"][ngb_pos]['content'] = new_content
       
        # Update the number of times the agent cell has been visited
        self.knowledge["perceptions"][current_pos]['nb_times_visited'] += 1
 
 
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Specific to the Robot type
        pass

    def do(self) -> tuple[str, str | int | None]:
        # Inform the environment about the chosen action
        self.percepts()
        action, *action_desc = self.deliberate()
        # Keep track of actions taken
        self.knowledge["actions"].append((action, *action_desc))
        return action, *action_desc

class GreenRobot(RobotAgent):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)

    def __repr__(self) -> str:
        return f'Green robot at position ({self.pos[0]}, {self.pos[1]})'

class YellowRobot(RobotAgent):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a YellowRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)

    def __repr__(self) -> str:
        return f'Yellow robot at position ({self.pos[0]}, {self.pos[1]})'

class RedRobot(RobotAgent):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a RedRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)

    def __repr__(self) -> str:
        return f'Red robot at position ({self.pos[0]}, {self.pos[1]})'