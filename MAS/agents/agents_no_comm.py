# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from objects import WasteAgent, WasteDisposalZone
from actions import sim_move
from agents.agents_base import GreenRobot, YellowRobot, RedRobot

class GreenRobotNoComm(GreenRobot):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        
    def deliberate(self) -> tuple[str, str | int | None]:
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
        
        # Drop combined_waste (yellow) at zone border
        if any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]):
            if current_pos[0] == self.knowledge["grid_width"] // 3 - 1:
                return "drop", "yellow"
            # Move to the border
            else:
                return "move", "E"
        
        possible_positions = {direction : sim_move(self, direction) for direction in ["N", "S", "E", "W"]}
        # GreenRobot zone is restricted to the left part
        is_in_restricted_zone = lambda pos : pos[0] < self.knowledge["grid_width"] // 3

        safe_dirs = [direction for direction, new_pos in  possible_positions.items()
                           if new_pos in perceptions and is_in_restricted_zone(new_pos) and perceptions[new_pos]['rad_level'] <= 0.33]
       
        safe_dirs_nb_visit = {direction : perceptions[possible_positions[direction]]['nb_times_visited'] for direction in safe_dirs}
        min_nb_visit = min(safe_dirs_nb_visit.values())
        move_direction = self.random.choice([safe_dir for safe_dir, nb_visit in safe_dirs_nb_visit.items() if nb_visit == min_nb_visit])
        return "move", move_direction
 

    def __repr__(self) -> str:
        return f'Green robot at position ({self.pos[0]}, {self.pos[1]})'

class YellowRobotNoComm(YellowRobot):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a YellowRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        
    def deliberate(self)-> tuple[str, str | int | None]:
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
        
        # Drop combined_waste (red) at zone border
        if any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]):
            if current_pos[0] == (self.knowledge["grid_width"] // 3) * 2 - 1:
                return "drop", "red"
            # Move to the border
            else:
                return "move", "E"
        
        possible_positions = {direction : sim_move(self, direction) for direction in ["N", "S", "E", "W"]}
        # YellowRobot zone is restricted to the middle part
        is_in_restricted_zone = lambda pos : (pos[0] >= self.knowledge["grid_width"] // 3 - 1) and (pos[0] < 2 * self.knowledge["grid_width"] // 3)
        safe_directions = [direction for direction, new_pos in  possible_positions.items()
                           if new_pos in perceptions and is_in_restricted_zone(new_pos) and perceptions[new_pos]['rad_level'] <= 0.66]
        move_direction = self.random.choice(safe_directions)
        return "move", move_direction

    def __repr__(self) -> str:
        return f'Yellow robot at position ({self.pos[0]}, {self.pos[1]})'

class RedRobotNoComm(RedRobot):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a RedRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green, yellow or red zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
       
        can_get_red_waste = any(isinstance(obj, WasteAgent) and obj.waste_type == 'red' 
                                  for obj in perceptions[current_pos]['content'])
        if can_get_red_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "red"
        
        # Drop red waste at zone border
        if any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]):
            if any(isinstance(obj, WasteDisposalZone) for obj in perceptions[current_pos]['content']):
                return "drop", "red"
            # Move to the waste disposal zone
            else:
                return "move", "E"
        
        possible_positions = {direction : sim_move(self, direction) for direction in ["N", "S", "E", "W"]}
        # RedRobot zone is restricted to the right part
        is_in_restricted_zone = lambda pos : (pos[0] >= 2 * self.knowledge["grid_width"] // 3 - 1)
        safe_directions = [direction for direction, new_pos in  possible_positions.items()
                           if new_pos in perceptions and is_in_restricted_zone(new_pos)]
        move_direction = self.random.choice(safe_directions)
        return "move", move_direction

    def __repr__(self) -> str:
        return f'Red robot at position ({self.pos[0]}, {self.pos[1]})'