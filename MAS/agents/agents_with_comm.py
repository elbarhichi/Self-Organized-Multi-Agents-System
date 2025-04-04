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

# Import communication components
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative

class GreenRobotWithComm(CommunicatingAgent, GreenRobot):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model):
        GreenRobot.__init__(self, model)
        CommunicatingAgent.__init__(self, self.unique_id)

    @classmethod
    def create_agents(cls, model, n):
        return [cls(model) for _ in range(n)]
        
    def percepts(self):
        super().percepts()
        # TODO : Update agent knowledge regarding communication
        
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]))
        
        if self.knowledge["collected_wastes"].count("green") >= 2:
            return "combine_wastes", "green", "green"
        
        # Drop combined_waste (yellow) at zone border
        # if any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]):
        #     if current_pos[0] == self.knowledge["grid_width"] // 3 - 1:
        #         return "drop", "yellow"
        #     # Move to the border
        #     else:
        #         return "move", "E"

        can_get_green_waste = any(waste_type == 'green' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_green_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "green"
        
        if "yellow" in self.knowledge["collected_wastes"]:
            if current_pos[0] == self.knowledge["grid_width"] // 3 - 1:
                # 🔊 Send message to all yellow robots
                for agent in self.model.schedule.agents:
                    if isinstance(agent, YellowRobotWithComm):
                        msg = Message(
                            self.get_name(),
                            agent.get_name(),
                            MessagePerformative.INFORM_REF,
                            current_pos
                        )
                        self.send_message(msg)
                return "drop", "yellow"
            else:
                return "move", "E"
        
        # Look for wastes to pick up
        target_wastes_pos = [pos for pos, content in perceptions.items() if any(waste_type == 'green' for waste_type in content['wastes'])]
        
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

class YellowRobotWithComm(CommunicatingAgent, YellowRobot):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""
    
    def __init__(self, model: mesa.Model):
        YellowRobot.__init__(self, model)
        CommunicatingAgent.__init__(self, self.unique_id)
        self.knowledge["target_yellow_drop"] = None
    
    @classmethod
    def create_agents(cls, model, n):
        return [cls(model) for _ in range(n)]

    def percepts(self):
        super().percepts()
        
        # Handle incoming message
        messages = self.get_new_messages()
        for msg in messages:
            if msg.get_performative() == MessagePerformative.INFORM_REF:
                self.knowledge["target_yellow_drop"] = msg.get_content()
        
        
    def deliberate(self)-> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green or yellow zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]))
        
        if self.knowledge.get("target_yellow_drop") is not None:
            drop_pos = self.knowledge["target_yellow_drop"]
            if current_pos == drop_pos:
                return "pick_up", "yellow"
            else:
                return "move", self.dir_to_target(drop_pos)

        if self.knowledge["collected_wastes"].count("yellow") >= 2:
            return "combine_wastes", "yellow", "yellow"
       
        can_get_yellow_waste = any(waste_type == 'yellow' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_yellow_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "yellow"
        
        # Drop combined_waste (red) at zone border
        if "red" in self.knowledge["collected_wastes"]:
            if current_pos[0] == (self.knowledge["grid_width"] // 3) * 2 - 1:
                return "drop", "red"
            else:
                return "move", "E"
            
        # Look for wastes to pick up
        target_wastes_pos = [pos for pos, content in perceptions.items() if any(waste_type == 'yellow' for waste_type in content['wastes'])]
        
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

class RedRobotWithComm(CommunicatingAgent, RedRobot):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model: mesa.Model):
        RedRobot.__init__(self, model)
        CommunicatingAgent.__init__(self, self.unique_id)

    @classmethod
    def create_agents(cls, model, n):
        return [cls(model) for _ in range(n)]
        
    def percepts(self):
        super().percepts()
        # TODO : Update agent knowledge regarding communication
        
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green, yellow or red zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
       
        can_get_red_waste = any(waste_type == 'red' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_red_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "red"
        
        # Drop red waste at zone border
        if "red" in self.knowledge["collected_wastes"]:
            if any(isinstance(obj, WasteDisposalZone) for obj in perceptions[current_pos]["other_agents"]):
                return "drop", "red"
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