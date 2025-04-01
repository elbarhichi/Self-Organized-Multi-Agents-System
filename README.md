# Self-Organization of Robotic Agents in Hostile Environments

## Introduction

This project aims to simulate the self-organization of heterogeneous robot agents assigned to handle hazardous waste in a radioactive environment. Each robot has specific capabilities and zone restrictions, and operates autonomously using agent-based modeling to perceive, reason, and act. The objective is to explore and evaluate three strategies: one without communication between agents, one with inter-agent communication, and a third that incorporates both communication and uncertainty.


## Project Structure

- `MAS/`
   - `agents/` - Contains different versions of robot agent implementations.
   - `model.py` - Defines the RobotMission model, including environment setup, agent behavior, and waste management.
   - `objects.py` - Defines static elements, including waste items, radioactive zones, and disposal sites.
   - `actions.py` - Manages robot actions, including movement, waste pickup, combination, and disposal.
   - `server.py` - Handles real-time visualization and simulation monitoring.
- `MAS_evaluation.ipynb` – Evaluates and compares the performance of different strategies.


## Visualization

The simulation provides a real-time visual interface to observe the behavior of the agents. Key visual components include:
- A grid-based environment displaying robots, waste items, and disposal zones.
- Visualization of the radioactivity level in each grid cell using color gradients. 
- Real-time tracking of the number of different types of waste.  
- Adjustable parameters via sliders to explore various scenarios.
- A Robot Type Selector dropdown, allowing to switch between different agent strategies.


## Robot Behavior Strategies

### No-Communication Strategy

In this strategy, robots act independently based on their local perceptions and do not communicate with one another. 

At the beginning, each robot moves randomly within its designated zone. If a robot detects a waste item of its type in the current cell and has capacity, it will pick it up. Once it collects two wastes of the same type, it combines them into a higher-level waste. After combining, the robot resumes random movement. When it reaches the eastern boundary of its zone, it drops the combined waste, allowing the next-tier robot to pick it up and continue the process. Red robots, however, drop red waste directly into a disposal zone.

Several improvements have been applied:
1. If a robot is holding one waste item and detects a second of the same type nearby, it will actively move toward it to attempt a combination.
2. Once a robot successfully combines two wastes, it immediately starts moving eastward toward the zone boundary.
3. If no useful waste is perceived, robots explore randomly, preferring directions that lead to less-visited cells by using their local visit memory.
4. To avoid situations where matching wastes are held indefinitely by different robots, robots now drop uncombined waste at the zone border or at the original pickup location after holding it for a certain number of steps.


### Cooperative Strategy with Communication

### Cooperative Strategy with Communication and Uncertainty Handling

## Running the Simulation

1. Clone the repository  
   ```sh
   git clone https://gitlab-student.centralesupelec.fr/marius.nadalin/mas_self_org_robots_in_host_env.git
   cd mas_self_org_robots_in_host_env

2. Install dependencies  
   ```sh
   pip install -r requirements.txt

3. Run the server
   ```sh
   solara run MAS/server.py

## Contact
- ZUO Yuxian – yuxian.zuo@student-cs.fr
- NADALIN Marius – marius.nadalin@student-cs.fr
- EL BARHICHI Mohammed – mohammed.elbarhichi@student-cs.fr