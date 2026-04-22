"""
listener.py
Captura teclas SOMENTE do teclado numérico USB externo.

Estratégia:
  1. Usa pywinusb para detectar e escutar o dispositivo HID (numpad USB).
  2. Mapeia os scan codes do numpad para IDs legíveis.
  3. Fallback: se pywinusb não encontrar o dispositivo, usa a biblioteca
     'keyboard' filtrando pelos scan codes exclusivos do numpad.
"""

import threading
import time
from typing import Callable, Optional

# Scan codes exclusivos das teclas do numpad físico
# (diferentes dos números na linha superior do teclado)
NUMPAD_SCAN_CODES = {
    69:  "KP_NUMLOCK",
    53:  "KP_DIVIDE",      # / (extended)
    55:  "KP_MULTIPLY",    # *
    74:  "KP_MINUS",       # -
    71:  "KP_7",
    72:  "KP_8",
    73:  "KP_9",
    78:  "KP_PLUS",        # +
    75:  "KP_4",
    76:  "KP_5",
    77:  "KP_6",
    14:  "KP_BACKSPACE",   # Backspace (scan 14)
    79:  "KP_1",
    80:  "KP_2",
    81:  "KP_3",
    28:  "KP_ENTER",       # Enter (extended)
    82:  "KP_0",
    83:  "KP_DOT",         # .
}


class NumpadListener:
    """
    Escuta o numpad USB e chama on_key_press(key_id) quando uma tecla
    é pressionada. Ignora o teclado do notebook.
    """

    def __init__(self, on_key_press: Callable[[str], None]):
        self.on_key_press = on_key_press
        self._enabled = True
        self._device_name: Optional[str] = None
        self._lock = threading.Lock()

    def set_enabled(self, value: bool):
        with self._lock:
            self._enabled = value

    def start(self):
        """Inicia a escuta. Tenta pywinusb primeiro, depois fallback."""
        if self._try_pywinusb():
            print("[Listener] Usando pywinusb (device-specific).")
        else:
            print("[Listener] pywinusb não encontrou o dispositivo. Usando fallback por scan code.")
            self._start_keyboard_fallback()

    # ──────────────────────────────────────────────
    # Método 1: pywinusb — isola o dispositivo USB
    # ──────────────────────────────────────────────
    def _try_pywinusb(self) -> bool:
        try:
            import pywinusb.hid as hid

            # Busca todos os dispositivos HID de teclado
            all_devices = hid.find_all_hid_devices()
            numpad = self._find_numpad_device(all_devices)

            if numpad is None:
                return False

            self._device_name = numpad.product_name
            print(f"[Listener] Dispositivo encontrado: {self._device_name}")

            numpad.open()
            numpad.set_raw_data_handler(self._hid_raw_handler)

            # Mantém a thread viva enquanto o dispositivo estiver conectado
            try:
                while numpad.is_plugged():
                    time.sleep(0.1)
            finally:
                numpad.close()

            return True

        except Exception as e:
            print(f"[Listener] pywinusb erro: {e}")
            return False

    def _find_numpad_device(self, devices):
        """
        Tenta identificar o numpad USB entre os dispositivos HID.
        Prioriza dispositivos com 'numpad' ou 'numeric' no nome.
        """
        import pywinusb.hid as hid

        keywords = ["numpad", "numeric", "num pad", "exbom", "teclado num"]

        # Busca por nome
        for dev in devices:
            name = (dev.product_name or "").lower()
            if any(k in name for k in keywords):
                return dev

        # Busca genérica: pega teclados HID que NÃO são o teclado principal
        # (teclados secundários costumam ter usage_page=1, usage=6)
        keyboards = [
            d for d in devices
            if d.usage_page == 1 and d.usage == 6
        ]

        # Se houver mais de um teclado, retorna o que não é o embutido
        # (heurística: o embutido geralmente tem vendor_id da fabricante do notebook)
        if len(keyboards) > 1:
            return keyboards[-1]  # geralmente o USB externo aparece por último

        return None

    def _hid_raw_handler(self, data: list):
        """Callback chamado pelo pywinusb com dados HID brutos."""
        if not self._enabled:
            return

        # Relatório HID de teclado: [modifier, 0x00, key1, key2, ...]
        # Mapeamos keycodes HID para key_id
        HID_TO_KEY = {
            0x53: "KP_NUMLOCK",
            0x54: "KP_DIVIDE",
            0x55: "KP_MULTIPLY",
            0x56: "KP_MINUS",
            0x57: "KP_PLUS",
            0x58: "KP_ENTER",
            0x59: "KP_1",
            0x5A: "KP_2",
            0x5B: "KP_3",
            0x5C: "KP_4",
            0x5D: "KP_5",
            0x5E: "KP_6",
            0x5F: "KP_7",
            0x60: "KP_8",
            0x61: "KP_9",
            0x62: "KP_0",
            0x63: "KP_DOT",
            0x2A: "KP_BACKSPACE",
        }

        # Verifica keys nos bytes 2 a 7 do relatório
        if len(data) >= 3:
            for byte in data[2:8]:
                if byte in HID_TO_KEY:
                    key_id = HID_TO_KEY[byte]
                    self.on_key_press(key_id)

    # ──────────────────────────────────────────────
    # Método 2: Fallback via scan codes (biblioteca keyboard)
    # ──────────────────────────────────────────────
    def _start_keyboard_fallback(self):
        import keyboard as kb

        def on_event(event):
            if not self._enabled:
                return
            if event.event_type != "down":
                return

            scan = event.scan_code
            key_id = NUMPAD_SCAN_CODES.get(scan)

            if key_id:
                self.on_key_press(key_id)

        kb.hook(on_event)

        # Mantém thread viva
        while True:
            time.sleep(1)

    def get_device_name(self) -> str:
        return self._device_name or "Numpad USB (scan codes)"
