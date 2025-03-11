# GROUP : 23
# DATE : 11.03.2025
# MEMBERS :
# - ZUO Yuxian
# - NADALIN	Marius
# - EL BARHICHI	Mohammed

import random
import mesa

class RadioactivityAgent(mesa.Agent):
    def __init__(self, model:mesa.Model, zone_type):
        super().__init__(model)
        
        self.zone_type = zone_type
        self.radioactivity_level = self._assign_radioactivity()

    def _assign_radioactivity(self):
        """Assigns a random radioactivity level based on the zone."""
        if self.zone_type == "green":
            return random.uniform(0, 0.33)
        elif self.zone_type == "yellow":
            return random.uniform(0.33, 0.66)
        elif self.zone_type == "red":
            return random.uniform(0.66, 1)
        else:
            raise ValueError("Invalid zone type. Must be 'green', 'yellow', or 'red'.")
        
    def __repr__(self):
        return f"RadioactivityAgent(zone={self.zone_type}, level={self.radioactivity_level:.2f})"

class WasteDisposalZone(mesa.Agent):
    def __init__(self, model:mesa.Model, grid_width):
        """
        Initializes the waste disposal zone at a random location in the easternmost column.
        """
        super().__init__(model)
        self.position = (grid_width - 1, random.randint(0, grid_width - 1))

    def __repr__(self):
        return f"WasteDisposalZone(position={self.position})"

class WasteAgent(mesa.Agent):
    def __init__(self, model:mesa.Model, waste_type):
        if waste_type not in {"green", "yellow", "red"}:
            raise ValueError("Invalid waste type. Must be 'green', 'yellow', or 'red'.")
        super().__init__(model)
        self.waste_type = waste_type
        model.add_waste(self)

    def __repr__(self):
        return f"WasteAgent(type={self.waste_type})"