"""
config_manager.py
Gerencia leitura e escrita das configurações em JSON.
"""

import json
import os
import copy

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "profiles.json")

DEFAULT_KEY = {
    "name": "Sem ação",
    "type": "none",
    "value": "",
    "icon": "·",
    "color": "gray"
}


class ConfigManager:
    def __init__(self):
        self._data = None
        self._ensure_config()

    def _ensure_config(self):
        """Garante que o arquivo de config existe."""
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            self._data = {
                "active_profile": "Dev Mode",
                "profiles": {"Dev Mode": {}}
            }
            self._write()
        else:
            self._data = self._read()

    def _read(self) -> dict:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def load(self) -> dict:
        """Retorna config completa."""
        self._data = self._read()
        return self._data

    def get_active_profile(self) -> str:
        return self._data.get("active_profile", "Dev Mode")

    def get_profiles(self) -> list:
        return list(self._data.get("profiles", {}).keys())

    def get_key_config(self, key_id: str) -> dict:
        """Retorna config de uma tecla no perfil ativo."""
        profile = self.get_active_profile()
        return self._data["profiles"][profile].get(key_id, copy.deepcopy(DEFAULT_KEY))

    def save_key(self, key_id: str, action_data: dict):
        """Salva configuração de uma tecla."""
        self._data = self._read()
        profile = self.get_active_profile()
        if profile not in self._data["profiles"]:
            self._data["profiles"][profile] = {}
        self._data["profiles"][profile][key_id] = action_data
        self._write()

    def set_active_profile(self, profile_name: str):
        """Muda o perfil ativo."""
        self._data = self._read()
        if profile_name in self._data["profiles"]:
            self._data["active_profile"] = profile_name
            self._write()

    def create_profile(self, name: str):
        """Cria novo perfil vazio."""
        self._data = self._read()
        if name not in self._data["profiles"]:
            self._data["profiles"][name] = {}
            self._write()

    def get_next_profile(self) -> str:
        """Retorna o próximo perfil na lista (para alternar)."""
        profiles = self.get_profiles()
        current = self.get_active_profile()
        if current in profiles:
            idx = profiles.index(current)
            return profiles[(idx + 1) % len(profiles)]
        return profiles[0] if profiles else current
