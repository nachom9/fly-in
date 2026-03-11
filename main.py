#!/usr/bin/env python3

from parse import Map, parse_map
from show import Screen, TerminalOutput

def main():
    map = Map()
    parse_map(map, "map_example.txt")
    map.show_map()
    


if __name__ == "__main__":
    main()