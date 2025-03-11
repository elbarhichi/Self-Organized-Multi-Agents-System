from MAS.objects import RadioactivityAgent, WasteDisposalZone, WasteAgent

# Create radioactivity agents for different zones
r1 = RadioactivityAgent("z1")
r2 = RadioactivityAgent("z2")
r3 = RadioactivityAgent("z3")

# Create a waste disposal zone in a grid of width 10
disposal_zone = WasteDisposalZone(grid_width=10)

# Create waste agents
w1 = WasteAgent("green")
w2 = WasteAgent("yellow")
w3 = WasteAgent("red")

print(r1)
print(r2)
print(r3)
print(disposal_zone)
print(w1)
print(w2)
print(w3)