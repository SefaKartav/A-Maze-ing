from typing import List


class MazeGenerator:

    pattern_42: List[List[int]] = [
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1]
    ]


    def __init__(self, width: int, height: int, perfect: bool = False) -> None:
        self.width = width
        self.height = height
        self.perfect = perfect

        self.wall: List[List[int]] = [[15 for _ in range(width)] for _ in range(height)]
        self.visited: List[List[bool]] = [[ False for _ in range(width)] for _ in range(height)]


    def _pattern_42(self) -> None:
        pattern_h = len(self.pattern_42)
        pattern_w = len(self.pattern_42[0])

        if self.width < self.pattern_w + 4 or self.height < pattern_h + 4:
            print()