#!/usr/bin/env python3

from parse import parse_map, MapParseError
from algorithm import Map
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python fly-in.py <map_file>")
        sys.exit(1)

    map = Map()

    try:
        parse_map(map, sys.argv[1])
        if not map.start or not map.end:
            raise MapParseError("Map must have both start and end zones.")
    except (MapParseError, ValueError, FileNotFoundError) as e:
        print(f"Error. {e}")
        sys.exit(1)

    try:
        map.path = map.shortest_path(map.start)
    except KeyError:
        print("Error. No solution")
        sys.exit(1)

    while len(map.end.drones) < map.drones:
        map.turn()


if __name__ == "__main__":
    main()
