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
        self._generate_perfect_maze()

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

    def _perfect_maze(self) -> None:
        