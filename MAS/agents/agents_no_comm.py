# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa
from objects import WasteAgent, WasteDisposalZone
from actions import sim_move, is_pos_in_bounds, dir_to_inbounds
from agents.agents_base import GreenRobot, YellowRobot, RedRobot

class GreenRobotNoComm(GreenRobot):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model)
        self.hold_timer = {}            # WasteAgent -> hold steps
        self.waste_origins = {}         # WasteAgent -> position where picked up
        self.max_hold_steps = 30        # N steps before dropping
        self.recently_dropped = {}      # WasteAgent -> cooldown counter
        self.drop_cooldown = 15          # Steps to avoid re-picking a dropped waste
        
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # Update hold timers for held wastes
        for waste in self.collected_wastes:
            self.hold_timer[waste] = self.hold_timer.get(waste, 0) + 1
        
        # Decay recently_dropped cooldown
        to_remove = []
        for waste, cooldown in self.recently_dropped.items():
            if cooldown <= 1:
                to_remove.append(waste)
            else:
                self.recently_dropped[waste] -= 1
        for waste in to_remove:
            del self.recently_dropped[waste]

        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]))
        
        # Try to combine if 2 green wastes
        if sum(waste.waste_type == "green" for waste in self.knowledge["collected_wastes"]) >= 2:
            return "combine_wastes", "green", "green"
        
        # Drop uncombined waste if held too long and at border or origin
        border_x = self.knowledge["grid_width"] // 3 - 1
        for waste in self.collected_wastes:
            if waste.waste_type == "green" and self.hold_timer.get(waste, 0) > self.max_hold_steps:
                at_border = current_pos[0] == border_x
                at_origin = self.waste_origins.get(waste) == current_pos
                if at_border or at_origin:
                    self.recently_dropped[waste] = self.drop_cooldown  # add to cooldown list
                    return "drop", waste.waste_type
                
        # Try to pick up green waste (not recently dropped)
        if len(self.collected_wastes) < 2:
            for obj in self.model.grid.get_cell_list_contents([current_pos]):
                if isinstance(obj, WasteAgent) and obj.waste_type == "green" and obj not in self.recently_dropped:
                    self.waste_origins[obj] = current_pos
                    return "pick_up", "green"
        
        # Drop combined_waste (yellow) at zone border
        if any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]):
            if current_pos[0] == self.knowledge["grid_width"] // 3 - 1:
                return "drop", "yellow"
            # Move to the border
            else:
                return "move", "E"
        
        # If holding 1 green waste, search for another green
        if sum(waste.waste_type == "green" for waste in self.collected_wastes) == 1:
            other_green_pos = [
                pos for pos, content in perceptions.items()
                if any(wt == 'green' for wt in content['wastes']) and not any(
                    isinstance(obj, WasteAgent) and obj in self.recently_dropped
                    for obj in self.model.grid.get_cell_list_contents([pos])
                )
            ]
            if other_green_pos:
                closest = min(other_green_pos, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
                return "move", self.dir_to_target(closest)
        
        # Look for wastes to pick up  (ignoring recently dropped)
        target_wastes_pos = [
            pos for pos, content in perceptions.items()
            if any(wt == 'green' for wt in content['wastes'])
            and not any(
                isinstance(obj, WasteAgent) and obj in self.recently_dropped
                for obj in self.model.grid.get_cell_list_contents([pos])
            )
        ]

        # Move to the closest waste seen
        if len(target_wastes_pos) > 0:
            closest_waste_pos = min(target_wastes_pos, key=lambda pos: abs(pos[0] - current_pos[0]) + abs(pos[1] - current_pos[1]))
            move_direction = self.dir_to_target(closest_waste_pos)
            return "move", move_direction
        
        # If no waste seen, explore randomly
        move_direction = self.random_exploration_dir()
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
        self.hold_timer = {}
        self.waste_origins = {}
        self.max_hold_steps = 30
        self.recently_dropped = {}
        self.drop_cooldown = 15
        
    def deliberate(self)-> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green or yellow zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]

        # Update hold timers for held wastes
        for waste in self.collected_wastes:
            self.hold_timer[waste] = self.hold_timer.get(waste, 0) + 1

        # Decay recently_dropped cooldown
        to_remove = []
        for waste, cooldown in self.recently_dropped.items():
            if cooldown <= 1:
                to_remove.append(waste)
            else:
                self.recently_dropped[waste] -= 1
        for waste in to_remove:
            del self.recently_dropped[waste]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]))
        
        # Combine if holding 2 yellow
        if sum(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]) >= 2:
            return "combine_wastes", "yellow", "yellow"
        
        # Drop uncombined waste if held too long and at border or origin
        border_x = (self.knowledge["grid_width"] // 3) * 2 - 1
        for waste in self.collected_wastes:
            if waste.waste_type == "yellow" and self.hold_timer.get(waste, 0) > self.max_hold_steps:
                at_border = current_pos[0] == border_x
                at_origin = self.waste_origins.get(waste) == current_pos
                if at_border or at_origin:
                    self.recently_dropped[waste] = self.drop_cooldown
                    return "drop", waste.waste_type
       
       # Try to pick up yellow waste (not recently dropped)
        if len(self.collected_wastes) < 2:
            for obj in self.model.grid.get_cell_list_contents([current_pos]):
                if isinstance(obj, WasteAgent) and obj.waste_type == "yellow" and obj not in self.recently_dropped:
                    self.waste_origins[obj] = current_pos
                    return "pick_up", "yellow"
        
        # Drop combined_waste (red) at zone border
        if any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]):
            if current_pos[0] == (self.knowledge["grid_width"] // 3) * 2 - 1:
                return "drop", "red"
            # Move to the border
            else:
                return "move", "E"
        
        # If holding 1 yellow waste, search for another yellow
        if sum(waste.waste_type == "yellow" for waste in self.collected_wastes) == 1:
            other_yellow_pos = [
                pos for pos, content in perceptions.items()
                if any(wt == 'yellow' for wt in content['wastes']) and not any(
                    isinstance(obj, WasteAgent) and obj in self.recently_dropped
                    for obj in self.model.grid.get_cell_list_contents([pos])
                )
            ]
            if other_yellow_pos:
                closest = min(other_yellow_pos, key=lambda p: abs(p[0] - current_pos[0]) + abs(p[1] - current_pos[1]))
                return "move", self.dir_to_target(closest)
            
        # Look for yellow wastes to pick up (ignoring recently dropped)
        target_wastes_pos = [
            pos for pos, content in perceptions.items()
            if any(wt == 'yellow' for wt in content['wastes'])
            and not any(
                isinstance(obj, WasteAgent) and obj in self.recently_dropped
                for obj in self.model.grid.get_cell_list_contents([pos])
            )
        ]

        # Move to the closest waste seen
        if len(target_wastes_pos) > 0:
            closest_waste_pos = min(target_wastes_pos, key=lambda pos: abs(pos[0] - current_pos[0]) + abs(pos[1] - current_pos[1]))
            move_direction = self.dir_to_target(closest_waste_pos)
            return "move", move_direction
        
        x_min = self.knowledge["grid_width"] // 3 - 1
        
        # If no waste seen:
        
        if not(is_pos_in_bounds(current_pos, x_min=x_min)):
            # get back in exploration bounds
            move_direction = dir_to_inbounds(current_pos, x_min=x_min)
        else:
            # explore randomly in exploration bounds
            move_direction = self.random_exploration_dir(x_min=x_min)
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
       
        can_get_red_waste = any(waste_type == 'red' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_red_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "red"
        
        # Drop red waste at zone border
        if any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]):
            if any(isinstance(obj, WasteDisposalZone) for obj in perceptions[current_pos]['other_agents']):
                return "drop", "red"
            # Move to the waste disposal zone
            else:
                return "move", "E"
            
        # Look for wastes to pick up
        target_wastes_pos = [pos for pos, content in perceptions.items() if any(waste_type == 'red' for waste_type in content['wastes'])]
        
        # Move to the closest waste seen
        if len(target_wastes_pos) > 0:
            closest_waste_pos = min(target_wastes_pos, key=lambda pos: abs(pos[0] - current_pos[0]) + abs(pos[1] - current_pos[1]))
            move_direction = self.dir_to_target(closest_waste_pos)
            return "move", move_direction
        
        x_min = self.knowledge["grid_width"] // 3 * 2 - 1
        x_max = self.knowledge["grid_width"] - 2
        
        # If no waste seen:
        
        if not(is_pos_in_bounds(current_pos, x_min=x_min, x_max=x_max)):
            # get back in exploration bounds
            move_direction = dir_to_inbounds(current_pos, x_min=x_min, x_max=x_max)
        else:
            # explore randomly in exploration bounds
            move_direction = self.random_exploration_dir(x_min=x_min, x_max=x_max)
        return "move", move_direction

    def __repr__(self) -> str:
        return f'Red robot at position ({self.pos[0]}, {self.pos[1]})'