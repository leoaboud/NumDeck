"""
actions.py
Executa as ações configuradas para cada tecla.
"""

import subprocess
import os
import webbrowser
import keyboard
import pyautogui
import time
import ctypes


class ActionExecutor:

    def execute(self, action: dict):
        """Despacha para o método correto baseado no tipo."""
        action_type = action.get("type", "none")
        value = action.get("value", "")

        dispatch = {
            "open_app":      lambda: self._open_app(value),
            "open_url":      lambda: self._open_url(value),
            "shortcut":      lambda: self._shortcut(value),
            "text":          lambda: self._type_text(value),
            "script":        lambda: self._run_script(value),
            "terminal_admin":lambda: self._open_terminal_admin(),
            "screenshot":    lambda: self._screenshot_and_copy(),
            "none":          lambda: None,
        }

        fn = dispatch.get(action_type)
        if fn:
            try:
                fn()
            except Exception as e:
                print(f"[Erro ao executar ação '{action_type}']: {e}")

    # ──────────────────────────────────────────────
    # Abrir aplicativo
    # ──────────────────────────────────────────────
    def _open_app(self, path: str):
        """Abre um executável. Suporta variáveis de ambiente no caminho."""
        expanded = os.path.expandvars(path)

        # Comando simples como 'code', 'notepad', etc.
        if not os.path.sep in expanded and not os.path.exists(expanded):
            subprocess.Popen(expanded, shell=True)
            return

        if os.path.exists(expanded):
            subprocess.Popen([expanded])
        else:
            # Tenta mesmo assim (pode estar no PATH)
            subprocess.Popen(expanded, shell=True)

    # ──────────────────────────────────────────────
    # Abrir URL
    # ──────────────────────────────────────────────
    def _open_url(self, url: str):
        webbrowser.open(url)

    # ──────────────────────────────────────────────
    # Atalho de teclado
    # ──────────────────────────────────────────────
    def _shortcut(self, keys: str):
        """
        Envia atalho de teclado.
        Exemplos: 'ctrl+c', 'ctrl+shift+esc', 'f5', 'alt+tab'
        """
        # Alt+Tab precisa de tratamento especial para funcionar corretamente
        if keys.lower() == "alt+tab":
            self._alt_tab()
            return

        keyboard.press_and_release(keys)

    def _alt_tab(self):
        """Alt+Tab funcional — segura Alt, pressiona Tab, solta Alt."""
        keyboard.press("alt")
        time.sleep(0.05)
        keyboard.press_and_release("tab")
        time.sleep(0.1)
        keyboard.release("alt")

    # ──────────────────────────────────────────────
    # Digitar texto
    # ──────────────────────────────────────────────
    def _type_text(self, text: str):
        """Digita um texto no campo ativo."""
        time.sleep(0.1)
        pyautogui.write(text, interval=0.03)

    # ──────────────────────────────────────────────
    # Executar script
    # ──────────────────────────────────────────────
    def _run_script(self, script_path: str):
        """Executa um script .bat, .py, .ps1, etc."""
        expanded = os.path.expandvars(script_path)
        subprocess.Popen(expanded, shell=True)

    # ──────────────────────────────────────────────
    # Terminal como Administrador
    # ──────────────────────────────────────────────
    def _open_terminal_admin(self):
        """Abre Windows Terminal como administrador."""
        # Tenta Windows Terminal primeiro, depois PowerShell
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "wt.exe", None, None, 1
            )
        except Exception:
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", "powershell.exe", None, None, 1
                )
            except Exception as e:
                print(f"[Terminal Admin] Erro: {e}")

    # ──────────────────────────────────────────────
    # Print Screen recortado + Ctrl+C
    # ──────────────────────────────────────────────
    def _screenshot_and_copy(self):
        """
        Ativa a ferramenta de recorte do Windows (Win+Shift+S).
        O Windows automaticamente copia a seleção para a área de transferência.
        """
        keyboard.press_and_release("windows+shift+s")
