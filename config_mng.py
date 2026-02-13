import json
import os
from threading import Lock


class ConfigurationManager:
    def __init__(self, config_path, default_config: dict = None) -> None:
        self._config_path = config_path
        self._default_config = default_config or {}
        self._lock = Lock()

        # jeśli plik nie istnieje → utwórz z default
        if not os.path.exists(self._config_path):
            self._write_file(self._default_config)

    def get_config(self) -> dict:
        with self._lock:
            try:
                with open(self._config_path, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # jeśli plik uszkodzony → reset do default
                data = self._default_config
                self._write_file(data)

            # merge z default (jeśli dodasz nowe pola w przyszłości)
            merged = self._default_config.copy()
            merged.update(data)

            return merged

    def save_config(self, new_config: dict):
        with self._lock:
            try:
                with open(self._config_path, "r") as f:
                    current = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                current = self._default_config.copy()

            current.update(new_config)

            with open(self._config_path, "w") as f:
                json.dump(current, f, indent=4)

    def _write_file(self, config: dict):
        with open(self._config_path, "w") as f:
            json.dump(config, f, indent=4)
