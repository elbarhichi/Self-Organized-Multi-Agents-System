# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import random
import mesa

class Radioactivity():
    """
    Class representing the radioactivity of a grid tile.
    """
    def __init__(self, model:mesa.Model, zone_type:str) -> None:
        self.model = model
        self.zone_type = zone_type
        self.radioactivity_level = self._assign_radioactivity()
        
    def get_radioactivity_level(self) -> float:
        return self.radioactivity_level

    def _assign_radioactivity(self) -> None:
        """Assigns a random radioactivity level based on the zone."""
        if self.zone_type == "green":
            return random.uniform(0, 0.33)
        elif self.zone_type == "yellow":
            return random.uniform(0.33, 0.66)
        elif self.zone_type == "red":
            return random.uniform(0.66, 1)
        else:
            raise ValueError("Invalid zone type. Must be 'green', 'yellow', or 'red'.")

    def __float__(self) -> float:
        """Allow implicit conversion of a Radioactivity object to a float."""
        return float(self.radioactivity_level)
        
    def __repr__(self) -> str:
        return f"Radioactivity(zone={self.zone_type}, level={self.radioactivity_level:.2f})"

class WasteDisposalZone(mesa.Agent):
    """
    WasteDisposalZone agent on a grid tile. Used to eliminate WasteAgent.
    """
    def __init__(self, model:mesa.Model) -> None:
        """
        Initializes the waste disposal zone.
        """
        super().__init__(model)
        self.pos = None
        model.add_disposal_zone(self)

    def __repr__(self) -> str:
        return f"WasteDisposalZone(position={self.pos})"

class WasteAgent(mesa.Agent):
    """
    WasteAgent to eliminate.
    """
    def __init__(self, model:mesa.Model, waste_type) -> None:
        if waste_type not in {"green", "yellow", "red"}:
            raise ValueError("Invalid waste type. Must be 'green', 'yellow', or 'red'.")
        super().__init__(model)
        self.waste_type = waste_type
        model.add_waste(self)

    def __repr__(self) -> str:
        return f"WasteAgent(type={self.waste_type})"