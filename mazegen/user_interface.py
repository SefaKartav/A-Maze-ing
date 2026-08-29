from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class StyleConfig:

    wall_h: str = "───"
    wall_v: str = "│"
    corner_tl: str = "╭"
    corner_tr: str = "╮"
    corner_bl: str = "╰"
    corner_br: str = "╯"
    cross: str = "┼"
    t_left: str = "├"
    t_right: str = "┤"
    t_top: str = "┬"
    t_bottom: str = "┴"

    entry_glyph: str = " ▢ "
    exit_glyph: str = " ▣ "
    path_glyph: str = " ◆ "
    pattern_42_glyph: str = " █ "
    empty_glyph: str = "   "


@dataclass
class ColorTheme:

    name: str
    wall_fg: str
    wall_bg: str
    empty_bg: str
    path_bg: str
    entry_bg: str
    exit_bg: str
    pattern_42_bg: str
    reset: str = "\033[0m"


class ThemeManager:

    def __init__(self) -> None:
        self.themes: List[ColorTheme] = [
            ColorTheme(
                name="Mavi-Sarı-Kırmızı Kontrast",
                wall_fg="\033[38;2;100;130;170m",
                wall_bg="\033[48;2;20;28;40m",
                empty_bg="\033[48;2;10;14;20m",
                path_bg="\033[48;2;0;128;255m",  # Canlı Mavi
                entry_bg="\033[48;2;255;50;50m",  # Canlı Kırmızı
                exit_bg="\033[48;2;255;215;0m",  # Parlak Sarı
                pattern_42_bg="\033[48;2;255;255;255m",  # Saf Beyaz
            ),
            ColorTheme(
                name="Neon Cyberpunk",
                wall_fg="\033[38;2;180;50;220m",
                wall_bg="\033[48;2;30;10;40m",
                empty_bg="\033[48;2;15;5;20m",
                path_bg="\033[48;2;0;255;200m",
                entry_bg="\033[48;2;255;0;100m",
                exit_bg="\033[48;2;255;230;0m",
                pattern_42_bg="\033[48;2;240;240;255m",
            ),
            ColorTheme(
                name="Monokrom Yumuşak",
                wall_fg="\033[38;2;160;160;160m",
                wall_bg="\033[48;2;35;35;35m",
                empty_bg="\033[48;2;18;18;18m",
                path_bg="\033[48;2;70;130;180m",
                entry_bg="\033[48;2;200;80;80m",
                exit_bg="\033[48;2;220;180;70m",
                pattern_42_bg="\033[48;2;255;255;255m",
            ),
        ]
        self._current_index: int = 0

    @property
    def current(self) -> ColorTheme:
        return self.themes[self._current_index]

    def rotate(self) -> ColorTheme:
        self._current_index = (self._current_index + 1) % len(self.themes)
        return self.current


class SoftTerminalUI:

    def __init__(
        self,
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        style: Optional[StyleConfig] = None,
    ) -> None:
        self.entry: Tuple[int, int] = entry
        self.exit_pos: Tuple[int, int] = exit_pos
        self.style: StyleConfig = style if style else StyleConfig()
        self.theme_mgr: ThemeManager = ThemeManager()
        self.show_path: bool = False

    def toggle_path(self) -> None:
        """Çözüm yolunu açıp kapatır."""
        self.show_path = not self.show_path

    def rotate_colors(self) -> None:
        """Tema rengini değiştirir."""
        self.theme_mgr.rotate()

    def _get_junction_char(
        self, north: bool, south: bool, east: bool, west: bool
    ) -> str:
        s = self.style
        if north and south and east and west:
            return s.cross
        if north and south and east:
            return s.t_left
        if north and south and west:
            return s.t_right
        if east and west and south:
            return s.t_top
        if east and west and north:
            return s.t_bottom
        if south and east:
            return s.corner_tl
        if south and west:
            return s.corner_tr
        if north and east:
            return s.corner_bl
        if north and west:
            return s.corner_br
        if east or west:
            return "─"
        if north or south:
            return s.wall_v
        return " "

    def _has_wall(
        self, wall_matrix: List[List[int]], x: int, y: int, bit: int
    ) -> bool:
        if 0 <= y < len(wall_matrix) and 0 <= x < len(wall_matrix[0]):
            return bool(wall_matrix[y][x] & bit)
        return False

    def _render_junction(
        self, wall: List[List[int]], jx: int, jy: int, theme: ColorTheme
    ) -> str:
        has_north = self._has_wall(wall, jx, jy - 1, 8) or self._has_wall(
            wall, jx - 1, jy - 1, 2
        )
        has_south = self._has_wall(wall, jx, jy, 8) or self._has_wall(
            wall, jx - 1, jy, 2
        )
        has_east = self._has_wall(wall, jx, jy, 1) or self._has_wall(
            wall, jx, jy - 1, 4
        )
        has_west = self._has_wall(wall, jx - 1, jy, 1) or self._has_wall(
            wall, jx - 1, jy - 1, 4
        )

        char = self._get_junction_char(
            has_north, has_south, has_east, has_west
        )
        return f"{theme.wall_bg}{theme.wall_fg}{char}{theme.reset}"

    def _get_cell_visuals(
        self,
        x: int,
        y: int,
        cell_val: int,
        path: List[Tuple[int, int]],
        theme: ColorTheme,
    ) -> Tuple[str, str]:
        if (x, y) == self.entry:
            return theme.entry_bg, self.style.entry_glyph
        if (x, y) == self.exit_pos:
            return theme.exit_bg, self.style.exit_glyph
        if cell_val == 15:
            return theme.pattern_42_bg, self.style.pattern_42_glyph
        if self.show_path and (x, y) in path:
            return theme.empty_bg, self.style.path_glyph
        return theme.empty_bg, self.style.empty_glyph

    def render(
        self,
        wall: List[List[int]],
        width: int,
        height: int,
        path: Optional[List[Tuple[int, int]]] = None,
    ) -> None:
        if path is None:
            path = []

        theme = self.theme_mgr.current
        s = self.style

        print(f"\n--- Aktif Tema: {theme.name} ---")

        for y in range(height + 1):
            top_line = ""
            for x in range(width + 1):
                top_line += self._render_junction(wall, x, y, theme)
                if x < width:
                    has_wall_h = self._has_wall(
                        wall, x, y, 1
                    ) or self._has_wall(wall, x, y - 1, 4)
                    if has_wall_h:
                        top_line += (
                            f"{theme.wall_bg}{theme.wall_fg}"
                            f"{s.wall_h}{theme.reset}"
                        )
                    else:
                        top_line += f"{theme.empty_bg}   {theme.reset}"
            print(top_line)

            if y < height:
                mid_line = ""
                for x in range(width + 1):
                    has_wall_v = self._has_wall(
                        wall, x, y, 8
                    ) or self._has_wall(wall, x - 1, y, 2)
                    if has_wall_v:
                        mid_line += (
                            f"{theme.wall_bg}{theme.wall_fg}"
                            f"{s.wall_v}{theme.reset}"
                        )
                    else:
                        mid_line += f"{theme.empty_bg} {theme.reset}"

                    if x < width:
                        bg, glyph = self._get_cell_visuals(
                            x, y, wall[y][x], path, theme
                        )
                        mid_line += f"{bg}{glyph}{theme.reset}"
                print(mid_line)

        print()
