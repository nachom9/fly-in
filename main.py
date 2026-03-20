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
    #pprint.pprint(map.connections)
    #return

    print(map.shortest_path())

if __name__ == "__main__":
    main()