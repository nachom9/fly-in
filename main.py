#!/usr/bin/env python3

from parse import parse_map, MapParseError
from algorithm import Map


def main() -> None:
    map = Map()
    try:
        parse_map(map, "challenger_map.txt")
    except (MapParseError, ValueError, FileNotFoundError) as e:
        print(f"Error. {e}")
        exit(1)
    try:
        path = map.shortest_path(map.start)
        map.path = path
    except KeyError:
        print("Error. No solution")
        exit(1)
    while len(map.end.drones) < map.drones:
        map.turn()


if __name__ == "__main__":
    main()
