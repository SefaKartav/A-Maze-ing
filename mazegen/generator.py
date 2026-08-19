import random
from typing import List, Tuple, Dict

class MazeGenerator:

    PATTERN_42: List[List[int]] = [
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1]
    ]

    directions: Dict[str, Tuple[int, int, int, int]] = {
        'N': (0, -1, 1, 4),
        'S': (0, 1, 4, 1),
        'E': (1, 0, 2, 8),
        'W': (-1, 0, 8, 2)
    }

    def __init__(self, width: int, height: int, perfect: bool = False) -> None:
        self.width = width
        self.height = height
        self.perfect = perfect

        self.wall: List[List[int]] = [[15 for _ in range(width)] for _ in range(height)]
        self.visited: List[List[bool]] = [[False for _ in range(width)] for _ in range(height)]

        self._pattern_42()
        self._perfect_maze()

    def _pattern_42(self) -> None:
        pattern_h = len(self.PATTERN_42)
        pattern_w = len(self.PATTERN_42[0])

        if self.width < pattern_w + 4 or self.height < pattern_h + 4:
            print("Maze size is too small for pattern 42.")
            return

        start_y = 1
        start_x = 1

        for y in range(pattern_h):
            for x in range(pattern_w):
                if self.PATTERN_42[y][x] == 1:
                    self.visited[start_y + y][start_x + x] = True

    def _not_visited_find(self, x: int, y: int) -> List[Tuple[int, int]]:
        adjoining_walls = []

        if y - 1 >= 0 and not self.visited[y - 1][x]:
            adjoining_walls.append((x, y - 1))
        if y + 1 < self.height and not self.visited[y + 1][x]:
            adjoining_walls.append((x, y + 1))
        if x + 1 < self.width and not self.visited[y][x + 1]:
            adjoining_walls.append((x + 1, y))
        if x - 1 >= 0 and not self.visited[y][x - 1]:
            adjoining_walls.append((x - 1, y))

        return adjoining_walls

    def _break_the_wall_between(self, current_x: int,
                                current_y: int, next_x: int, next_y: int) -> None:
        if next_x == current_x + 1:
            self.wall[current_y][current_x] &= ~2
            self.wall[next_y][next_x] &= ~8

        if next_y == current_y + 1:
            self.wall[current_y][current_x] &= ~4
            self.wall[next_y][next_x] &= ~1

        if next_x == current_x - 1:
            self.wall[current_y][current_x] &= ~8
            self.wall[next_y][next_x] &= ~2

        if next_y == current_y - 1:
            self.wall[current_y][current_x] &= ~1
            self.wall[next_y][next_x] &= ~4

    def _perfect_maze(self) -> None:
        start_x = 0
        start_y = 0
        while self.visited[start_y][start_x]:
            start_x = random.randint(0, self.width - 1)
            start_y = random.randint(0, self.height - 1)
            
        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        self.visited[start_y][start_x] = True

        while stack:
            current_x, current_y = stack[-1]
            neighbors = self._not_visited_find(current_x, current_y)

            if neighbors:
                selected_index = random.randint(0, len(neighbors) - 1)
                next_x, next_y = neighbors[selected_index]
                self._break_the_wall_between(current_x, current_y, next_x, next_y)
                self.visited[next_y][next_x] = True
                stack.append((next_x, next_y))
            else:
                stack.pop()