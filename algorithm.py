class Map:

    def __init__(self):
        self.zones = {}
        self.n_zones = {}
        self.r_zones = {}
        self.connections = {}
        self.drones: int = 0
        self.path = []
        self.start = None
        self.end = None

    def add_zone(self, zone):
        self.zones[zone.coord] = zone
        self.n_zones[zone.name] = zone

    def show_map(self):
        for y in range(self.heigth):
            print()
            for x in range(self.width):
                if (x,y) in self.zones.keys():
                    if self.zones[(x, y)].zone_type == "priority":
                        c.print_green(f"({x}, {y})")
                    elif self.zones[(x, y)].zone_type == "restricted":
                        c.print_yellow(f"({x}, {y})")
                    elif self.zones[(x, y)].zone_type == "blocked":
                        c.print_red(f"({x}, {y})")
                    else:
                        print(f"({x}, {y})", end=' ')
                else:
                    print("      ", end=' ')
    def has_exit(self, zone):
        if "goal" in zone.name:
            return True
        elif zone.name not in self.connections.keys():
            return False
        for z in self.connections[zone.name]:
            result = self.has_exit(self.n_zones[z])
            if result == True:
                return True


    def shortest_path(self, start):
        parents = {}
        path = []
        queue = [(0, start)]
        best_cost = {start: 0}

        while queue:
            min_index = min(range(len(queue)), key=lambda index: queue[index][0])
            cost, zone = queue.pop(min_index)
            if zone == self.end:
                break
            for next_name in self.connections.get(zone.name, {}):
                next_zone = self.n_zones[next_name]
                pen = 1
                if zone.max_drones != self.drones:
                    pen = (self.drones - (next_zone.max_drones - len(next_zone.drones)))
                if next_zone.zone_type == 'restricted':
                    next_cost = 2 * pen
                else:
                    next_cost = 1 * pen
                new_cost = next_cost + cost
                if (next_name not in best_cost.keys() or new_cost < best_cost[next_name]):
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
            return
        path.append(start)

        return path[::-1]

    def move_drone(self, moves_from, moves_to, drone):
        if moves_from:
            moves_from.drones.pop(drone)
            if moves_to.zone_type == "restricted":
                self.r_zones[moves_to] = (drone, moves_from)
                moves_to.drones[drone] = False
                print(drone, f"{moves_from.name}-{moves_to.name}", sep='-', end=' ')
            else:
                moves_to.drones[drone] = True
                print(drone, moves_to.name, sep='-', end=' ')
        else:
            if moves_to.zone_type == "restricted":
                moves_to.drones[drone] = False
            else:
                moves_to.drones[drone] = False
            print(drone, moves_to.name, sep='-', end=' ')

    def empty_zone(self, zone):
        for drone in list(zone.drones.keys()):
            path = self.shortest_path(start=zone)
            if not path:
                continue
            prox = path[1]
            if zone.drones[drone] == False:
                zone.drones[drone] = True
                continue
            link = self.connections[zone.name][prox.name]
            if len(prox.drones) < prox.max_drones and link > 0:
                self.move_drone(zone, prox, drone)
                link -= 1
            self.connections[zone.name][prox.name] = link

    def turn(self):
        temp_connections = {
            zone: connections.copy()
            for zone, connections in self.connections.items()
        }
        for moves_to, (drone, moves_from) in self.r_zones.items():
            self.move_drone(moves_from= None, moves_to = moves_to, drone = drone)
            if self.connections[moves_from.name][moves_to.name] != -1:
                self.connections[moves_from.name][moves_to.name] -= 1
        self.r_zones = {}

        occ_zones = [z for z in self.zones.values() if len(z.drones) > 0 and z != self.end]
        for z in occ_zones[::-1]:
            if len(z.drones) > 0:
                self.empty_zone(z)
        self.connections = temp_connections
        print()
