# GROUP : 23
# DATE : 13.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import mesa.agent
import mesa.model
from objects import WasteAgent
import mesa

def is_pos_in_bounds(pos, x_min=None, x_max=None, y_min=None, y_max=None):
    """Check if a position is within the bounds."""
    x, y = pos
    return (x_min is None or x_min <= x) and (x_max is None or x <= x_max) and (y_min is None or y_min <= y) and (y_max is None or y <= y_max)

def dir_to_inbounds(pos, x_min=None, x_max=None, y_min=None, y_max=None):
    """Get the direction to the nearest inbounds position."""
    x, y = pos
    if x < x_min:
        return "E"
    if x > x_max:
        return "W"
    if y < y_min:
        return "N"
    if y > y_max:
        return "S"
    return None
    
# Action simulation
def sim_move(agent:mesa.agent, direction:str) -> tuple[int, int]:
    """Returns a new position based on the direction without modifying the agent."""
    x, y = agent.pos
    moves = {
        "N": (x, y + 1),
        "S": (x, y - 1),
        "E": (x + 1, y),
        "W": (x - 1, y),
    }
    return moves.get(direction, agent.pos)

# Define actions as pure functions
def move(model:mesa.model, agent:mesa.agent, direction:str) -> None:
    """Move the agent in the specified direction."""
    new_pos = sim_move(agent, direction)
    model.grid.move_agent(agent, new_pos)

def pick_up(model:mesa.model, agent:mesa.agent, waste:WasteAgent) -> None:
    """The agent picks up the waste."""
    agent.collected_wastes.append(waste)
    model.grid.remove_agent(waste)
            
def combine_wastes(model:mesa.model, agent:mesa.agent, waste_1:WasteAgent, waste_2:WasteAgent, combined_waste_type:str) -> None:
    """Transforms 2 wastes into a new form."""
    if (not waste_1 in agent.collected_wastes) or (not waste_2 in agent.collected_wastes):
        return
    combined_waste = WasteAgent(model, combined_waste_type)
    agent.collected_wastes.remove(waste_1)
    agent.collected_wastes.remove(waste_2)
    model.remove_waste(waste_1)
    model.remove_waste(waste_2)
    agent.collected_wastes.append(combined_waste)

def drop(model:mesa.model, agent:mesa.agent, waste:WasteAgent) -> None:
    """Drop down the waste."""
    if not waste in agent.collected_wastes:
        return
    agent.collected_wastes.remove(waste)
    model.grid.place_agent(waste, agent.pos)

# Store actions in a dictionary
ACTIONS = {
    "move": move,
    "pick_up": pick_up,
    "combine_wastes": combine_wastes,
    "drop": drop
}
