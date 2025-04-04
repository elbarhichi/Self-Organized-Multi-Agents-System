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

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative

class GreenRobotWithComm(GreenRobot, CommunicatingAgent):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model, "GreenRobot", is_prefix_name=True)
        
    def send_msg(self, msg_performative: MessagePerformative, msg_exp: str, msg_content: str | int) -> None:
        """Send a message to other agents.

        Args:
            msg_performative: The performative of the message.
            msg_exp: The expression of the message.
            msg_content: The content of the message.
        """
        self.send_message(Message(self.get_name(), msg_exp, msg_performative, msg_content))
        
    def broadcast_msg(self, msg_performative: MessagePerformative, msg_group_exp: str, msg_content: str | int) -> None:
        self.model.broadcast_message(self.get_name(), msg_group_exp, msg_performative, msg_content)
    
    def percepts(self):
        
        super().percepts()
        # TODO : Update agent knowledge regarding communication
        
        list_messages = self.get_new_messages()
        for message in list_messages:
            # print(message)
            msg_performative = message.get_performative()
            msg_exp = message.get_exp()
            msg_content = message.get_content()
            msg_content_type = type(msg_content)
            # self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.INFORM_REF, self.__v))
            
        # Update robot knowledge based of last action success feedback
        action_success = self.knowledge["action_success"]
        if self.knowledge["last_action"]:
            last_action, *last_action_desc = self.knowledge["last_action"]
        
        if action_success:
            if last_action == "drop":
                waste_type = last_action_desc[0]
                if waste_type == "yellow":
                    #Communicate yellow waste pos to all YellowRobot agents
                    self.broadcast_msg(MessagePerformative.INFORM_REF, "yellow", self.pos)
        
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "yellow" for waste in self.knowledge["collected_wastes"]))
        
        if sum(waste_type == "green" for waste_type in self.knowledge["collected_wastes"]) >= 2:
            return "combine_wastes", "green", "green"
       
        can_get_green_waste = any(waste_type == 'green' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_green_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "green"
        
        # Drop combined_waste (yellow) at zone border
        if any(waste_type == "yellow" for waste_type in self.knowledge["collected_wastes"]):
            if current_pos[0] == self.knowledge["grid_width"] // 3 - 1:
                return "drop", "yellow"
            # Move to the border
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

class YellowRobotWithComm(YellowRobot, CommunicatingAgent):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a YellowRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model, "YellowRobot", is_prefix_name=True)
        # YellowRobot.__init__(self, model)
        # CommunicatingAgent.__init__(self, model, "YellowRobot" + str(self.unique_id))
        # TODO : Add communication attributes
        
    def percepts(self):
        super().percepts()
        # TODO : Update agent knowledge regarding communication
        
        list_messages = self.get_new_messages()
        for message in list_messages:
            # print(message)
            msg_performative = message.get_performative()
            msg_exp = message.get_exp()
            msg_content = message.get_content()
            msg_content_type = type(msg_content)
            # self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.INFORM_REF, self.__v))
        
    def deliberate(self)-> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green or yellow zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        # DEBUG
        # print(self, self.collected_wastes, self.knowledge["collected_wastes"], any(waste.waste_type == "red" for waste in self.knowledge["collected_wastes"]))
        
        if sum(waste_type == "yellow" for waste_type in self.knowledge["collected_wastes"]) >= 2:
            return "combine_wastes", "yellow", "yellow"
       
        can_get_yellow_waste = any(waste_type == 'yellow' for waste_type in perceptions[current_pos]['wastes'])
        if can_get_yellow_waste and len(self.knowledge["collected_wastes"]) < 2:
            return "pick_up", "yellow"
        
        # Drop combined_waste (red) at zone border
        if any(waste_type == "red" for waste_type in self.knowledge["collected_wastes"]):
            if current_pos[0] == (self.knowledge["grid_width"] // 3) * 2 - 1:
                return "drop", "red"
            # Move to the border
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

class RedRobotWithComm(RedRobot, CommunicatingAgent):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a RedRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model, "RedRobot", is_prefix_name=True)
        # TODO : Add communication attributes
        
    def percepts(self):
        super().percepts()
        # TODO : Update agent knowledge regarding communication
        
        list_messages = self.get_new_messages()
        for message in list_messages:
            # print(message)
            msg_performative = message.get_performative()
            msg_exp = message.get_exp()
            msg_content = message.get_content()
            msg_content_type = type(msg_content)
            # self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.INFORM_REF, self.__v))
        
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