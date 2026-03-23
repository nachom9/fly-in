from algorithm import Map

class Zone:

    def __init__(self, name, x, y, color, zone_type, max_drones, drones):
        self.name = name
        self.x = x
        self.y = y
        self.coord = (x, y)
        self.color = color
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.drones = drones


    @classmethod
    def process_metadata(cls, name, x, y, metadata, map):
        zone_type = 'normal'
        drones = {}
        i = 1
        max_drones = 1
        color = None
        data = metadata.split()
        for item in data:
            key, value = item.strip('[]').split('=')
            if key == 'color':
                color = value
            elif key == 'zone':
                zone_type = value
            elif key == 'max_drones':
                max_drones = int(value)
        if name == 'start':
            for drone in range(map.drones):
                drones[f'D{i}'] = True
                i += 1

        return cls(name, x, y, color, zone_type, max_drones, drones)


def parse_map(map, map_name):
    with open(map_name, 'r') as file:
        for line in file:
            line = line.strip()
            if ':' in line:
                key, value = [x.strip() for x in line.split(':', 1)]
                if key in ('hub', 'start_hub', 'end_hub'):
                    data = value.split()
                    metadata = value.split('[')[1]
                    zone = Zone.process_metadata(data[0], int(data[1]), int(data[2]), metadata, map)
                    map.add_zone(zone)
                    if key == 'start_hub':
                        map.start = zone
                    elif key == 'end_hub':
                        map.end = zone
                elif key == 'connection':
                    if '[' in value:
                        zones, metadata = value.split('[', 1)
                        max_link = int(metadata.strip('[]').split('=', 1)[1])
                        zone_a, zone_b = zones.strip().split('-')
                    else:
                        zone_a, zone_b = value.strip().split('-')
                        max_link = -1
                    map.connections.setdefault(zone_a, {})[zone_b] = max_link

                elif key == 'nb_drones':
                    map.drones = int(value)
    for zo, con in map.connections.items():
        for z in list(con.keys()):
            if z not in map.n_zones:
                map.connections[zo].pop(z)
    map.width = max(z.x for z in map.zones.values()) + 1
    map.heigth = max(z.y for z in map.zones.values()) + 1
