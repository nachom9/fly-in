from colors import PrintColors as c


class Map:

    def __init__(self):
        self.zones = {}
        self.n_zones = {}
        self.connections = {}
        self.drones: int = 0
        self.width: int = 0
        self.heigth: int = 0
        self.path = []

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

    def shortest_path(self):
        parents = {}
        path = []
        queue = [(0, self.start)]
        visited = set([self.start])

        while queue:
            min_index = min(range(len(queue)), key=lambda index: queue[index][0])
            cost, zone = queue.pop(min_index)
            cost += len(zone.drones)
            if zone == self.end:
                break
            for next_zone in self.connections.get(zone.name, {}):
                if next_zone not in visited:
                    if self.n_zones[next_zone].zone_type == 'restricted':
                        next_cost = 2
                    else:
                        next_cost = 1
                    queue.append((next_cost + cost, self.n_zones[next_zone]))
                    visited.add(next_zone)
                    parents[next_zone] = zone

        current = self.end
        try:
            while current != self.start:
                path.append(current)
                current = parents[current.name]
        except KeyError:
            print("No solution.")
            exit(1)
        path.append(self.start)

        return path[::-1]


    def can_move(self, zone):
        capacity = 0
        prox = [z for z in self.connections[zone.name].keys() if self.has_exit(self.n_zones[z])]
        for con in prox:
            capacity += self.n_zones[con].max_drones - len(self.n_zones[con].drones)
        return capacity > 0

    def move_drone(self, moves_from, moves_to, drone):
        moves_from.drones.pop(drone)
        if moves_to.zone_type == "restricted":
            moves_to.drones[drone] = False
        else:
            moves_to.drones[drone] = True
        print(drone, moves_to.name, sep='-', end=' ')


    def empty_zone(self, zone):
        prox = self.path[self.path.index(zone) + 1]
        for drone in zone.drones.keys():
            if zone.drones[drone] == False:
                zone.drones[drone] = True
                continue
            if len(prox.drones) < prox.max_drones:
                self.move_drone(zone, prox, drone)
                return

    def turn(self):
        occ_zones = [z for z in self.path if len(z.drones) > 0 and 'goal' not in z.name]
        for z in occ_zones:
            if self.can_move(z) and len(z.drones) > 0:
                self.empty_zone(z)
        print()
