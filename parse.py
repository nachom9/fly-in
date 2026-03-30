from algorithm import Map

class MapParseError(Exception):
    pass


class InvalidConnectionError(MapParseError):
    pass


class ZoneNotFoundError(MapParseError):
    pass


class InvalidDroneNumberError(MapParseError):
    pass


class MetadataError(MapParseError):
    pass


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
    def process_metadata(cls, name, x, y, metadata, map, line_count):
        zone_type = 'normal'
        drones = {}
        max_drones = 1
        color = 'reset'
        if metadata:
            data = metadata.split()
            for item in data:
                key, value = item.strip('[]').split('=')
                if key == 'color' and value in map.colors:
                    color = value
                elif key == 'zone':
                    zone_type = value
                elif key == 'max_drones':
                    max_drones = int(value)

            if zone_type == 'blocked':
                max_drones = 0
        
        if zone_type not in ['normal', 'blocked', 'restricted', 'priority']:
            raise MetadataError(f"Line {line_count}. Unknown zone type: '{zone_type}'")
        if max_drones <= 0 and zone_type != 'blocked':
            raise InvalidDroneNumberError(f"Max drones must be at least 1")

        return cls(name, x, y, color, zone_type, max_drones, drones)


def parse_map(map, map_name):
    line_count = 1
    with open(map_name, 'r') as file:
        for line in file:
            line = line.strip()
            if ':' in line:
                key, value = [x.strip() for x in line.split(':', 1)]
                if key in ('hub', 'start_hub', 'end_hub'):
                    data = value.split()
                    if data[0] in map.n_zones:
                        raise MapParseError(f"Line {line_count}. Duplicate zone: {data[0]}")
                    if '[' in value and ']' in value:
                        if not value.endswith(']'):
                            raise MapParseError(f"Line {line_count}. Wrong format")
                        metadata = value.split('[')[1]
                        if len(data) != (3 + len(metadata.split())):
                            raise MapParseError(f"Line {line_count}. Wrong format")
                    else:
                        metadata = None
                        if len(data) != 3:
                            raise MapParseError(f"Line {line_count}. Wrong format")
                    try:
                        x = int(data[1])
                        y = int(data[2])
                    except Exception:
                        raise ValueError(f"Line {line_count}. Wrong format.")
                    if (x, y) in map.zones:
                        raise MapParseError(f"Line {line_count}. Duplicate coordinates: {data[0]}")
                    zone = Zone.process_metadata(data[0], x, y, metadata, map, line_count)
                    map.add_zone(zone)
                    if key == 'start_hub':
                        if map.start:
                            raise MapParseError(f"Line {line_count}. Map must have only 1 start_hub")
                        map.start = zone
                        i = 1
                        for drone in range(map.drones):
                            zone.drones[f'D{i}'] = True
                            i += 1
                    elif key == 'end_hub':
                        if map.end:
                            raise MapParseError(f"Line {line_count}. Map must have only 1 end_hub")
                        map.end = zone
                        zone.max_drones = map.drones
                elif key == 'connection':
                    if '[' in value:
                        zones, metadata = value.split('[', 1)
                        try:
                            max_link = int(metadata.strip('[]').split('=', 1)[1])
                        except Exception:
                            raise ValueError(f"Line {line_count}. Wrong format.")
                        zone_a, zone_b = zones.strip().split('-')
                    else:
                        zone_a, zone_b = value.strip().split('-')
                        max_link = 1
                    if zone_a in map.n_zones and zone_b in map.n_zones:
                        map.connections.setdefault(zone_a, {})[zone_b] = max_link
                    else:
                        if not map.start or not map.end:
                            raise ZoneNotFoundError("Map must have both start and end zones.")
                        raise InvalidConnectionError(f"Connection {zone_a}-{zone_b} not possible")
                    if max_link < 1:
                        raise InvalidConnectionError("Max link must be at least 1")
                elif key == 'nb_drones':
                    try:
                        map.drones = int(value)
                    except Exception:
                        raise ValueError(f"Line {line_count}. Wrong format.")
                elif line[0] != '#':
                    raise MapParseError(f"Line {line_count}. Wrong format")
            elif line and line[0] != '#':
                raise MapParseError(f"Line {line_count}. Wrong format")
            line_count += 1
    if not map.start or not map.end:
        raise ZoneNotFoundError("Map must have both start and end zones.")
    if not map.zones:
        raise MapParseError("Map has no zones")
    if not map.connections:
        raise MapParseError("Map has no connections")
    if not map.drones or map.drones <= 0:
        raise InvalidDroneNumberError(f"Map must have at least 1 drone")
