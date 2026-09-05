#!/usr/bin/env python3
"""Espresso3D — abre a interface local no navegador.

    python -m espresso3d                 # http://localhost:7860
    python -m espresso3d --porta 8000
"""

from __future__ import annotations

import argparse
import logging

from .ui import rodar


def main() -> None:
    parser = argparse.ArgumentParser(description="Espresso3D — imagem para 3D, local.")
    parser.add_argument("--porta", type=int, default=7860, help="porta HTTP")
    parser.add_argument(
        "--compartilhar",
        action="store_true",
        help="cria um link público temporário do Gradio",
    )
    parser.add_argument("--debug", action="store_true", help="log detalhado")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    rodar(porta=args.porta, compartilhar=args.compartilhar)


if __name__ == "__main__":
    main()
