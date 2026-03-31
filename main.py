#!/usr/bin/env python3

from parse import parse_map, MapParseError
from algorithm import Map


def main() -> None:
    map = Map()
    try:
        parse_map(map, "challenger_map.txt")
        if not map.start or not map.end:
            raise MapParseError("Map must have both start and end zones.")
    except (MapParseError, ValueError, FileNotFoundError) as e:
        print(f"Error. {e}")
        exit(1)

    try:
        map.path = map.shortest_path(map.start)
    except KeyError:
        print("Error. No solution")
        exit(1)

    while len(map.end.drones) < map.drones:
        map.turn()


if __name__ == "__main__":
    main()
