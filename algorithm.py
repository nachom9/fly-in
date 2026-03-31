from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from parse import Zone


from typing import Dict, Optional, Tuple


class Map:

    def __init__(self) -> None:
        self.zones: Dict[Tuple[int, int], Zone] = {}
        self.n_zones: Dict[str, Zone] = {}
        self.r_zones: Dict[Zone, Tuple[str, Zone]] = {}
        self.connections: Dict[str, Dict[str, int]] = {}

        self.drones: int = 0
        self.path: list[Zone] = []

        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None

        self.colors: Dict[str, str] = {
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "purple": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "orange": "\033[38;5;208m",
            "brown": "\033[38;5;130m",
            "maroon": "\033[38;5;52m",
            "darkred": "\033[38;5;88m",
            "violet": "\033[38;5;177m",
            "crimson": "\033[38;5;160m",
            "reset": "\033[0m"
        }

    def add_zone(self, zone: "Zone") -> None:
        self.zones[zone.coord] = zone
        self.n_zones[zone.name] = zone

    def shortest_path(self, start: "Zone") -> Optional[list["Zone"]]:
        parents: Dict[str, Zone] = {}
        path: list[Zone] = []
        queue: list[Tuple[int, Zone]] = [(0, start)]
        best_cost: Dict[str, int] = {start.name: 0}
        while queue:
            min_index = min(range(len(queue)),
                            key=lambda index: queue[index][0])
            cost, zone = queue.pop(min_index)
            if zone == self.end:
                break
            for next_name in self.connections.get(zone.name, {}):
                next_zone = self.n_zones[next_name]
                pen = 1
                if zone.max_drones != self.drones:
                    pen = (self.drones -
                           (next_zone.max_drones - len(next_zone.drones)))
                if next_zone.zone_type == 'restricted':
                    next_cost = 2 * pen
                else:
                    next_cost = 1 * pen
                new_cost = next_cost + cost
                if (next_name not in best_cost.keys()
                   or new_cost < best_cost[next_name]):
                    queue.append((new_cost, next_zone))
                    parents[next_name] = zone
                    best_cost[next_name] = new_cost

        current = self.end
        try:
            while current != start:
                path.append(current)
                current = parents[current.name]
        except KeyError:
            if start == self.start:
                raise KeyError
        path.append(start)
        return path[::-1]

    def move_drone(self, moves_from: Optional["Zone"], moves_to: "Zone",
                   drone: str) -> None:

        if moves_from:
            moves_from.drones.pop(drone)
            if moves_to.zone_type == "restricted":
                self.r_zones[moves_to] = (drone, moves_from)
                moves_to.drones[drone] = False
                print(f"{self.colors[moves_to.color]}{drone}-{moves_from.name}"
                      f"-{moves_to.name}{self.colors['reset']}", end=' ')
            else:
                moves_to.drones[drone] = True
                print(f"{self.colors[moves_to.color]}{drone}-{moves_to.name}"
                      f"{self.colors['reset']}", end=' ')
        else:
            print(f"{self.colors[moves_to.color]}{drone}-{moves_to.name}"
                  f"{self.colors['reset']}", end=' ')

    def empty_zone(self, zone: "Zone") -> None:
        for drone in list(zone.drones.keys()):
            path = self.shortest_path(start=zone)
            if not path:
                continue
            prox = path[1]
            if zone.drones[drone] is False:
                zone.drones[drone] = True
                continue
            link = self.connections[zone.name][prox.name]
            if len(prox.drones) < prox.max_drones and link > 0:
                self.move_drone(zone, prox, drone)
                link -= 1
            self.connections[zone.name][prox.name] = link

    def turn(self) -> None:
        temp_connections = {
            zone: connections.copy()
            for zone, connections in self.connections.items()
        }
        for moves_to, (drone, moves_from) in self.r_zones.items():
            self.move_drone(moves_from=None, moves_to=moves_to, drone=drone)
            if self.connections[moves_from.name][moves_to.name] > 0:
                self.connections[moves_from.name][moves_to.name] -= 1
        self.r_zones = {}

        occ_zones = [z for z in self.zones.values()
                     if len(z.drones) > 0 and z != self.end]
        for z in occ_zones[::-1]:
            if len(z.drones) > 0:
                self.empty_zone(z)
        self.connections = temp_connections
        print()
