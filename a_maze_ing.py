from mazegen.config_parser import ConfigParser
from mazegen.generator import MazeGenerator 
from mazegen.user_interface import NeonTerminalUI
import sys
if len(sys.argv) != 2:
    print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
    sys.exit(1)

try:
    config = ConfigParser(sys.argv[1]).parse()
except (FileNotFoundError, ValueError) as err:
    print(f"Error: {err}", file=sys.stderr)
    sys.exit(1)


gen = MazeGenerator(config["WIDTH"], config["HEIGHT"], config["PERFECT"], config["SEED"])

ui = NeonTerminalUI(entry=config["ENTRY"], exit_pos=config["EXIT"])

while True:
    ui.render(gen.wall, gen.width, gen.height)
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Quit")
    choice = input("Choice? (1-4): ").strip()

    if choice == "1":
        gen = MazeGenerator(config["WIDTH"], config["HEIGHT"], config["PERFECT"])
    elif choice == "2":
        ui.toggle_path()
    elif choice == "3":
        ui.rotate_colors()
    elif choice == "4":
        break
ConfigParser.write_maze_output(
    config["OUTPUT_FILE"],
    gen.wall,
    config["ENTRY"],
    config["EXIT"],
)
