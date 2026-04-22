"""
api.py
Ponte entre o JavaScript da interface e o backend Python.
Todos os métodos públicos desta classe ficam disponíveis em:
  window.pywebview.api.<método>()
"""

import json
from config_manager import ConfigManager
from actions import ActionExecutor


class Api:
    def __init__(self, config: ConfigManager):
        self._config = config
        self._executor = ActionExecutor()
        self._window = None
        self._deck_enabled = True

    def set_window(self, window):
        """Registra a janela pywebview para poder chamar JS."""
        self._window = window

    # ──────────────────────────────────────────────
    # Configuração
    # ──────────────────────────────────────────────

    def get_config(self) -> str:
        """Retorna toda a configuração como JSON string."""
        return json.dumps(self._config.load())

    def save_key(self, key_id: str, action_data: dict) -> dict:
        """
        Salva a configuração de uma tecla no perfil ativo.
        Chamado pelo JS quando o usuário clica em Salvar.
        """
        self._config.save_key(key_id, action_data)
        return {"success": True, "key_id": key_id}

    def get_profiles(self) -> str:
        return json.dumps(self._config.get_profiles())

    def get_active_profile(self) -> str:
        return self._config.get_active_profile()

    def switch_profile(self, profile_name: str) -> str:
        """Muda para o perfil especificado e retorna nova config."""
        self._config.set_active_profile(profile_name)
        return json.dumps(self._config.load())

    def switch_to_next_profile(self) -> str:
        """Alterna para o próximo perfil da lista."""
        next_profile = self._config.get_next_profile()
        self._config.set_active_profile(next_profile)
        return json.dumps(self._config.load())

    def create_profile(self, name: str) -> str:
        """Cria um novo perfil vazio."""
        self._config.create_profile(name)
        return json.dumps(self._config.get_profiles())

    # ──────────────────────────────────────────────
    # Controle do deck
    # ──────────────────────────────────────────────

    def toggle_deck(self) -> bool:
        """Liga ou desliga o deck. Retorna o novo estado."""
        self._deck_enabled = not self._deck_enabled
        return self._deck_enabled

    def is_deck_enabled(self) -> bool:
        return self._deck_enabled

    # ──────────────────────────────────────────────
    # Execução de teclas
    # ──────────────────────────────────────────────

    def handle_key_press(self, key_id: str):
        """
        Chamado pelo listener (via evaluate_js) quando uma tecla física
        é pressionada. Executa a ação configurada.
        """
        if not self._deck_enabled and key_id != "KP_NUMLOCK":
            return

        # NumLock → liga/desliga o deck
        if key_id == "KP_NUMLOCK":
            self._deck_enabled = not self._deck_enabled
            self._notify_js("onDeckToggle", self._deck_enabled)
            return

        # KP_DIVIDE → alterna perfil
        config = self._config.load()
        profile = self._config.get_active_profile()
        key_config = config.get("profiles", {}).get(profile, {}).get(key_id)

        if not key_config:
            return

        if key_config.get("type") == "profile_switch":
            new_config = self.switch_to_next_profile()
            self._notify_js("onProfileSwitch", json.loads(new_config))
            return

        # Executa a ação em background para não travar a UI
        import threading
        threading.Thread(
            target=self._executor.execute,
            args=(key_config,),
            daemon=True
        ).start()

    def test_key(self, key_id: str) -> dict:
        """
        Permite testar uma tecla pela interface (sem precisar pressionar fisicamente).
        """
        self.handle_key_press(key_id)
        return {"success": True}

    # ──────────────────────────────────────────────
    # Janela
    # ──────────────────────────────────────────────

    def minimize_to_tray(self):
        """Esconde a janela para a bandeja do sistema."""
        if self._window:
            self._window.hide()

    # ──────────────────────────────────────────────
    # Interno
    # ──────────────────────────────────────────────

    def _notify_js(self, fn_name: str, data):
        """Chama uma função JavaScript na interface."""
        if self._window:
            payload = json.dumps(data)
            self._window.evaluate_js(f"{fn_name}({payload})")

    def notify_key_pressed(self, key_id: str):
        """Avisa o JS que uma tecla foi pressionada (para animação)."""
        self._notify_js("onKeyPressed", key_id)
