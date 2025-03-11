import random

class RadioactivityAgent:
    def __init__(self, zone_type):
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

class WasteDisposalZone:
    def __init__(self, grid_width):
        """
        Initializes the waste disposal zone at a random location in the easternmost column.
        """
        self.position = (grid_width - 1, random.randint(0, grid_width - 1))

    def __repr__(self):
        return f"WasteDisposalZone(position={self.position})"

class WasteAgent:
    def __init__(self, waste_type):
        if waste_type not in {"green", "yellow", "red"}:
            raise ValueError("Invalid waste type. Must be 'green', 'yellow', or 'red'.")
        self.waste_type = waste_type

    def __repr__(self):
        return f"WasteAgent(type={self.waste_type})"
