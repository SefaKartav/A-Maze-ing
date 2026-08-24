from typing import List


class MazeCell:

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    def __init__(self) -> None:
        self.walls: int = 15

    def remove_wall(self, direction: int) -> None:
        self.walls &= ~direction

    def add_wall(self, direction: int) -> None:
        self.walls |= direction

    def has_wall(self, direction: int) -> bool:
        return bool(self.walls & direction)


class MazeGrid:

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid: List[List[MazeCell]] = [[MazeCell() for _ in range(width)] for _ in range(height)]

    def get_cell(self, x: int, y: int) -> MazeCell:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Cell coordinates out of bounds: ({x}, {y})")
        return self.grid[y][x]