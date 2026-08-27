*This project has been created as part of the 42 curriculum by sekartav, fakartal.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python 3.10+. It reads a plain-text
configuration file, generates a maze in one of two modes, solves it, renders it
in the terminal, and writes the result to a file using a hexadecimal wall
encoding.

The project has two faces:

- **The application** (`a_maze_ing.py`) — reads a config file, draws the maze in
  the terminal with ANSI colours, and lets you regenerate it, toggle the
  shortest path, or cycle the colour theme.
- **The reusable package** (`mazegen/`) — a standalone, pip-installable module
  that exposes the generation and solving logic so that later projects can
  import it without dragging the terminal interface along.

Two generation modes are supported:

| Mode | Meaning |
| --- | --- |
| `PERFECT=True` | A *perfect* maze: exactly one path between any two cells, no loops at all. |
| `PERFECT=False` | A **Pac-Man-usable board**: fully connected, at least two independent routes, corners and centre open, and virtually no dead-ends. |

Every maze contains a visible **"42"** drawn with fully closed cells at its
centre. If the maze is too small to fit the pattern, it is skipped and a message
is printed to the console.

---

## Instructions

### Requirements

- Python **3.10** or later
- No third-party runtime dependencies — the generator uses only the standard
  library

### Running

```bash
python3 a_maze_ing.py config.txt
```

The configuration file is the only argument. Any filename works:

```bash
python3 a_maze_ing.py my_other_config.txt
```

### Using the Makefile

```bash
make install    # install development dependencies (flake8, mypy, build)
make run        # python3 a_maze_ing.py config.txt
make debug      # run under pdb
make lint       # flake8 . and mypy with the mandatory flags
make clean      # remove __pycache__, .mypy_cache and build artefacts
```

### Interactive controls

Once the maze is drawn, the menu offers:

| Key | Action |
| --- | --- |
| `1` | Generate a brand-new maze (always random, ignores `SEED`) |
| `2` | Show / hide the shortest path from entry to exit |
| `3` | Rotate through the colour themes |
| `4` | Quit and write the output file |

---

## Configuration file format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and are
ignored, as is anything after a `#` on a value line.

```ini
# Maze dimensions, in cells
WIDTH=50
HEIGHT=50

# Entry and exit coordinates, as x,y
ENTRY=1,1
EXIT=45,45

# Leave empty (or write None) for a random maze every run
SEED=

# Where the hexadecimal maze is written
OUTPUT_FILE=maze.txt

# True  -> perfect maze (single path, no loops)
# False -> Pac-Man board (loops, no dead-ends)
PERFECT=True
```

### Keys

| Key | Mandatory | Type | Description |
| --- | --- | --- | --- |
| `WIDTH` | yes | integer | Maze width in cells |
| `HEIGHT` | yes | integer | Maze height in cells |
| `ENTRY` | yes | `x,y` | Entry coordinates |
| `EXIT` | yes | `x,y` | Exit coordinates |
| `OUTPUT_FILE` | yes | string | Output filename |
| `PERFECT` | yes | boolean | `True`, `1` or `yes` enable perfect mode |
| `SEED` | no | integer | Fixes the random seed; empty or `None` means "pick one at random" |

A default `config.txt` is provided at the root of the repository.

### Output file format

The generated file contains one hexadecimal digit per cell, one row per line.
Each digit encodes the **closed** walls of that cell as a bitmask:

| Bit | Value | Direction |
| --- | --- | --- |
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

So `a` (binary `1010`) means the east and west walls are closed, while the north
and south walls are open.

After the grid comes **one empty line**, then three more lines: the entry
coordinates, the exit coordinates, and the shortest path expressed with the
letters `N`, `E`, `S`, `W`.

```
9139551111555515515395153
ac2a9102829113855692c3a92
...
c44556c6c555455546c446c46

1,1
45,45
ESEENEEESSEESESSESESSSSEEEEEESES
```

The provided `maze_analyzer.py` can be used to check a generated file:

```bash
python3 maze_analyzer.py maze.txt
```

---

## Technical choices

### Generation algorithm: iterative recursive backtracker

Both modes start from the same base: a **recursive backtracker** (depth-first
search with an explicit stack) that carves a spanning tree over the grid.

**Why this algorithm?**

- It produces a *perfect* maze by construction. A spanning tree has exactly one
  path between any two nodes, which is precisely what `PERFECT=True` requires —
  no post-processing, no verification pass.
- It creates long, winding corridors, which look far more maze-like than the
  short, bushy passages that Prim's or Kruskal's algorithms tend to produce.
- The **iterative** form (an explicit stack instead of recursion) avoids
  Python's recursion limit. A 50×50 maze would need a call depth of up to 2500,
  well past the default limit of 1000.
- It never opens a border wall, because neighbour lookups are bounds-checked, so
  the "walls at the external borders" requirement is satisfied for free.

**Getting from a perfect maze to a Pac-Man board.** When `PERFECT=False`, the
spanning tree is post-processed:

1. `_remove_dead_ends` scans every cell with exactly three closed walls and
   opens one of them at random. Each wall removed adds an independent loop, so a
   50×50 board ends up with roughly 260 of them — far beyond the two the subject
   requires.
2. `_ensure_key_cells_open` makes sure the four corners and the centre are open
   corridors, as required for ghosts, super-pac-gums, and the player's start.

Both steps refuse to open a wall that faces a "42" cell, which keeps the pattern
intact.

**The "42" pattern.** Before any carving happens, the cells forming the pattern
are marked as already visited. The backtracker therefore never enters them and
they stay fully closed (`f`). The pattern is centred, and the check that the
maze is at least four cells wider and taller than the pattern guarantees the
surrounding corridors stay connected.

### Solving algorithm: breadth-first search

The shortest path is found with a **BFS** over the cell graph
(`mazegen/path_finder.py`).

**Why BFS rather than A\* or DFS?**

- BFS explores cells in order of increasing distance from the entry, so the
  first time it reaches a cell it has done so by a shortest route. That gives
  the *shortest* path the subject asks for, with no extra proof needed.
- DFS would find *a* path, but not necessarily the shortest one.
- A\* with a Manhattan heuristic is admissible here, but walls weaken the
  heuristic badly in a maze: the estimated distance is almost always far below
  the real one, so A\* degenerates towards BFS while paying for a priority
  queue. On a 2500-cell grid BFS already completes in about 1 ms.

**Implementation notes.**

- A `collections.deque` is used as the queue: `list.pop(0)` is O(n) and would
  dominate the runtime on a grid this size, while `deque.popleft()` is O(1).
- Instead of a separate `visited` set plus a `parent` map, a single `came_from`
  grid stores *which direction was used to enter each cell*. A non-`None` entry
  means "already visited", and the stored letter is exactly what the output path
  string needs — so reconstructing the path is a matter of walking backwards
  from the exit and reversing the collected letters.
- No bounds checking is needed inside the loop. The outer border walls are
  always closed, so the wall-bit test can never move the search off the grid.

---

## Reusable module

The generation and solving logic lives in the `mazegen` package, which is
independent of the terminal interface and can be installed with pip.

### Building and installing

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install build
python3 -m build          # produces dist/mazegen-1.0.0-py3-none-any.whl
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen.generator import MazeGenerator

# A 20x15 Pac-Man style board
maze = MazeGenerator(width=20, height=15, perfect=False)

print(maze.wall[0][0])   # wall bitmask of the top-left cell
print(maze.seed)         # the seed actually used, so you can reproduce it
```

### Custom parameters

```python
# A perfect maze, reproducible across runs
maze = MazeGenerator(width=30, height=30, perfect=True, seed=1234)
```

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `width` | `int` | — | Maze width in cells |
| `height` | `int` | — | Maze height in cells |
| `perfect` | `bool` | `False` | `True` for a single-path maze, `False` for a Pac-Man board |
| `seed` | `int \| None` | `None` | Fixes the RNG; `None` picks a random seed and stores it in `.seed` |

### Accessing the structure and a solution

The generator exposes the maze as a list of rows of integers, where each integer
is the bitmask of that cell's closed walls (N=1, E=2, S=4, W=8):

```python
maze.wall      # List[List[int]], indexed as wall[y][x]
maze.width     # int
maze.height    # int
maze.seed      # int, the seed that produced this maze
```

Note that this is the *in-memory* structure; it is not required to match the
output file byte for byte, though in practice each integer maps to one
hexadecimal digit.

A shortest path between any two cells is obtained from the solver:

```python
from mazegen.path_finder import solve, path_cells

path = solve(maze.wall, maze.width, maze.height, (1, 1), (18, 13))
print(path)          # e.g. "ESEENEEESSEESESS"

cells = path_cells((1, 1), path)
print(cells[:3])     # [(1, 1), (2, 1), (3, 1)]
```

`solve` returns a string of `N`/`E`/`S`/`W` letters, `""` when entry and exit are
the same cell, and `None` when no path exists (for instance if the exit sits on
a "42" cell). `path_cells` converts that string into the list of coordinates the
path visits, which is what a renderer or a game needs.

### Reproducibility

Every generator instance owns a private `random.Random` instance rather than
touching the global `random` module. Two generators built with the same seed
produce byte-identical mazes, and a generator never disturbs the random state of
the program that imports it.

---

## Project management

### Team roles

Both of us worked on every part of the project together — design, coding, and
debugging were done side by side rather than split into separate ownerships.
Decisions about the architecture, the algorithms, and the file layout were made
jointly, and both of us can explain and defend any part of the code.

### Planning and how it evolved

The work was planned in six phases, tracked in
`A-Maze-ing_ToDo_List_v2.md`:

1. Project setup and tooling
2. Configuration management
3. Algorithm architecture and generation
4. Pathfinding and output
5. Visual representation
6. Packaging and documentation

The plan changed in two meaningful ways as we went:

- **The pathfinder was simplified.** The original plan called for a hierarchical
  search that treated "regional gates" as graph nodes. While designing it we
  realised the naive version does not guarantee a shortest path — collapsing a
  region into a single distance can hide the real optimum — and that making it
  correct would take substantially more work for no measurable gain on a
  2500-cell grid. We chose a plain BFS, which is provably optimal and runs in
  about a millisecond.
- **Seeding was added later than it should have been.** Reproducibility was
  treated as a finishing touch, but it turned out to be the tool that made
  debugging the generator practical. Being able to replay the exact maze that
  triggered a bug saved a lot of time once it existed.

### What worked well, what could be improved

**Worked well.** Keeping the wall encoding as a single integer bitmask per cell
made the coherence requirement almost automatic: opening a wall always clears
the matching bit in both neighbours, in one helper function. Validating against
the provided `maze_analyzer.py` early gave us a hard, objective target instead
of a subjective "looks fine".

**Could be improved.** The code-quality work (flake8, mypy, docstrings) was left
until the end and turned into a long mechanical cleanup; running the linters
from the first commit would have been cheaper. The `mazegen` package also still
contains `config_parser.py` and `user_interface.py`, which are application
concerns rather than generator concerns — a cleaner split would leave only the
generation and solving logic inside the reusable package.

### Tools used

- **flake8** and **mypy** for style and static type checking
- **`maze_analyzer.py`**, provided with the subject, as the correctness oracle
- **Git** for version control
- **Visual Studio Code** as the editor

---

## Resources

### Maze generation and graph theory

- Jamis Buck, *Maze Generation: Recursive Backtracking* —
  <https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking>
- Walter Pullen, *Think Labyrinth: Maze Algorithms* —
  <https://www.astrolog.org/labyrnth/algrithm.htm>
- Wikipedia, *Maze generation algorithm* —
  <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- Wikipedia, *Spanning tree* — the formal link between perfect mazes and
  spanning trees — <https://en.wikipedia.org/wiki/Spanning_tree>

### Pathfinding

- Amit Patel (Red Blob Games), *Introduction to A\** — an excellent visual
  comparison of BFS, Dijkstra and A\* —
  <https://www.redblobgames.com/pathfinding/a-star/introduction.html>
- Wikipedia, *Breadth-first search* —
  <https://en.wikipedia.org/wiki/Breadth-first_search>

### Python

- PEP 257, *Docstring Conventions* — <https://peps.python.org/pep-0257/>
- PEP 484, *Type Hints* — <https://peps.python.org/pep-0484/>
- Python documentation, `collections.deque` —
  <https://docs.python.org/3/library/collections.html#collections.deque>
- Python Packaging User Guide, *Packaging Python Projects* —
  <https://packaging.python.org/en/latest/tutorials/packaging-projects/>
- Choose a License — <https://choosealicense.com/>

### How AI was used

We used Claude (Anthropic) throughout the project, but deliberately restricted
it to a reviewing and explaining role: **it did not write any of the source code
in this repository.** Concretely, it was used for:

- **Reviewing our code against the subject.** Reading the PDF alongside our
  files and reporting mismatches — a missing blank line in the output file that
  made `maze_analyzer.py` reject it, a `setdefault` call that silently discarded
  the configured seed, `wall[x][y]` written where `wall[y][x]` was meant.
- **Explaining algorithms.** Why BFS guarantees a shortest path while DFS does
  not, why a spanning tree is exactly a perfect maze, and why an admissible
  heuristic matters for A\*. We then implemented the algorithms ourselves.
- **Reading the provided analyser.** Working out what `maze_analyzer.py`
  actually expects — where it stops parsing the grid, how it counts loops, and
  why it tolerates dead-ends enclosed by the "42" pattern.
- **Writing verification scripts** kept outside the project tree, which checked
  properties such as wall coherence, connectivity, and whether our BFS result
  matched a reference implementation over dozens of random mazes.
- **Drafting this README and the LICENSE file**, which are documentation rather
  than source code.

Every suggestion was applied by hand after we understood it, which is why we can
explain any line of this project.
