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

from collections import deque

MAX_RESPONSE_DELAY = 6      # Maximum delay to wait for a response from the other robot
INFORM_PICK_UP_PERIOD = 8   # Period between 2 pick up messages (repetition of the same message)

class CommunicatingRobot(CommunicatingAgent):
    """A robot that is able to send and receive Messages"""
    
    def __init__(self, model:mesa.Model, name:str, *args, **kwargs):
        super().__init__(model, name, is_prefix_name=True, *args, **kwargs)

    def send_msg(self, msg_performative: MessagePerformative, msg_exp: str, msg_content: str | int) -> None:
        """Send a message to another agent.

        Args:
            msg_performative: The performative of the message.
            msg_exp: The name of the receiver.
            msg_content: The content of the message.
        """
        self.send_message(Message(self.get_name(), msg_exp, msg_performative, msg_content))
        
    def broadcast_msg(self, msg_performative: MessagePerformative, msg_group_exp: str, msg_content: str | int) -> None:
        """Send a message to a group of agents.

        Args:
            msg_performative: The performative of the message.
            msg_group_exp: The name of the receiver group ("green", "yellow", "red").
            msg_content: The content of the message.
        """
        self.model.broadcast_message(self.get_name(), msg_group_exp, msg_performative, msg_content)
        
    def get_id_from_name(self, name: str) -> int:
        """
        Get the ID of an agent from its name.
        """
        id = name.split("_")[1]
        return int(id)
        
    def has_priority(self, msg_exp: str) -> bool:
        """Check if the agent has priority over the message sender.

        Args:
            msg_exp: The name of the sender.

        Returns:
            True if the agent has priority, False otherwise.
        """
        return self.get_id_from_name(msg_exp) < self.get_id_from_name(self.get_name())
        
    def extract_sender_type(self, msg_exp) -> str:
        if "Green" in msg_exp:
            return "green"
        elif "Yellow" in msg_exp:
            return "yellow"
        elif "Red" in msg_exp:
            return "red"

class GreenRobotWithComm(GreenRobot, CommunicatingRobot):
    """A robot that lives in the green zone (low radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a GreenRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model, "GreenRobot")
        self.knowledge['msgs_to_process'] = deque()
        self.knowledge['msgs_to_send'] = deque()
        self.knowledge['msgs_to_broadcast'] = deque()
        self.knowledge['new_pick_up_msg_cooldown'] = 0
        self.knowledge['collaboration_in_progress'] = False
        self.knowledge['negociation_timer'] = 0
        self.knowledge['partner_name'] = None
        self.knowledge['should_drop'] = False
        self.knowledge['target_drop_pos'] = None
        self.knowledge['pos_given_waste'] = set()
        
        self._step = 0
    
    def percepts(self):
        super().percepts()
        
        # Receive messages from other agents
        list_messages = self.get_new_messages()
        self.knowledge["msgs_to_process"].extend(list_messages)
            
        # Update robot knowledge based of last action success feedback
        action_success = self.knowledge["action_success"]
        last_action, *last_action_desc = self.knowledge["last_action"]
        
        if action_success:
            if last_action == "drop":
                waste_type = last_action_desc[0]
                if waste_type == "yellow":
                    # Communicate yellow waste pos to all YellowRobot agents
                    self.knowledge['msgs_to_broadcast'].append((MessagePerformative.INFORM_REF, "yellow", self.pos))
                    
            elif last_action == "pick_up":
                waste_type = last_action_desc[0]
                if waste_type == self.target_waste_type and self.get_nb_target_waste_held() == 1:
                    # Inform GreenRobot agents that a green waste is picked up
                    self.knowledge['msgs_to_broadcast'].append((MessagePerformative.INFORM_REF, "green", "picked_green"))
                    self.knowledge['new_pick_up_msg_cooldown'] = INFORM_PICK_UP_PERIOD + 1 # Start cooldown

    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        self._step += 1
        
        if self.knowledge['negociation_timer'] > 0:
            self.knowledge['negociation_timer'] -= 1
            if self.knowledge['negociation_timer'] == 0:
                # Timeout, cancel collaboration
                # print(f'[GREEN] [step {self._step}] {self.get_name()} collaboration TIMEOUT') # DEBUG
                self.knowledge['collaboration_in_progress'] = False
                self.knowledge['partner_name'] = None
                self.knowledge['should_drop'] = False
                
        if self.knowledge['new_pick_up_msg_cooldown'] > 0 and (not self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0):
            if self.get_nb_target_waste_held() != 1:
                # Stop cooldown
                self.knowledge['new_pick_up_msg_cooldown'] = 0
            else:
                self.knowledge['new_pick_up_msg_cooldown'] -= 1
                if self.knowledge['new_pick_up_msg_cooldown'] == 0:
                    # Resend a collaboration search
                    self.knowledge['msgs_to_broadcast'].append((MessagePerformative.INFORM_REF, "green", "picked_green"))
                    self.knowledge['new_pick_up_msg_cooldown'] = INFORM_PICK_UP_PERIOD # Start cooldown
                
        # Process messages
        while self.knowledge["msgs_to_process"]:
            message = self.knowledge["msgs_to_process"].popleft()
            msg_performative = message.get_performative()
            msg_exp = message.get_exp()
            msg_content = message.get_content()
            sender_type = self.extract_sender_type(msg_exp)
            
            # print(f'[GREEN] [step {self._step}] {self.get_name()} {msg_performative} {msg_exp} {msg_content}') # DEBUG
            
            if sender_type == "green":                
                if msg_performative == MessagePerformative.INFORM_REF and msg_content == "picked_green":
                    if self.get_nb_target_waste_held() == 1 and (not self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0):
                        # Propose collaboration
                        self.knowledge['msgs_to_send'].append((MessagePerformative.PROPOSE, msg_exp, "combine?"))
                        self.knowledge['negociation_timer'] = MAX_RESPONSE_DELAY # Start timer
                        self.knowledge['partner_name'] = msg_exp
                        
                elif msg_performative == MessagePerformative.PROPOSE:
                    if self.get_nb_target_waste_held() == 1:
                        if not self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0:
                            self.knowledge['collaboration_in_progress'] = True
                            # Accept
                            self.knowledge['msgs_to_send'].append((MessagePerformative.ACCEPT, msg_exp, current_pos))
                            self.knowledge['partner_name'] = msg_exp
                            self.knowledge['should_drop'] = True
                            self.knowledge['target_drop_pos'] = current_pos
                            
                        elif msg_exp == self.knowledge["partner_name"]:
                            # Rare case when 2 robots send PROPOSE to each other at the same step
                            self.knowledge['collaboration_in_progress'] = True
                            if self.has_priority(msg_exp):
                                # Priority based on name (tie-breack), accept the proposal and send position to drop
                                self.knowledge['msgs_to_send'].append((MessagePerformative.ACCEPT, msg_exp, current_pos))
                                self.knowledge['should_drop'] = True
                                self.knowledge['target_drop_pos'] = current_pos
                                self.knowledge['negociation_timer'] = 0 # Don't wait for response anymore
                            else:
                                # Wait for the other robot to accept the proposal
                                self.knowledge['negociation_timer'] = MAX_RESPONSE_DELAY # Reset timer
                        else:
                            pass # TODO : REFUSE message

                elif msg_performative == MessagePerformative.ACCEPT:
                    shared_waste_pos = msg_content
                    # Partner accepted; go pick up the piece
                    self.knowledge['negociation_timer'] = 0 # Don't wait for response anymore
                    self.knowledge['collaboration_in_progress'] = True
                    self.knowledge['partner_name'] = msg_exp
                    self.knowledge['target_pick_up_pos'] = shared_waste_pos
                
        # Send messages
        while self.knowledge["msgs_to_broadcast"]:
            msg_performative, msg_group_exp, msg_content = self.knowledge["msgs_to_broadcast"].popleft()
            self.broadcast_msg(msg_performative, msg_group_exp, msg_content)
            
        while self.knowledge["msgs_to_send"]:
            msg_performative, msg_exp, msg_content = self.knowledge["msgs_to_send"].popleft()
            self.send_msg(msg_performative, msg_exp, msg_content)
        
        if self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0:
            # Drop green waste at target drop position
            if self.knowledge['should_drop']:
                if current_pos == self.knowledge['target_drop_pos']:
                    self.knowledge['should_drop'] = False
                    self.knowledge['collaboration_in_progress'] = False
                    self.knowledge['target_drop_pos'] = None
                    self.knowledge['pos_given_waste'].add(current_pos)
                    return "drop", "green"
                else:
                    # Move to the drop position
                    move_direction = self.dir_to_target(self.knowledge['target_drop_pos'])
                    return "move", move_direction
            else:
                # Move to the pick up position
                if current_pos == self.knowledge['target_pick_up_pos']:
                    self.knowledge['collaboration_in_progress'] = False
                    self.knowledge['target_pick_up_pos'] = None
                    return "pick_up", "green"
                else:
                    # Move to the pick up position
                    move_direction = self.dir_to_target(self.knowledge['target_pick_up_pos'])
                    return "move", move_direction
        
        if self.get_nb_target_waste_held() >= 2:
            return "combine_wastes", "green", "green"

        if not current_pos in self.knowledge['pos_given_waste']: # Avoid picking up waste shared with other robots
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
        target_wastes_pos = [pos for pos, content in perceptions.items() 
                             if any(waste_type == 'green' for waste_type in content['wastes']) and pos not in self.knowledge['pos_given_waste']]
        
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

class YellowRobotWithComm(YellowRobot, CommunicatingRobot):
    """A robot that lives in the green & yellow zone (low to medium radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a YellowRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model, "YellowRobot")
        self.knowledge['msgs_to_process'] = deque()
        self.knowledge['msgs_to_send'] = deque()
        self.knowledge['msgs_to_broadcast'] = deque()
        self.knowledge['new_pick_up_msg_cooldown'] = 0
        self.knowledge['collaboration_in_progress'] = False
        self.knowledge['negociation_timer'] = 0
        self.knowledge['partner_name'] = None
        self.knowledge['should_drop'] = False
        self.knowledge['target_drop_pos'] = None
        self.knowledge['pos_given_waste'] = set()
        
        self._step = 0
    
    def percepts(self):
        super().percepts()
        
        # Receive messages from other agents
        list_messages = self.get_new_messages()
        self.knowledge["msgs_to_process"].extend(list_messages)
            
        # Update robot knowledge based of last action success feedback
        action_success = self.knowledge["action_success"]
        last_action, *last_action_desc = self.knowledge["last_action"]
        
        if action_success:
            if last_action == "drop":
                waste_type = last_action_desc[0]
                if waste_type == "red":
                    # Communicate red waste pos to all YellowRobot agents
                    self.knowledge['msgs_to_broadcast'].append((MessagePerformative.INFORM_REF, "red", self.pos))
                    
            elif last_action == "pick_up":
                waste_type = last_action_desc[0]
                if waste_type == self.target_waste_type and self.get_nb_target_waste_held() == 1:
                    # Inform YellowRobot agents that a green waste is picked up
                    self.knowledge['msgs_to_broadcast'].append((MessagePerformative.INFORM_REF, "yellow", "picked_yellow"))
                    self.knowledge['new_pick_up_msg_cooldown'] = INFORM_PICK_UP_PERIOD + 1 # Start cooldown
        
    def deliberate(self)-> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green or yellow zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        self._step += 1
        
        if self.knowledge['negociation_timer'] > 0:
            self.knowledge['negociation_timer'] -= 1
            if self.knowledge['negociation_timer'] == 0:
                # Timeout, cancel collaboration
                # print(f'[YELLOW] [step {self._step}] {self.get_name()} collaboration TIMEOUT') # DEBUG
                self.knowledge['collaboration_in_progress'] = False
                self.knowledge['partner_name'] = None
                self.knowledge['should_drop'] = False    
                
        if self.knowledge['new_pick_up_msg_cooldown'] > 0 and (not self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0):
            if self.get_nb_target_waste_held() != 1:
                # Stop cooldown
                self.knowledge['new_pick_up_msg_cooldown'] = 0
            else:
                self.knowledge['new_pick_up_msg_cooldown'] -= 1
                if self.knowledge['new_pick_up_msg_cooldown'] == 0:
                    # Resend a collaboration search
                    self.knowledge['msgs_to_broadcast'].append((MessagePerformative.INFORM_REF, "yellow", "picked_yellow"))
                    self.knowledge['new_pick_up_msg_cooldown'] = INFORM_PICK_UP_PERIOD # Start cooldown
                
        # Process messages
        while self.knowledge["msgs_to_process"]:
            message = self.knowledge["msgs_to_process"].popleft()
            msg_performative = message.get_performative()
            msg_exp = message.get_exp()
            msg_content = message.get_content()
            sender_type = self.extract_sender_type(msg_exp)
            
            # print(f'[YELLOW] [step {self._step}] {self.get_name()} {msg_performative} {msg_exp} {msg_content}') # DEBUG
            
            if sender_type == "green":
                if msg_performative == MessagePerformative.INFORM_REF and isinstance(msg_content, tuple):
                    # Update knowledge with the new yellow waste position
                    waste_pos = msg_content
                    if not waste_pos in self.knowledge["perceptions"]:
                        self.knowledge["perceptions"][msg_content] = {
                            'rad_level' : None,
                            'wastes' : [],
                            'other_agents' : [],
                            'nb_times_visited' : 0
                            }
                    self.knowledge["perceptions"][msg_content]["wastes"].append("yellow")
            
            elif sender_type == "yellow":
                if msg_performative == MessagePerformative.INFORM_REF and msg_content == "picked_yellow":
                    if self.get_nb_target_waste_held() == 1 and (not self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0):
                        # Propose collaboration
                        self.knowledge['msgs_to_send'].append((MessagePerformative.PROPOSE, msg_exp, "combine?"))
                        self.knowledge['negociation_timer'] = MAX_RESPONSE_DELAY # Start timer
                        self.knowledge['partner_name'] = msg_exp
                        
                elif msg_performative == MessagePerformative.PROPOSE:
                    if self.get_nb_target_waste_held() == 1:
                        if not self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0:
                            self.knowledge['collaboration_in_progress'] = True
                            # Accept
                            self.knowledge['msgs_to_send'].append((MessagePerformative.ACCEPT, msg_exp, current_pos))
                            self.knowledge['partner_name'] = msg_exp
                            self.knowledge['should_drop'] = True
                            self.knowledge['target_drop_pos'] = current_pos
                            
                        elif msg_exp == self.knowledge["partner_name"]:
                            # Rare case when 2 robots send PROPOSE to each other at the same step
                            self.knowledge['collaboration_in_progress'] = True
                            if self.has_priority(msg_exp):
                                # Priority based on name (tie-breack), accept the proposal and send position to drop
                                self.knowledge['msgs_to_send'].append((MessagePerformative.ACCEPT, msg_exp, current_pos))
                                self.knowledge['should_drop'] = True
                                self.knowledge['target_drop_pos'] = current_pos
                                self.knowledge['negociation_timer'] = 0 # Don't wait for response anymore
                            else:
                                # Wait for the other robot to accept the proposal
                                self.knowledge['negociation_timer'] = MAX_RESPONSE_DELAY # Reset timer
                        else:
                            pass # TODO : REFUSE message

                elif msg_performative == MessagePerformative.ACCEPT:
                    shared_waste_pos = msg_content
                    # Partner accepted; go pick up the piece
                    self.knowledge['negociation_timer'] = 0 # Don't wait for response anymore
                    self.knowledge['collaboration_in_progress'] = True
                    self.knowledge['partner_name'] = msg_exp
                    self.knowledge['target_pick_up_pos'] = shared_waste_pos
                
        # Send messages
        while self.knowledge["msgs_to_broadcast"]:
            msg_performative, msg_group_exp, msg_content = self.knowledge["msgs_to_broadcast"].popleft()
            self.broadcast_msg(msg_performative, msg_group_exp, msg_content)
            
        while self.knowledge["msgs_to_send"]:
            msg_performative, msg_exp, msg_content = self.knowledge["msgs_to_send"].popleft()
            self.send_msg(msg_performative, msg_exp, msg_content)
            
        if self.knowledge['collaboration_in_progress'] and self.knowledge['negociation_timer'] == 0:
            # Drop yellow waste at target drop position
            if self.knowledge['should_drop']:
                if current_pos == self.knowledge['target_drop_pos']:
                    self.knowledge['should_drop'] = False
                    self.knowledge['collaboration_in_progress'] = False
                    self.knowledge['target_drop_pos'] = None
                    self.knowledge['pos_given_waste'].add(current_pos)
                    return "drop", "yellow"
                else:
                    # Move to the drop position
                    move_direction = self.dir_to_target(self.knowledge['target_drop_pos'])
                    return "move", move_direction
            else:
                # Move to the pick up position
                if current_pos == self.knowledge['target_pick_up_pos']:
                    self.knowledge['collaboration_in_progress'] = False
                    self.knowledge['target_pick_up_pos'] = None
                    return "pick_up", "yellow"
                else:
                    # Move to the pick up position
                    move_direction = self.dir_to_target(self.knowledge['target_pick_up_pos'])
                    return "move", move_direction
        
        if self.get_nb_target_waste_held() >= 2:
            return "combine_wastes", "yellow", "yellow"
       
        if not current_pos in self.knowledge['pos_given_waste']: # Avoid picking up waste shared with other robots
            can_get_yellow_waste = any(waste_type == 'yellow' for waste_type in perceptions[current_pos]['wastes'])
            if can_get_yellow_waste and len(self.knowledge["collected_wastes"]) < 2:
                return "pick_up", "yellow"
        
        # Drop combined_waste (red) at zone border
        if any(waste_type == "red" for waste_type in self.knowledge["collected_wastes"]):
            if current_pos[0] == 2 * self.knowledge["grid_width"] // 3 - 1:
                return "drop", "red"
            # Move to the border
            else:
                return "move", "E"
                   
        # Look for wastes to pick up
        target_wastes_pos = [pos for pos, content in perceptions.items()
                             if any(waste_type == 'yellow' for waste_type in content['wastes']) and pos not in self.knowledge['pos_given_waste']]
        
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

class RedRobotWithComm(RedRobot, CommunicatingRobot):
    """A robot that lives in the green, yellow & red zone (low to high radioactivity zone)"""

    def __init__(self, model:mesa.Model) -> None:
        """initialize a RedRobot instance.

        Args:
            model: A RobotMission instance
        """
        super().__init__(model, "RedRobot")
        
        self.knowledge['msgs_to_process'] = deque()
        self.knowledge['msgs_to_send'] = deque()
        self.knowledge['msgs_to_broadcast'] = deque()
        
        self._step = 0
        
    def percepts(self):
        super().percepts()
        
        # Receive messages from other agents
        list_messages = self.get_new_messages()
        self.knowledge["msgs_to_process"].extend(list_messages)
            
        # Update robot knowledge based of last action success feedback
        action_success = self.knowledge["action_success"]
        last_action, *last_action_desc = self.knowledge["last_action"]
        
        if action_success:
            if last_action == "pick_up":
                waste_type = last_action_desc[0]
                if waste_type == self.target_waste_type and self.get_nb_target_waste_held() == 1:
                    # Inform RedRobot agents that a green waste is picked up
                    self.knowledge['msgs_to_broadcast'].append((MessagePerformative.INFORM_REF, "red", "picked_red"))
        
    def deliberate(self) -> tuple[str, str | int | None]:
        # Based on the current knowledge, choose an action to perform
        # Random move in green, yellow or red zone
        perceptions = self.knowledge["perceptions"]
        current_pos = self.knowledge["current_pos"]
        
        self._step += 1
                
        # Process messages
        while self.knowledge["msgs_to_process"]:
            message = self.knowledge["msgs_to_process"].popleft()
            msg_performative = message.get_performative()
            msg_exp = message.get_exp()
            msg_content = message.get_content()
            sender_type = self.extract_sender_type(msg_exp)
            
            # print(f'[RED] [step {self._step}] {self.get_name()} {msg_performative} {msg_exp} {msg_content}') # DEBUG
            
            if sender_type == "yellow":
                if msg_performative == MessagePerformative.INFORM_REF and isinstance(msg_content, tuple):
                    # Update knowledge with the new red waste position
                    waste_pos = msg_content
                    if not waste_pos in self.knowledge["perceptions"]:
                        self.knowledge["perceptions"][msg_content] = {
                            'rad_level' : None,
                            'wastes' : [],
                            'other_agents' : [],
                            'nb_times_visited' : 0
                            }
                    self.knowledge["perceptions"][msg_content]["wastes"].append("red")
            
            elif sender_type == "red":
                pass
                
        # Send messages
        while self.knowledge["msgs_to_broadcast"]:
            msg_performative, msg_group_exp, msg_content = self.knowledge["msgs_to_broadcast"].popleft()
            self.broadcast_msg(msg_performative, msg_group_exp, msg_content)
            
        while self.knowledge["msgs_to_send"]:
            msg_performative, msg_exp, msg_content = self.knowledge["msgs_to_send"].popleft()
            self.send_msg(msg_performative, msg_exp, msg_content)
       
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