# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from objects import RadioactivityAgent, WasteAgent, WasteDisposalZone
from actions import sim_move

from collections.abc import Callable # For typing

class RobotAgent(mesa.Agent):
    def __init__(self, model:mesa.Model):
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
        self.knowledge["current_pos"] = self.pos
        
        # Perception of surronding cells
        neighbour_cells = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=True
            )
        for ngb_pos in neighbour_cells:
            ngb_perception = {'rad_level' : 1.0,
                              'content' : []
                              }
            for other_agent in self.model.grid.get_cell_list_contents([ngb_pos]):
                if isinstance(other_agent, RadioactivityAgent):
                    ngb_perception['rad_level'] = other_agent.radioactivity_level
                else:
                    ngb_perception['content'].append(other_agent)
            self.knowledge["perceptions"][ngb_pos] = ngb_perception

    def deliberate(self) -> tuple[Callable, str | int | None] | None:
        # Based on the current knowledge, choose an action to perform
        # Specific to the Robot type
        pass

    def do(self) -> None:
        # Inform the environment about the chosen action
        self.percepts()
        action, *action_desc = self.deliberate()
        # Keep track of actions taken
        self.knowledge["actions"].append((action, *action_desc))
        return action, *action_desc

class GreenRobot(RobotAgent):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model):
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        
    def deliberate(self) -> tuple[Callable, str | int | None] | None:
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]))
        
        if sum(waste.waste_type == "green" for waste in self.knowledge["collected_wastes"]) >= 2:
            return "combine_wastes", "green", "green"
       
        can_get_green_waste = any(isinstance(obj, WasteAgent) and obj.waste_type == 'green' 
                                  for obj in perceptions[current_pos]['content'])
        if can_get_green_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "green"
        
        # Drop combined_wastes at zone border
        if current_pos[0] == self.knowledge["grid_width"] // 3 - 1 and any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]):
            return "drop", "yellow"
        
        possible_positions = {direction : sim_move(self, direction) for direction in ["N", "S", "E", "W"]}
        # GreenRobot zone is restricted to the left part
        is_in_restricted_zone = lambda pos : pos[0] < self.knowledge["grid_width"] // 3
        safe_directions = [direction for direction, new_pos in  possible_positions.items()
                           if new_pos in perceptions and is_in_restricted_zone(new_pos) and perceptions[new_pos]['rad_level'] <= 0.33]
        move_direction = self.random.choice(safe_directions)
        return "move", move_direction

    def __repr__(self) -> str:
        return f'Green robot at position ({self.pos[0]}, {self.pos[1]})'

class YellowRobot(RobotAgent):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""

    def __init__(self, model:mesa.Model):
        """initialize a YellowRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        
    def deliberate(self)-> tuple[Callable, str | int | None] | None:
        # Based on the current knowledge, choose an action to perform
        # Random move in green or yellow zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]))
        
        if sum(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]) >= 2:
            return "combine_wastes", "yellow", "yellow"
       
        can_get_yellow_waste = any(isinstance(obj, WasteAgent) and obj.waste_type == 'yellow' 
                                  for obj in perceptions[current_pos]['content'])
        if can_get_yellow_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "yellow"
        
        # Drop combined_wastes at zone border
        if current_pos[0] == (self.knowledge["grid_width"] // 3) * 2 - 1 and any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]):
            return "drop", "red"
        
        possible_positions = {direction : sim_move(self, direction) for direction in ["N", "S", "E", "W"]}
        # YellowRobot zone is restricted to the middle part
        is_in_restricted_zone = lambda pos : (pos[0] >= self.knowledge["grid_width"] // 3 - 1) and (pos[0] < 2 * self.knowledge["grid_width"] // 3)
        safe_directions = [direction for direction, new_pos in  possible_positions.items()
                           if new_pos in perceptions and is_in_restricted_zone(new_pos) and perceptions[new_pos]['rad_level'] <= 0.66]
        move_direction = self.random.choice(safe_directions)
        return "move", move_direction

    def __repr__(self) -> str:
        return f'Yellow robot at position ({self.pos[0]}, {self.pos[1]})'

class RedRobot(RobotAgent):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model:mesa.Model):
        """initialize a RedRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        
    def deliberate(self) -> tuple[Callable, str | int | None] | None:
        # Based on the current knowledge, choose an action to perform
        # Random move in green, yellow or red zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
       
        can_get_red_waste = any(isinstance(obj, WasteAgent) and obj.waste_type == 'red' 
                                  for obj in perceptions[current_pos]['content'])
        if can_get_red_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "red"
        
        # Drop red waste at disposal zone
        if any(isinstance(obj, WasteDisposalZone) for obj in perceptions[current_pos]['content']) and any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]):
            return "drop", "red"
        
        possible_positions = {direction : sim_move(self, direction) for direction in ["N", "S", "E", "W"]}
        # RedRobot zone is restricted to the right part
        is_in_restricted_zone = lambda pos : (pos[0] >= 2 * self.knowledge["grid_width"] // 3 - 1)
        safe_directions = [direction for direction, new_pos in  possible_positions.items()
                           if new_pos in perceptions and is_in_restricted_zone(new_pos)]
        move_direction = self.random.choice(safe_directions)
        return "move", move_direction

    def __repr__(self) -> str:
        return f'Red robot at position ({self.pos[0]}, {self.pos[1]})'