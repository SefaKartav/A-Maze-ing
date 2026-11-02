"""Main program: reads the config file, draws the maze and saves it."""

from mazegen.config_parser import ConfigParser
from mazegen.generator import MazeGenerator
from mazegen.user_interface import SoftTerminalUI
import sys
from mazegen.path_finder import solve, path_cells


if len(sys.argv) != 2:
    print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
    sys.exit(1)

try:
    config = ConfigParser(sys.argv[1]).parse()
except (OSError, ValueError, UnicodeDecodeError) as err:
    print(f"Error: {err}", file=sys.stderr)
    sys.exit(1)


gen = MazeGenerator(
    config["WIDTH"], config["HEIGHT"], config["PERFECT"], config["SEED"]
)


path = solve(gen.wall, gen.width, gen.height, config["ENTRY"], config["EXIT"])
path_to_cells = path_cells(config["ENTRY"], path or "")

ui = SoftTerminalUI(entry=config["ENTRY"], exit_pos=config["EXIT"])

try:
    ConfigParser.write_maze_output(
        config["OUTPUT_FILE"],
        gen.wall,
        config["ENTRY"],
        config["EXIT"],
        path or ""
    )
except OSError as err:
    print(f"Error: could not write the output file: {err}", file=sys.stderr)
    sys.exit(1)

while True:
    ui.render(gen.wall, gen.width, gen.height, path_to_cells)
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Quit")
    try:
        choice = input("Choice? (1-4): ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if choice == "1":
        gen = MazeGenerator(
            config["WIDTH"], config["HEIGHT"], config["PERFECT"]
        )
        path = solve(
            gen.wall, gen.width, gen.height,
            config["ENTRY"], config["EXIT"],
        )

        path_to_cells = path_cells(config["ENTRY"], path or "")

    elif choice == "2":
        ui.toggle_path()
    elif choice == "3":
        ui.rotate_colors()
    elif choice == "4":
        break
