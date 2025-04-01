# GROUP : 23
# DATE : 21.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from actions import sim_move, is_pos_in_bounds
from objects import WasteAgent

class RobotAgent(mesa.Agent):
    def __init__(self, model:mesa.Model) -> None:
        """initialize a RobotAgent instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.collected_wastes = []
        self.rad_resistance = 0
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
                    'wastes' : [],
                    'other_agents' : [],
                    'nb_times_visited' : 0,
                    }
            
            # Update the perception of the cell
            new_content = {
                'wastes' : [],
                'other_agents' : [],
                }
            for other_agent in self.model.grid.get_cell_list_contents([ngb_pos]):
                if other_agent == self:
                    continue
                if isinstance(other_agent, WasteAgent):
                    new_content['wastes'].append(other_agent.waste_type)
                else:
                    new_content['other_agents'].append(other_agent)
                
            self.knowledge["perceptions"][ngb_pos].update(new_content)
        
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
    
    def dir_to_target(self, target:tuple[int, int]) -> str:
        # Return the direction leading to the target
        current_pos = self.knowledge["current_pos"]
        x, y = current_pos
        x_target, y_target = target
        if y_target > y:
            return "N"
        elif y_target < y:
            return "S"
        elif x_target > x:
            return "E"
        return "W"
    
    def random_exploration_dir(self, x_min=None, x_max=None, y_min=None, y_max=None) -> str:
        # Return a random direction for exploration :
        # Safe direction leading to least visited ngb cell
        
        perceptions = self.knowledge["perceptions"]
        
        dir_to_pos = {direction : sim_move(self, direction) for direction in ["N", "S", "E", "W"]}
        safe_dirs = [direction for direction, new_pos in  dir_to_pos.items()
                           if new_pos in perceptions and perceptions[new_pos]['rad_level'] <= self.rad_resistance and is_pos_in_bounds(new_pos, x_min, x_max, y_min, y_max)]
        
        safe_dirs_nb_visit = {direction : perceptions[dir_to_pos[direction]]['nb_times_visited'] for direction in safe_dirs}
        min_nb_visit = min(safe_dirs_nb_visit.values())
        
        return self.random.choice([safe_dir for safe_dir, nb_visit in safe_dirs_nb_visit.items() if nb_visit == min_nb_visit])

class GreenRobot(RobotAgent):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.rad_resistance = 0.33

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
        self.rad_resistance = 0.66

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
        self.rad_resistance = 1.0

    def __repr__(self) -> str:
        return f'Red robot at position ({self.pos[0]}, {self.pos[1]})'