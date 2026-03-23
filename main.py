#!/usr/bin/env python3

#import pprint
from parse import Map, parse_map
from show import Screen, TerminalOutput

def main():
    map = Map()
    parse_map(map, "challenger_map.txt")
    map.show_map()
    print('\n\n')
    turns = 0
    map.path = map.shortest_path()
    for p in map.path:
        print(p.name)
    print(map.path)
    while len(map.end.drones) < map.drones:
        map.turn()
        turns += 1
    print(f"Turns: {turns}")
    #pprint.pprint(map.connections)
    #return


if __name__ == "__main__":
    main()