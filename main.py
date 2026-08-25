from mazegen.config_parser import ConfigParser
from mazegen.generator import MazeGenerator 
from mazegen.user_interface import NeonTerminalUI

config = ConfigParser("config.txt").parse()

gen = MazeGenerator(config["WIDTH"], config["HEIGHT"], config["PERFECT"])

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
ConfigParser.write_maze_output("output.txt", gen.wall, config["ENTRY"], config["EXIT"])