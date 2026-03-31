*This project has been created as part of the 42 curriculum by imelero-.*

# Fly-In Drones Simulator

## Description

Fly-In Drones is a pathfinding and simulation project where multiple drones must navigate through a network of interconnected zones to reach a final destination.

The goal is to simulate how drones move from a start hub to an end hub, respecting constraints such as:
- Zone capacity limits
- Connection capacity limits
- Special zone behaviors (restricted, priority, blocked)

The program parses a custom map file, computes optimal paths, and simulates drone movements turn by turn until all drones reach the goal.

## Instructions
### Installation

Clone the repository:

git clone https://github.com/nachom9/fly-in.git
cd fly-in

Create a virtual environment and install dependencies:

make install  


### Usage

Run the simulator:
```bash
make run  
```

By default, it uses:

map.txt  

Run with a custom map:
```bash
make run MAP=your_map.txt  
```

### Debug
```bash
make debug MAP=your_map.txt  
```

### Linting
```bash
make lint  
```
Strict mode:
```bash
make lint-strict  
```

### Clean
```bash
make clean  
```

## Algorithm & Implementation

### Pathfinding Strategy

The project uses a modified Dijkstra-like algorithm to compute paths dynamically.

Costs are adjusted based on:
- Zone occupancy
- Zone capacity
- Zone type (restricted zones increase cost)
- Priority zones slightly reduce cost

This allows drones to avoid congestion and distribute across multiple paths.


### Movement Simulation

The simulation runs in discrete turns:

1. Restricted zone movements are resolved first  
2. Zones are processed in reverse order  
3. Each drone computes a path and moves if possible  

Connection capacities are temporarily updated each turn.


### Constraints Handling

- Zone capacity (max_drones)  
- Connection capacity (max_link)  
- Blocked zones (cannot be entered)  
- Restricted zones (delayed movement behavior)  


## Visual Representation

The simulation outputs drone movements in the terminal.

Each turn prints movements like:

D1-A-B D2-C  

Colors are used via ANSI escape codes to improve readability.

This allows:
- Clear tracking of drone movements
- Easy identification of congestion
- Better understanding of simulation progress


## Features

- Custom map parser with validation  
- Dynamic pathfinding  
- Multiple drones support  
- Zone types: normal, restricted, priority, blocked  
- Capacity constraints for zones and connections  
- Turn-based simulation  
- Colored terminal output  
- Type hints with full mypy compliance  
- Makefile automation  


## File Format

The map file defines the simulation structure using a simple line-based format.

### Elements

- **Zones**
  - `hub`: a normal zone
  - `start_hub`: starting zone where drones are created
  - `end_hub`: destination zone where drones must arrive
- **Connections**
  - Define links between zones
- **Drones**
  - Total number of drones in the simulation
- **Metadata (optional)**
  - `[color=...]`
  - `[zone=...]` (normal, blocked, restricted, priority)
  - `[max_drones=...]`
  - `[max_link=...]` (for connections)


### Example Map
```bash
nb_drones: 3  

start_hub: A 0 0 [color=green]  
hub: B 1 0  
hub: C 2 0 [zone=priority color=blue]  
end_hub: D 3 0  

connection: A-B  
connection: B-C [max_link=2]  
connection: C-D  
```

### Explanation

- **nb_drones: 3**  
  Defines that 3 drones will be simulated.

- **Zones**
  - `A` is the start zone at coordinates (0, 0)
  - `D` is the end zone at coordinates (3, 0)
  - `B` and `C` are intermediate zones
  - Metadata can define:
    - color (for output visualization)
    - zone type (priority, restricted, blocked)
    - max_drones (capacity of the zone)

- **Connections**
  - `A-B`: simple connection with default capacity of 1
  - `B-C [max_link=2]`: connection with higher capacity
  - `C-D`: final connection to the end
## Resources

## References

- Python typing: https://docs.python.org/3/library/typing.html  
- PEP 257: https://peps.python.org/pep-0257/  
- Dijkstra Algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm  


## AI Usage

AI (ChatGPT) was used as a support tool for:

- Type hints and mypy compliance  
- Writing documentation (README and docstrings)  