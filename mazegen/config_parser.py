import os
from typing import Any, Dict, List, Tuple


class ConfigParser:

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.config: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Configuration "
                                    f"file not found: {self.filepath}")

        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if not line or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                self._process_kv(key.strip(), value.strip())

        self._validate()
        return self.config

    def _process_kv(self, key: str, value: str) -> None:
        if key in ('WIDTH', 'HEIGHT'):
            self.config[key] = int(value)
        elif key in ('ENTRY', 'EXIT'):
            parts = value.split(',')
            self.config[key] = (int(parts[0]), int(parts[1]))
        elif key == 'PERFECT':
            self.config[key] = value.lower() in ('true', '1', 'yes')
        elif key == 'SEED':
            if not value or value.lower() == 'none':
                self.config[key] = None
            else:
                self.config[key] = int(value)
        else:
            self.config[key] = value

    def _validate(self) -> None:
        mandatory_keys = ['WIDTH',
                          'HEIGHT',
                          'ENTRY',
                          'EXIT',
                          'OUTPUT_FILE',
                          'PERFECT']
        for k in mandatory_keys:
            if k not in self.config:
                raise ValueError(f"Missing "
                                 f"mandatory configuration key: {k}")
        self.config.setdefault('SEED', None)

    @staticmethod
    def write_maze_output(
        filepath: str,
        walls: List[List[int]],
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        path: str = "",
    ) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            for row in walls:
                f.write("".join(format(c & 0xF, "x") for c in row) + "\n")

            f.write("\n")
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit_pos[0]},{exit_pos[1]}\n")
            f.write(f"{path}\n")
