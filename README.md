*This project has been created as part of the 42 curriculum by sekartav, fakartal.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator. It is written in Python 3.10 or newer.

The program reads a simple text file. This file holds the settings. Then the
program does four things:

1. It builds a random maze.
2. It finds the shortest path from the entry to the exit.
3. It draws the maze in the terminal with colours.
4. It saves the maze to a file.

The project has two parts:

- **The application** — the file `a_maze_ing.py`. It reads the config file and
  draws the maze. You can make a new maze, show the path, or change the colours.
- **The reusable package** — the folder `mazegen/`. This is a normal Python
  package. You can install it with pip. Another project can import it and use
  the maze code without the terminal interface.

There are two maze modes:

| Mode | What it means |
| --- | --- |
| `PERFECT=True` | A perfect maze. There is only one path between any two cells. There are no loops. |
| `PERFECT=False` | A Pac-Man board. All cells are connected. There are many loops, so a player can always run away. The corners and the centre area are open. |

Every maze also shows a **"42"** pattern. We draw it with cells that keep all
four walls. If the maze is too small for the pattern, the program skips it and
prints a message in the terminal.

---

## Instructions

### What you need

- Python **3.10** or newer.
- Nothing else. The generator only uses the Python standard library.

### How to run it

```bash
python3 a_maze_ing.py config.txt
```

The config file is the only argument. You can use any file name:

```bash
python3 a_maze_ing.py my_other_config.txt
```

### The Makefile

```bash
make install    # install flake8, mypy and build
make run        # python3 a_maze_ing.py config.txt
make debug      # run the program with pdb
make lint       # run flake8 . and mypy with the required flags
make build      # build the package
make clean      # delete __pycache__, .mypy_cache and build files
```

### The menu

The program draws the maze and then shows a menu:

| Key | What it does |
| --- | --- |
| `1` | Build a new maze. It is always random and it does not use `SEED`. |
| `2` | Show or hide the shortest path. |
| `3` | Change the colour theme. There are three themes. |
| `4` | Quit. |

The program writes the output file one time, at the start, from the first maze.
This is what the subject asks for. If you press `1`, the new maze is only drawn
on the screen. It does not change the file.

---

## Configuration file

The file has one `KEY=VALUE` pair on each line. A line that starts with `#` is a
comment, and the program ignores it. The program also ignores the text after a
`#` on a normal line.

This is the `config.txt` file in the repository:

```ini
WIDTH=50
HEIGHT=50
ENTRY=1,1
EXIT=49,49
SEED=
OUTPUT_FILE=maze.txt
PERFECT=False
```

### The keys

| Key | Needed? | Type | What it is |
| --- | --- | --- | --- |
| `WIDTH` | yes | integer | The width of the maze in cells |
| `HEIGHT` | yes | integer | The height of the maze in cells |
| `ENTRY` | yes | `x,y` | The entry cell |
| `EXIT` | yes | `x,y` | The exit cell |
| `OUTPUT_FILE` | yes | text | The name of the output file |
| `PERFECT` | yes | boolean | `True`, `1` or `yes` turn on the perfect mode. `False`, `0` or `no` turn it off. |
| `SEED` | no | integer | It fixes the random numbers. If it is empty, or if you write `None`, the program picks a random seed. |

You can also write the keys in lower case.

### Error handling

The program never crashes. It prints a clear message and stops. It checks these
problems:

- The config file does not exist.
- A line has no `=` sign.
- A key is missing.
- `WIDTH` or `HEIGHT` is not a number, or it is smaller than 1.
- `ENTRY` or `EXIT` is not in the `x,y` format.
- `ENTRY` or `EXIT` is outside the maze.
- `ENTRY` and `EXIT` are the same cell.
- `PERFECT` is not a boolean value.
- The program cannot write the output file.

---

## Output file

The program writes one hexadecimal digit for each cell. Each row of the maze is
one line. The digit says which walls are **closed**. Every wall has a number:

| Bit | Value | Direction |
| --- | --- | --- |
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

We add the values together. For example, `a` is `1010` in binary. So the east
wall and the west wall are closed, and the north and south walls are open. A
cell with the value `f` has all four walls closed.

After the maze there is **one empty line**. Then there are three more lines: the
entry cell, the exit cell, and the shortest path. The path uses the letters `N`,
`E`, `S` and `W`. Every line ends with `\n`.

```
9139551111555515515395153
ac2a9102829113855692c3a92
...
c44556c6c555455546c446c46

1,1
49,49
ESEENEEESSEESESSESESSSSEEEEEESES
```

---

## How it works

### The generation algorithm: recursive backtracker

Both modes start in the same way. We use a **recursive backtracker**. This is a
depth-first search with a stack. It walks through the grid and breaks walls, and
it makes a spanning tree.

A spanning tree is a shape that touches every cell but has no loops.

**Why did we choose this algorithm?**

- It gives a perfect maze directly. A spanning tree has only one path between
  two cells. This is exactly what `PERFECT=True` needs. We do not need any extra
  work or any check after it.
- It makes long corridors that turn a lot. This looks better than the short
  corridors of Prim's or Kruskal's algorithm.
- We use a **stack** instead of real recursion. Python stops a program after
  about 1000 recursive calls. A 50×50 maze can need 2500 calls, so real
  recursion would crash. A stack has no such limit.
- It never breaks a wall on the border, because the code checks the grid
  limits before it moves. So the maze always has walls all around it.

**From a perfect maze to a Pac-Man board.** When `PERFECT=False`, we change the
tree after we build it:

1. `_remove_dead_ends` looks at every cell with three closed walls. A cell like
   this is a dead end. The function opens one of its walls. Each open wall makes
   a new loop. On a 50×50 board we counted **260 loops** and only **3 dead
   ends**. The subject asks for two loops, so this is much more than enough.
2. `_ensure_key_cells_open` opens the four corners and the centre. The subject
   needs them for the ghosts and for the player.

Both functions never open a wall of a "42" cell. So the pattern stays closed.

**The "42" pattern.** Before we start to build, we mark the cells of the pattern
as "visited". The backtracker never enters a visited cell, so these cells keep
all four walls and stay `f`. The pattern sits in the middle of the maze. We
build it only if the maze is at least 4 cells wider and 4 cells taller than the
pattern. The pattern is 7 cells wide and 5 cells tall, so the maze must be at
least 11×9. This free space around the pattern keeps all the other cells
connected. If the maze is smaller, the program prints
`Maze size is too small for pattern 42.` and builds the maze without it.

**No big open areas.** The subject says a corridor cannot be wider than 2 cells.
The backtracker gives us this for free. It only breaks a wall to a cell that it
has never visited. So it can never open a square of 3×3 cells: to do that, it
would need to visit one cell two times. In the `PERFECT=False` mode we open more
walls, but only one wall for each dead end, so this stays true.

### The solving algorithm: breadth-first search

We find the shortest path with a **breadth-first search (BFS)**. The code is in
[mazegen/path_finder.py](mazegen/path_finder.py).

**Why BFS and not A\* or DFS?**

- BFS looks at the near cells first, and then the far cells. So when it arrives
  at a cell, it has used the shortest way. The result is always the shortest
  path.
- DFS finds *a* path, but it is often not the shortest one.
- A\* is a good algorithm, but it is not better here. Its guess about the
  distance is almost always too small in a maze, because of the walls. So A\*
  becomes almost the same as BFS, but it is slower, because it must sort a
  queue. Our grid has only 2500 cells, and BFS needs about 1 millisecond.

**Two small ideas in the code.**

- We use `collections.deque` for the queue. If we used a list, `list.pop(0)`
  would move every item one step to the left every time. That is slow. With a
  deque, `popleft()` is fast.
- We do not keep a `visited` set and a `parent` map. We keep only one grid,
  `came_from`. For each cell it stores the letter of the direction that we used
  to enter it. If a cell has a letter, we already visited it. And the letter is
  the same letter that the output file needs. So at the end we walk back from
  the exit to the entry, we collect the letters, and we reverse them.

---

## The reusable module

The maze code is in the `mazegen` package. It does not need the terminal
interface, so another project can use it.

### Build and install it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install build
python3 -m build
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

The built files `mazegen-1.0.0-py3-none-any.whl` and `mazegen-1.0.0.tar.gz` are
also in the repository. The file `pyproject.toml` has everything that you need
to build them again.

### A simple example

```python
from mazegen import MazeGenerator

# A 20x15 Pac-Man board
maze = MazeGenerator(width=20, height=15, perfect=False)

print(maze.seed)   # the seed of this maze, so you can build it again
```

### The parameters

```python
# A perfect maze. It is the same every time, because of the seed.
maze = MazeGenerator(width=30, height=30, perfect=True, seed=1234)
```

| Parameter | Type | Default | What it is |
| --- | --- | --- | --- |
| `width` | `int` | — | The width in cells |
| `height` | `int` | — | The height in cells |
| `perfect` | `bool` | `False` | `True` for one path only, `False` for a Pac-Man board |
| `seed` | `int \| None` | `None` | It fixes the random numbers. With `None` the class picks a seed and saves it in `.seed`. |

### The maze structure

The class keeps the maze in `maze.wall`. It is a list of rows. Each item is the
number of the closed walls of that cell (N=1, E=2, S=4, W=8).

**Important:** the row comes first and the column comes second. So you write
`wall[y][x]`, not `wall[x][y]`.

```python
maze.wall      # list of lists of int, you read it as wall[y][x]
maze.width     # int
maze.height    # int
maze.seed      # int, the seed of this maze
maze.perfect   # bool, the mode of this maze
```

This is the structure inside the program. The subject says that it does not need
to be the same as the output file. Here each number is in fact one hexadecimal
digit of the file.

### The solution

```python
from mazegen import solve, path_cells

path = solve(maze.wall, maze.width, maze.height, (1, 1), (18, 13))
print(path)          # for example "ESEENEEESSEESESS"

cells = path_cells((1, 1), path)
print(cells[:3])     # [(1, 1), (2, 1), (3, 1)]
```

`solve` gives you a text with the letters `N`, `E`, `S` and `W`. It gives you:

- an empty text `""` if the entry and the exit are the same cell;
- `None` if there is no path. This happens when the entry or the exit is a "42"
  cell, because that cell has all four walls closed.

`path_cells` changes this text into a list of cells. A game or a display needs
this list.

### The same maze every time

Every `MazeGenerator` has its own `random.Random` object. It does not use the
global `random` module. This gives two good things:

- Two mazes with the same seed are exactly the same. We tested it.
- The generator never changes the random numbers of the program that imports it.

---

## The licence

The file [LICENSE.md](LICENSE.md) is at the root of the repository. It uses the
**MIT licence**. This licence is short and it is very open: anybody can use,
copy, change and share this code, in a free project or in a commercial project.
The only rule is to keep the licence text.

We chose it because the subject says that a later project must be able to reuse
this generator. The MIT licence allows this and it does not add any hard
condition.

---

## Project management

### Our roles

We worked on all the parts of the project together. We did the design, the code
and the debugging side by side. We did not give one file to one person. We took
all the decisions about the structure and the algorithms together. So both of us
can explain every part of the code.

### Our plan and how it changed

We planned the work in six steps:

1. Set up the project and the tools.
2. Read and check the config file.
3. Design and write the generator.
4. Write the pathfinder and the output file.
5. Draw the maze in the terminal.
6. Build the package and write the documentation.

Two things changed while we worked:

- **The pathfinder became simpler.** Our first plan was a search on "regions" of
  the maze. While we designed it, we understood a problem: this idea does not
  always give the shortest path, because one region can hide the real best way.
  To make it correct we needed much more work, and our grid is small. So we
  chose a normal BFS. It is always correct and it takes about one millisecond.
- **We added the seed too late.** We thought that the seed was only a small
  extra feature. In fact it was the best tool for debugging. When we could build
  the same maze again, it was much easier to find a bug. We should have written
  it at the beginning.

### What was good and what we can do better

**Good.** We keep the walls of a cell as one number. This made the walls
coherent almost automatically: when we open a wall, one function clears the bit
in the two neighbour cells at the same time. So two cells can never disagree
about a wall.

**Better next time.** We left flake8, mypy and the docstrings for the end. Then
we had to clean many files one by one, and it took a long time. It is cheaper to
run the linters from the first commit. Also, the `mazegen` package still holds
`config_parser.py` and `user_interface.py`. These two files belong to the
application, not to the generator. A cleaner package would keep only the
generation and the solving code.

### Our tools

- **flake8** for the style and **mypy** for the types.
- **Git** for the versions.
- **Visual Studio Code** as the editor.
- Small test scripts that we wrote ourselves. They check the walls, the
  connections and the path on many random mazes.

---

## Resources

### Mazes and graphs

- Jamis Buck, *Maze Generation: Recursive Backtracking* —
  <https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking>
- Walter Pullen, *Think Labyrinth: Maze Algorithms* —
  <https://www.astrolog.org/labyrnth/algrithm.htm>
- Wikipedia, *Maze generation algorithm* —
  <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- Wikipedia, *Spanning tree* — it explains the link between a perfect maze and a
  spanning tree — <https://en.wikipedia.org/wiki/Spanning_tree>

### Pathfinding

- Amit Patel (Red Blob Games), *Introduction to A\** — it compares BFS, Dijkstra
  and A\* with good pictures —
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

### How we used AI

We used Claude (Anthropic) during the project. But we used it only to review our
work and to explain things. **It did not write the source code of this
repository.** We used it for these tasks:

- **To review our code with the subject.** It read the subject next to our files
  and it showed us our mistakes: a missing empty line in the output file, a
  `setdefault` call that deleted the seed from the config, and `wall[x][y]`
  where we needed `wall[y][x]`.
- **To explain algorithms.** Why BFS always gives the shortest path and DFS does
  not. Why a spanning tree is the same thing as a perfect maze. Why the guess of
  A\* must not be too big. After that we wrote the code ourselves.
- **To write test scripts** outside the project. They checked the walls, the
  connections, and our BFS result against another simple version, on many random
  mazes.
- **To write this README, the docstrings and the LICENSE file.** These are
  documents, not source code.

We read and understood every idea before we used it. This is why we can explain
every line of this project.
