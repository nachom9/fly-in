#!/usr/bin/env python3

from parse import Map, parse_map, MapParseError

def main():
    map = Map()
    try:
        parse_map(map, "challenger_map.txt")
    except MapParseError as e:
        print(f"Error. {e}")
        exit(1)
    except ValueError as e:
        print(f"Error. {e}")
        exit(1)
    except FileNotFoundError as e:
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