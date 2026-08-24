from typing import List, Tuple, Optional


class Colors:
    RESET = "\033[0m"

    WALL = "\033[48;2;25;35;50m"
    EMPTY = "\033[48;2;10;15;20m"
    PATH = "\033[48;2;0;255;255m"
    ENTRY = "\033[48;2;219;112;147m"
    EXIT = "\033[48;2;255;100;100m"
    PATTERN_42 = "\033[48;2;230;240;255m"


class NeonTerminalUI:
    def __init__(self, entry: Tuple[int, int], exit_pos: Tuple[int, int]) -> None:
        self.entry = entry
        self.exit_pos = exit_pos
        self.show_path: bool = False

    def toggle_path(self) -> None:
        self.show_path = not self.show_path

    def _get_cell_bg(self, x: int, y: int, wall_value: int, path: List[Tuple[int, int]]) -> str:
        if (x, y) == self.entry:
            return Colors.ENTRY
        if (x, y) == self.exit_pos:
            return Colors.EXIT
        if wall_value == 15:
            return Colors.PATTERN_42
        if self.show_path and (x, y) in path:
            return Colors.PATH
        return Colors.EMPTY

    def render(self, wall: List[List[int]], width: int, height: int, path: Optional[List[Tuple[int, int]]] = None) -> None:
        if path is None:
            path = []

        print("\n" + Colors.WALL + "   " * width + Colors.RESET)
        
        for y in range(height):
            top_line = ""
            mid_line = ""
            for x in range(width):
                cell_val = wall[y][x]
                
                bg = self._get_cell_bg(x, y, cell_val, path)
                wall_bg = Colors.WALL
                reset = Colors.RESET

                if cell_val & 1:
                    top_line += f"{wall_bg}   {reset}"
                else:
                    top_line += f"{wall_bg} {reset}{bg} {reset}{wall_bg} {reset}"

                left = f"{wall_bg} {reset}" if (cell_val & 8) else f"{bg} {reset}"
                right = f"{wall_bg} {reset}" if (cell_val & 2) else f"{bg} {reset}"
                
                mid_line += f"{left}{bg} {reset}{right}"

            print(top_line)
            print(mid_line)

            if y == height - 1:
                bottom_line = ""
                for x in range(width):
                    if wall[y][x] & 4:
                        bottom_line += f"{Colors.WALL}   {Colors.RESET}"
                    else:
                        bottom_line += f"{Colors.WALL} {Colors.RESET}{Colors.EMPTY} {NeonColors.RESET}{NeonColors.WALL} {NeonColors.RESET}"
                print(bottom_line)
                
        print(Colors.WALL + "   " * width + Colors.RESET + "\n")