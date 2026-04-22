"""
tray.py
Ícone na bandeja do sistema (systray) do Windows.
"""

import pystray
from PIL import Image, ImageDraw
import threading


def _create_icon_image():
    """Cria um ícone simples em memória."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo arredondado azul
    draw.rounded_rectangle([2, 2, size - 2, size - 2], radius=12, fill="#4f8fff")

    # Letras "ND"
    draw.rectangle([14, 20, 24, 44], fill="white")
    draw.rectangle([14, 20, 38, 28], fill="white")
    draw.rectangle([14, 30, 38, 36], fill="white")
    draw.rectangle([28, 20, 38, 44], fill="white")
    draw.rectangle([40, 20, 50, 44], fill="white")
    draw.polygon([(40, 20), (52, 32), (40, 44)], fill="white")

    return img


def start_tray(window):
    """Inicia o ícone na bandeja. Deve rodar em thread separada."""

    def on_show(icon, item):
        icon.visible = True
        window.show()

    def on_quit(icon, item):
        icon.stop()
        import sys
        sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Abrir NumDeck", on_show, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair", on_quit),
    )

    icon = pystray.Icon(
        name="NumDeck",
        icon=_create_icon_image(),
        title="NumDeck — Rodando",
        menu=menu
    )

    icon.run()
