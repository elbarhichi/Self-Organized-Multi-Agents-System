# Self-Organization of Robots in a Hostile Environment

## Introduction

This project simulates the self-organization of heterogeneous robot agents tasked with handling hazardous waste in a radioactive environment. Each robot has specific capabilities and zone restrictions. Using agent-based modeling, robots perceive, reason, and act autonomously. The goal is to explore and evaluate different coordination strategies.

## Project Structure

- `agents/` - Contains different versions of agent implementations.
- `model.py` - Defines the simulation environment, agent interactions, and execution logic.
- `objects.py` - Implements static elements such as waste, radiation zones, and disposal sites.
- `actions.py` - Manages agent actions, including movement, waste collection, and transformations.
- `server.py` - Handles real-time visualization and simulation monitoring.

## Visualization

The simulation includes a real-time visualizer that displays agent movements, waste collection, and overall system dynamics. Key visual outputs include:

- Grid-based representation of the environment.
- Robot movement and interactions with waste.
- Graphs showing waste reduction over time.

## Agent Strategies

### Without Communication Capabilities

### With Communication Capabilities


### With Communication and Uncertainties

## Running the Simulation

1. Clone the repository.
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt

## Contact
