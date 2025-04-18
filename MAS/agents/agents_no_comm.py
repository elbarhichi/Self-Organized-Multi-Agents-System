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
        self.max_hold_steps = 30        # N steps before dropping
        # self.max_hold_steps = 100000        # N steps before dropping
        self.drop_cooldown = 15         # Steps to avoid re-picking a dropped waste
        
    def percepts(self):
        super().percepts() # Update knowledge on surrundings
        
        # Update robot knowledge based of last action success feedback
        action_success = self.knowledge["action_success"]
        last_action, *last_action_desc = self.knowledge["last_action"]
        
        if action_success:
            if last_action == "pick_up":
                waste_type = last_action_desc[0]
                self.knowledge["hold_timer"][waste_type] = 0
                self.knowledge["held_waste_origin"][waste_type] = self.pos
                
            elif last_action == "drop":
                waste_type = last_action_desc[0]
                if not waste_type in self.collected_wastes and waste_type in self.knowledge["hold_timer"]:
                    # Remove waste hold timer
                    del self.knowledge["hold_timer"][waste_type]
                if waste_type == self.target_waste_type:
                    # Add cooldown to drop location
                    # This is only for the target_waste_type
                    self.knowledge["recent_drop_pos"][self.pos] = self.drop_cooldown
            
            elif last_action == "combine_wastes":
                waste_type = last_action_desc[0]
                # Remove waste hold timer of previous wastes
                del self.knowledge["hold_timer"][waste_type]
        
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # Update the collected waste's hold timer
        for waste_type in self.knowledge["hold_timer"]:
            self.knowledge["hold_timer"][waste_type] += 1
            
        # Decay the target waste_type drop cooldown:
        to_delete = []
        for pos, cooldown in self.knowledge["recent_drop_pos"].items():
            if cooldown <= 1:
                to_delete.append(pos)
            else:
                self.knowledge["recent_drop_pos"][pos] -= 1
        for pos in to_delete:
            del self.knowledge["recent_drop_pos"][pos]

        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]))
        
        # Combine if holding 2 green wastes
        if self.get_nb_target_waste_held() >= 2:
            return "combine_wastes", "green", "green"
        
        # Drop uncombined waste if held too long and at border or origin
        border_x = self.knowledge["grid_width"] // 3 - 1
        for waste_type in self.knowledge["collected_wastes"]:
            if waste_type == "green" and self.knowledge["hold_timer"][waste_type] > self.max_hold_steps:
                at_border = current_pos[0] == border_x
                at_origin = self.knowledge["held_waste_origin"]["green"] == current_pos
                if at_border or at_origin:
                    return "drop", "green"

        # Pick up green waste (not recently dropped)
        can_get_green_waste = any(waste_type == 'green' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_green_waste and (not current_pos in self.knowledge["recent_drop_pos"]) and (len(self.knowledge["collected_wastes"]) < 2):
            return "pick_up", "green"
        
        # Drop combined_waste (yellow) at zone border
        if any(waste_type == "yellow" for waste_type in self.knowledge["collected_wastes"]):
            if current_pos[0] == self.knowledge["grid_width"] // 3 - 1:
                return "drop", "yellow"
            # Move to the border
            else:
                return "move", "E"
        
        # Look for wastes to pick up (ignoring recently dropped)
        target_wastes_pos = [pos for pos, content in perceptions.items() if any(waste_type == 'green' for waste_type in content['wastes'])
                             and (not pos in self.knowledge["recent_drop_pos"])]
        
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
        self.max_hold_steps = 30
        self.drop_cooldown = 15
        
    def percepts(self):
        super().percepts() # Update knowledge on surrundings
        
        # Update robot knowledge based of last action success feedback
        action_success = self.knowledge["action_success"]
        last_action, *last_action_desc = self.knowledge["last_action"]
        
        if action_success:
            if last_action == "pick_up":
                waste_type = last_action_desc[0]
                self.knowledge["hold_timer"][waste_type] = 0
                self.knowledge["held_waste_origin"][waste_type] = self.pos
                
            elif last_action == "drop":
                waste_type = last_action_desc[0]
                if not waste_type in self.collected_wastes and waste_type in self.knowledge["hold_timer"]:
                    # Remove waste hold timer
                    del self.knowledge["hold_timer"][waste_type]
                if waste_type == self.target_waste_type:
                    # Add cooldown to drop location
                    # This is only for the target_waste_type
                    self.knowledge["recent_drop_pos"][self.pos] = self.drop_cooldown
            
            elif last_action == "combine_wastes":
                waste_type = last_action_desc[0]
                # Remove waste hold timer of previous wastes
                del self.knowledge["hold_timer"][waste_type]
        
    def deliberate(self)-> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # Update the collected waste's hold timer
        for waste_type in self.knowledge["hold_timer"]:
            self.knowledge["hold_timer"][waste_type] += 1
            
        # Decay the target waste_type drop cooldown:
        to_delete = []
        for pos, cooldown in self.knowledge["recent_drop_pos"].items():
            if cooldown <= 1:
                to_delete.append(pos)
            else:
                self.knowledge["recent_drop_pos"][pos] -= 1
        for pos in to_delete:
            del self.knowledge["recent_drop_pos"][pos]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]))
        
        # Combine if holding 2 yellow wastes
        if self.get_nb_target_waste_held() >= 2:
            return "combine_wastes", "yellow", "yellow"
        
        # Drop uncombined waste if held too long and at border or origin
        border_x = 2 * self.knowledge["grid_width"] // 3 - 1
        for waste_type in self.knowledge["collected_wastes"]:
            if waste_type == "yellow" and self.knowledge["hold_timer"][waste_type] > self.max_hold_steps:
                at_border = current_pos[0] == border_x
                at_origin = self.knowledge["held_waste_origin"]["yellow"] == current_pos
                if at_border or at_origin:
                    return "drop", "yellow"
       
        # Pick up yellow waste (not recently dropped)
        can_get_yellow_waste = any(waste_type == 'yellow' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_yellow_waste and (not current_pos in self.knowledge["recent_drop_pos"]) and (len(self.knowledge["collected_wastes"]) < 2):
            return "pick_up", "yellow"
        
        # Drop combined_waste (red) at zone border
        if any(waste_type == "red" for waste_type in self.knowledge["collected_wastes"]):
            if current_pos[0] == 2 * self.knowledge["grid_width"] // 3 - 1:
                return "drop", "red"
            # Move to the border
            else:
                return "move", "E"
            
        # Look for yellow wastes to pick up (ignoring recently dropped)
        target_wastes_pos = [pos for pos, content in perceptions.items() if any(waste_type == 'yellow' for waste_type in content['wastes'])
                             and (not pos in self.knowledge["recent_drop_pos"])]

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
        if any(waste_type == "red" for waste_type in self.knowledge["collected_wastes"]):
            if any(other_agent["agent_type"] == 'disposal_zone' for other_agent in perceptions[current_pos]['other_agents']):
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
        
        x_min = 2 * self.knowledge["grid_width"] // 3 - 1
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