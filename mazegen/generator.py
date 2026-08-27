import random
from typing import List, Optional, Tuple
from . import utils


class MazeGenerator:

    def __init__(
        self,
        width: int,
        height: int,
        perfect: bool = False,
        seed: Optional[int] = None,
    ) -> None:

        self.width = width
        self.height = height
        self.perfect = perfect
        if seed is None:
            self.seed: int = random.randrange(2**32)
        else:
            self.seed = seed
        self._rnd_seed = random.Random(self.seed)

        self.wall: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)
        ]
        self.visited: List[List[bool]] = [
            [False for _ in range(width)] for _ in range(height)
        ]

        utils._pattern_42(self.visited, self.width, self.height, self.perfect)

        if self.perfect:
            self._perfect_maze()
        else:
            self._false_maze()

    def _perfect_maze(self) -> None:
        start_x = 0
        start_y = 0
        while self.visited[start_y][start_x]:
            start_x = self._rnd_seed.randint(0, self.width - 1)
            start_y = self._rnd_seed.randint(0, self.height - 1)

        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        self.visited[start_y][start_x] = True

        while stack:
            current_x, current_y = stack[-1]
            neighbors = utils._not_visited_find(
                self.visited, self.width, self.height, current_x, current_y
            )

            if neighbors:
                selected_index = self._rnd_seed.randint(0, len(neighbors) - 1)
                next_x, next_y = neighbors[selected_index]
                utils._break_the_wall_between(
                    self.wall, current_x, current_y, next_x, next_y
                )

                self.visited[next_y][next_x] = True
                stack.append((next_x, next_y))
            else:
                stack.pop()

    def _false_maze(self) -> None:
        self._perfect_maze()
        utils._remove_dead_ends(
            self.wall, self.width, self.height, self._rnd_seed
        )
        utils._ensure_key_cells_open(
            self.wall, self.width, self.height, self._rnd_seed
        )
