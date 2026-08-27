from collections import deque
from typing import List, Optional, Tuple


DIRECTIONS: Tuple[Tuple[int, int, int, str], ...] = (
    (1, 0, -1, "N"),
    (2, 1, 0, "E"),
    (4, 0, 1, "S"),
    (8, -1, 0, "W")
)

BACK = {
    "N": (0, 1),
    "E": (-1, 0),
    "S": (0, -1),
    "W": (1, 0)
}

STEP = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0)
}


def solve(
        wall: List[List[int]],
        width: int,
        height: int,
        entry_pos: Tuple[int, int],
        exit_pos: Tuple[int, int]
) -> Optional[str]:
    ex, ey = entry_pos
    xx, xy = exit_pos

    if entry_pos == exit_pos:
        return ""

    if wall[xy][xx] == 15 or wall[ey][ex] == 15:
        return None

    came_from: List[List[Optional[str]]] = [
        [None] * width for _ in range(height)
    ]
    came_from[ey][ex] = "*"

    queue = deque([entry_pos])
    while queue:
        x, y = queue.popleft()
        if (x, y) == exit_pos:
            break
        for bit, dx, dy, letter in DIRECTIONS:
            if wall[y][x] & bit:
                continue
            nx, ny = x + dx, y + dy

            if came_from[ny][nx] is not None:
                continue
            came_from[ny][nx] = letter
            queue.append((nx, ny))

    if came_from[xy][xx] is None:
        return None

    letters = []
    x, y = exit_pos

    while (x, y) != entry_pos:
        came = came_from[y][x]
        if came is None:
            return None
        letters.append(came)
        bdx, bdy = BACK[came]
        x, y = x + bdx, y + bdy
    return "".join(reversed(letters))


def path_cells(
    entry_pos: Tuple[int, int],
    path: str,
) -> List[Tuple[int, int]]:
    cells = [entry_pos]
    x, y = entry_pos

    for letter in path:
        dx, dy = STEP[letter]
        x = x + dx
        y = y + dy
        cells.append((x, y))

    return cells
