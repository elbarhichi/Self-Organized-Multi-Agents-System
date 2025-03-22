# Self-Organization of Robotic Agents in Hostile Environments

## Introduction

This project aims to simulate the self-organization of heterogeneous robot agents assigned to handle hazardous waste in a radioactive environment. Each robot has specific capabilities and zone restrictions, and operates autonomously using agent-based modeling to perceive, reason, and act. The objective is to explore and evaluate three strategies: one without communication between agents, one with inter-agent communication, and a third that incorporates both communication and uncertainty.

## Project Structure

- `agents/` - Contains different versions of robot agent implementations.
- `model.py` - Defines the RobotMission model, including environment setup, agent behavior, and waste management.
- `objects.py` - Defines static elements, including waste items, radioactive zones, and disposal sites.
- `actions.py` - Manages robot actions, including movement, waste pickup, combination, and disposal.
- `server.py` - Handles real-time visualization and simulation monitoring.

## Visualization

The simulation provides a real-time visual interface to observe the behavior of the agents. Key visual components include:

- A grid-based environment displaying robots, waste items, and disposal zones.
- Visualization of the radioactivity level in each grid cell using color gradients. 
- Real-time tracking of the number of different types of waste.  
- Adjustable parameters via sliders to explore various scenarios.

## Robot Behavior Strategies

### No-Communication Strategy

In this strategy, robots act independently based on their local perceptions and do not communicate with one another. 

At the beginning, each robot moves randomly within its designated zone. If a robot detects a waste item of its type in the current cell and has capacity, it will pick it up. Once it collects two wastes of the same type, it combines them into a higher-level waste. After combining, the robot resumes random movement. When it reaches the eastern boundary of its zone, it drops the combined waste, allowing the next-tier robot to pick it up and continue the process. Red robots, however, drop red waste directly into a disposal zone.

To slightly improve coordination, once a robot successfully combines two wastes, it immediately starts moving eastward toward the zone boundary rather than continuing to wander randomly. This behavior ensures that the combined waste is delivered efficiently to the correct boundary, improving the chances of successful collection and processing by the next robot type.

### Cooperative Strategy with Communication

### Cooperative Strategy with Communication and Uncertainty Handling

## Running the Simulation

1. Clone the repository.
2. Install dependencies:  
   ```powershell
   pip install -r requirements.txt

## Contact
