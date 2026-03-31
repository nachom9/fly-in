#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class Zone:
    name: str
    zone_type: str
    max_drones: int


@dataclass(frozen=True)
class TransitState:
    target: str


class MapData:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start: str | None = None
        self.goal: str | None = None
        self.zones: dict[str, Zone] = {}
        self.adj: dict[str, set[str]] = defaultdict(set)
        self.conn_capacity: dict[frozenset[str], int] = {}


ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def strip_comment(line: str) -> str:
    pos = line.find("#")
    if pos != -1:
        line = line[:pos]
    return line.strip()


def parse_metadata(text: str) -> dict[str, str]:
    text = text.strip()
    if not text:
        return {}
    if not (text.startswith("[") and text.endswith("]")):
        raise ValidationError(f"Invalid metadata block: {text}")
    inner = text[1:-1].strip()
    if not inner:
        return {}
    result: dict[str, str] = {}
    for item in inner.split():
        if "=" not in item:
            raise ValidationError(f"Invalid metadata item: {item}")
        key, value = item.split("=", 1)
        result[key] = value
    return result


def parse_zone_line(kind: str, rest: str, data: MapData, lineno: int) -> None:
    parts = rest.split(None, 3)
    if len(parts) < 3:
        raise ValidationError(f"Line {lineno}: invalid zone definition")

    name = parts[0]
    if "-" in name or " " in name:
        raise ValidationError(f"Line {lineno}: invalid zone name '{name}'")
    if name in data.zones:
        raise ValidationError(f"Line {lineno}: duplicate zone '{name}'")

    try:
        int(parts[1])
        int(parts[2])
    except ValueError as exc:
        raise ValidationError(f"Line {lineno}: invalid coordinates") from exc

    meta_text = parts[3].strip() if len(parts) >= 4 else ""
    meta = parse_metadata(meta_text) if meta_text else {}

    zone_type = meta.get("zone", "normal")
    if zone_type not in ZONE_TYPES:
        raise ValidationError(f"Line {lineno}: invalid zone type '{zone_type}'")

    max_drones_raw = meta.get("max_drones", "1")
    if not max_drones_raw.isdigit() or int(max_drones_raw) <= 0:
        raise ValidationError(f"Line {lineno}: invalid max_drones")
    max_drones = int(max_drones_raw)

    data.zones[name] = Zone(name=name, zone_type=zone_type, max_drones=max_drones)

    if kind == "start_hub":
        if data.start is not None:
            raise ValidationError(f"Line {lineno}: duplicate start_hub")
        data.start = name
    elif kind == "end_hub":
        if data.goal is not None:
            raise ValidationError(f"Line {lineno}: duplicate end_hub")
        data.goal = name


def parse_connection_line(rest: str, data: MapData, lineno: int) -> None:
    m = re.fullmatch(r"([^\s\[]+)(?:\s+(\[.*\]))?", rest)
    if not m:
        raise ValidationError(f"Line {lineno}: invalid connection definition")

    conn_name = m.group(1).strip()
    meta_text = m.group(2) or ""
    meta = parse_metadata(meta_text) if meta_text else {}

    if conn_name.count("-") != 1:
        raise ValidationError(f"Line {lineno}: invalid connection '{conn_name}'")

    a, b = conn_name.split("-", 1)
    a = a.strip()
    b = b.strip()

    if a not in data.zones or b not in data.zones:
        raise ValidationError(
            f"Line {lineno}: connection references undefined zone '{conn_name}'"
        )

    key = frozenset((a, b))
    if key in data.conn_capacity:
        raise ValidationError(f"Line {lineno}: duplicate connection '{conn_name}'")

    cap_raw = meta.get("max_link_capacity", "1")
    if not cap_raw.isdigit() or int(cap_raw) <= 0:
        raise ValidationError(f"Line {lineno}: invalid max_link_capacity")

    data.conn_capacity[key] = int(cap_raw)
    data.adj[a].add(b)
    data.adj[b].add(a)


def parse_map(map_path: str) -> MapData:
    data = MapData()

    with open(map_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = strip_comment(raw)
            if not line:
                continue

            if line.startswith("nb_drones:"):
                value = line.split(":", 1)[1].strip()
                if not value.isdigit() or int(value) <= 0:
                    raise ValidationError(f"Line {lineno}: invalid nb_drones")
                data.nb_drones = int(value)
                continue

            if ":" not in line:
                raise ValidationError(f"Line {lineno}: missing ':'")

            kind, rest = line.split(":", 1)
            kind = kind.strip()
            rest = rest.strip()

            if kind in {"start_hub", "end_hub", "hub"}:
                parse_zone_line(kind, rest, data, lineno)
            elif kind == "connection":
                parse_connection_line(rest, data, lineno)
            else:
                raise ValidationError(f"Line {lineno}: unknown directive '{kind}'")

    if data.nb_drones <= 0:
        raise ValidationError("Map: missing or invalid nb_drones")
    if data.start is None:
        raise ValidationError("Map: missing start_hub")
    if data.goal is None:
        raise ValidationError("Map: missing end_hub")

    start_zone = data.zones[data.start]
    if start_zone.max_drones < data.nb_drones:
        data.zones[data.start] = Zone(
            name=start_zone.name,
            zone_type=start_zone.zone_type,
            max_drones=data.nb_drones,
        )

    goal_zone = data.zones[data.goal]
    data.zones[data.goal] = Zone(
        name=goal_zone.name,
        zone_type=goal_zone.zone_type,
        max_drones=max(goal_zone.max_drones, data.nb_drones * 1000),
    )

    return data


def parse_solution(solution_path: str) -> list[list[tuple[str, str]]]:
    turns: list[list[tuple[str, str]]] = []
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    with open(solution_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            line = ansi_re.sub("", line).strip()

            if not line:
                continue

            prefixed = re.match(r"^T\d+:\s*(.*)$", line)
            if prefixed:
                content = prefixed.group(1).strip()
            else:
                content = line

            if not content:
                turns.append([])
                continue

            moves: list[tuple[str, str]] = []
            seen: set[str] = set()

            for token in content.split():
                token = ansi_re.sub("", token).strip()

                if "-" not in token:
                    raise ValidationError(
                        f"Solution line {lineno}: invalid token '{token}'"
                    )

                drone, dest = token.split("-", 1)
                drone = ansi_re.sub("", drone).strip()
                dest = ansi_re.sub("", dest).strip()

                if not re.fullmatch(r"D[1-9]\d*", drone):
                    raise ValidationError(
                        f"Solution line {lineno}: invalid drone id '{drone}'"
                    )

                if drone in seen:
                    raise ValidationError(
                        f"Solution line {lineno}: drone '{drone}' appears twice"
                    )
                seen.add(drone)

                if not dest:
                    raise ValidationError(
                        f"Solution line {lineno}: empty destination for '{drone}'"
                    )

                moves.append((drone, dest))

            turns.append(moves)

    return turns


def is_connection_name(dest: str, map_data: MapData) -> bool:
    if dest.count("-") != 1:
        return False
    a, b = dest.split("-", 1)
    return frozenset((a, b)) in map_data.conn_capacity


def validate_solution(map_data: MapData, turns: list[list[tuple[str, str]]]) -> None:
    assert map_data.start is not None
    assert map_data.goal is not None

    valid_drones = {f"D{i}" for i in range(1, map_data.nb_drones + 1)}
    positions = {f"D{i}": map_data.start for i in range(1, map_data.nb_drones + 1)}
    in_transit: dict[str, TransitState] = {}
    delivered: set[str] = set()

    for turn_index, moves in enumerate(turns, 1):
        move_dict: dict[str, str] = {}

        for drone, dest in moves:
            if drone not in valid_drones:
                raise ValidationError(f"Turn {turn_index}: unknown drone '{drone}'")
            if drone in delivered:
                raise ValidationError(f"Turn {turn_index}: {drone} moved after reaching goal")
            if drone in move_dict:
                raise ValidationError(f"Turn {turn_index}: {drone} appears twice")
            move_dict[drone] = dest

        arriving_this_turn: set[str] = set()
        for drone, transit in in_transit.items():
            actual = move_dict.get(drone)
            if actual is None:
                raise ValidationError(
                    f"Turn {turn_index}: {drone} was in transit and must arrive at '{transit.target}'"
                )
            if actual != transit.target:
                raise ValidationError(
                    f"Turn {turn_index}: {drone} was in transit and must arrive at "
                    f"'{transit.target}', not '{actual}'"
                )
            arriving_this_turn.add(drone)

        for drone, dest in move_dict.items():
            if drone not in in_transit and dest == positions[drone]:
                raise ValidationError(
                    f"Turn {turn_index}: {drone} stays in place but is listed as moving"
                )

        occupancy: dict[str, int] = defaultdict(int)

        for drone, zone in positions.items():
            if drone in delivered:
                continue
            if drone in in_transit:
                continue
            if drone in move_dict:
                continue
            occupancy[zone] += 1

        connection_usage: dict[frozenset[str], int] = defaultdict(int)
        normal_edge_directions: dict[frozenset[str], tuple[str, str]] = {}

        for drone, dest in move_dict.items():
            if drone in arriving_this_turn:
                occupancy[dest] += 1
                if occupancy[dest] > map_data.zones[dest].max_drones:
                    raise ValidationError(
                        f"Turn {turn_index}: zone capacity exceeded at '{dest}'"
                    )
                continue

            origin = positions[drone]

            if is_connection_name(dest, map_data):
                a, b = dest.split("-", 1)
                edge = frozenset((a, b))

                if origin != a and origin != b:
                    raise ValidationError(
                        f"Turn {turn_index}: {drone} uses connection '{dest}' but is at '{origin}'"
                    )

                target = b if origin == a else a
                target_zone = map_data.zones[target]

                if target_zone.zone_type != "restricted":
                    raise ValidationError(
                        f"Turn {turn_index}: connection '{dest}' used as transit but "
                        f"destination '{target}' is not restricted"
                    )

                connection_usage[edge] += 1
                if connection_usage[edge] > map_data.conn_capacity[edge]:
                    raise ValidationError(
                        f"Turn {turn_index}: connection capacity exceeded at '{dest}'"
                    )
                continue

            if dest not in map_data.zones:
                raise ValidationError(
                    f"Turn {turn_index}: destination '{dest}' is neither zone nor connection"
                )

            if dest not in map_data.adj[origin]:
                raise ValidationError(f"Turn {turn_index}: invalid move {origin}->{dest}")

            dest_zone = map_data.zones[dest]

            if dest_zone.zone_type == "blocked":
                raise ValidationError(
                    f"Turn {turn_index}: cannot enter blocked zone '{dest}'"
                )

            if dest_zone.zone_type == "restricted":
                raise ValidationError(
                    f"Turn {turn_index}: entering restricted zone '{dest}' must use connection id"
                )

            edge = frozenset((origin, dest))

            connection_usage[edge] += 1
            if connection_usage[edge] > map_data.conn_capacity[edge]:
                raise ValidationError(
                    f"Turn {turn_index}: connection capacity exceeded at '{origin}-{dest}'"
                )

            previous_direction = normal_edge_directions.get(edge)
            current_direction = (origin, dest)

            if previous_direction is None:
                normal_edge_directions[edge] = current_direction
            elif previous_direction != current_direction:
                raise ValidationError(
                    f"Turn {turn_index}: opposite-direction crossing conflict on '{origin}-{dest}'"
                )

            occupancy[dest] += 1
            if occupancy[dest] > dest_zone.max_drones:
                raise ValidationError(
                    f"Turn {turn_index}: zone capacity exceeded at '{dest}'"
                )

        new_transit: dict[str, TransitState] = {}

        for drone, dest in move_dict.items():
            if drone in arriving_this_turn:
                positions[drone] = dest
                if dest == map_data.goal:
                    delivered.add(drone)
                continue

            if is_connection_name(dest, map_data):
                a, b = dest.split("-", 1)
                origin = positions[drone]
                target = b if origin == a else a
                new_transit[drone] = TransitState(target=target)
            else:
                positions[drone] = dest
                if dest == map_data.goal:
                    delivered.add(drone)

        in_transit = new_transit

    if in_transit:
        pending = ", ".join(
            f"{drone}->{state.target}" for drone, state in sorted(in_transit.items())
        )
        raise ValidationError(
            "Simulation ended with drones still in restricted transit: " + pending
        )

    missing = sorted(valid_drones - delivered)
    if missing:
        raise ValidationError("Not all drones reached goal: " + ", ".join(missing))


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 validate_simulation.py MAP_FILE SOLUTION_FILE")
        return 1

    try:
        map_data = parse_map(sys.argv[1])
        turns = parse_solution(sys.argv[2])
        validate_solution(map_data, turns)
    except ValidationError as exc:
        print(f"INVALID: {exc}")
        return 1
    except FileNotFoundError as exc:
        print(f"ERROR: file not found: {exc.filename}")
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())