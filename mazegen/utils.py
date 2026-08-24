import random
from typing import List, Tuple, Dict

PATTERN_42: List[List[int]] = [
    [1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1]
]

PATTERN_42_FALSE: List[List[int]] = [
    [1, 0, 1, 1, 1, 1],
    [1, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1]
]

directions: Dict[str, Tuple[int, int, int, int]] = {
    'N': (0, -1, 1, 4),
    'S': (0, 1, 4, 1),
    'E': (1, 0, 2, 8),
    'W': (-1, 0, 8, 2)
}

def _pattern_42(visited: List[List[bool]], width: int, height: int, perfect: bool) -> None:
    active_pattern = PATTERN_42 if perfect else PATTERN_42_FALSE
    pattern_h = len(PATTERN_42)
    pattern_w = len(PATTERN_42[0])

    if width < pattern_w + 4 or height < pattern_h + 4:
        print("Maze size is too small for pattern 42.")
        return

    start_y = (height - pattern_h) // 2
    start_x = (width - pattern_w) // 2

    for y in range(pattern_h):
        for x in range(pattern_w):
            if active_pattern[y][x] == 1:
                visited[start_y + y][start_x + x] = True

def _not_visited_find(visited: List[List[bool]], width: int, height: int, x: int, y: int) -> List[Tuple[int, int]]:
    adjoining_walls = []

    if y - 1 >= 0 and not visited[y - 1][x]:
        adjoining_walls.append((x, y - 1))
    if y + 1 < height and not visited[y + 1][x]:
        adjoining_walls.append((x, y + 1))
    if x + 1 < width and not visited[y][x + 1]:
        adjoining_walls.append((x + 1, y))
    if x - 1 >= 0 and not visited[y][x - 1]:
        adjoining_walls.append((x - 1, y))

    return adjoining_walls

def _break_the_wall_between(wall: List[List[int]], current_x: int, current_y: int, next_x: int, next_y: int) -> None:
    if next_x == current_x + 1:
        wall[current_y][current_x] &= ~2
        wall[next_y][next_x] &= ~8

    if next_y == current_y + 1:
        wall[current_y][current_x] &= ~4
        wall[next_y][next_x] &= ~1

    if next_x == current_x - 1:
        wall[current_y][current_x] &= ~8
        wall[next_y][next_x] &= ~2

    if next_y == current_y - 1:
        wall[current_y][current_x] &= ~1
        wall[next_y][next_x] &= ~4

def _count_closed_walls(wall: List[List[int]], x: int, y: int) -> int:
    return bin(wall[y][x]).count('1')

def _break_random_wall(wall: List[List[int]], width: int, height: int, x: int, y: int) -> None:
    breakable_list = []

    if (wall[y][x] & 1) and y - 1 >= 0 and wall[y - 1][x] != 15:
        breakable_list.append((x, y - 1))
    if (wall[y][x] & 2) and x + 1 < width and wall[y][x + 1] != 15:
        breakable_list.append((x + 1, y))
    if (wall[y][x] & 4) and y + 1 < height and wall[y + 1][x] != 15:
        breakable_list.append((x, y + 1))
    if (wall[y][x] & 8) and x - 1 >= 0 and wall[y][x - 1] != 15:
        breakable_list.append((x - 1, y))

    if breakable_list:
        br_next_x, br_next_y = random.choice(breakable_list)
        _break_the_wall_between(wall, x, y, br_next_x, br_next_y)

def _remove_dead_ends(wall: List[List[int]], width: int, height: int) -> List[Tuple[int, int]]:
    for y in range(height):
        for x in range(width):
            if wall[y][x] == 15:
                continue

            if _count_closed_walls(wall, x, y) == 3:
                _break_random_wall(wall, width, height, x, y)

def _ensure_key_cells_open(wall: List[List[int]], width: int, height: int) -> None:
    center_x = width // 2
    center_y = height // 2
    
    key_points = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
        (center_x, center_y)
    ]
    
    for x, y in key_points:
        if 0 <= x < width and 0 <= y < height:
            if wall[y][x] != 15:
                attempts = 0
                while _count_closed_walls(wall, x, y) >= 3 and attempts < 4:
                    _break_random_wall(wall, width, height, x, y)
                    attempts += 1