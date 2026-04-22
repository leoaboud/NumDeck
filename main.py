"""
main.py
Ponto de entrada do NumDeck.

Uso:
  python main.py

Para gerar .exe:
  pip install pyinstaller
  pyinstaller --onefile --windowed --icon=icon.ico main.py
"""

import os
import sys
import threading
import webview

from api import Api
from config_manager import ConfigManager
from listener import NumpadListener
from tray import start_tray


def main():
    # ── Config e API ──────────────────────────────
    config = ConfigManager()
    api = Api(config)

    # ── Janela pywebview ──────────────────────────
    interface_path = os.path.join(
        os.path.dirname(__file__), "interface", "index.html"
    )

    window = webview.create_window(
        title="NumDeck",
        url=interface_path,
        js_api=api,
        width=1100,
        height=700,
        min_size=(900, 600),
        resizable=True,
        frameless=False,
        on_top=False,
        background_color="#0a0a0f",
    )

    api.set_window(window)

    # ── Listener do numpad ────────────────────────
    def on_key_press(key_id: str):
        """Chamado pelo listener quando tecla física é pressionada."""
        # Anima a tecla na interface
        api.notify_key_pressed(key_id)
        # Executa a ação
        api.handle_key_press(key_id)

    listener = NumpadListener(on_key_press=on_key_press)

    listener_thread = threading.Thread(target=listener.start, daemon=True)
    listener_thread.start()

    # ── Bandeja do sistema ────────────────────────
    tray_thread = threading.Thread(
        target=start_tray,
        args=(window,),
        daemon=True
    )
    tray_thread.start()

    # ── Inicia o app ──────────────────────────────
    webview.start(debug=False)


if __name__ == "__main__":
    main()
