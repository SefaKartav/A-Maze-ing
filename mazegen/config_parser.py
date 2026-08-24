import os
from typing import Dict, Any, List


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

