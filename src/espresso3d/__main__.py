#!/usr/bin/env python3
"""Espresso3D — opens the local UI in the browser.

    python -m espresso3d                 # http://localhost:7860
    python -m espresso3d --port 8000
"""

from __future__ import annotations

import argparse
import logging

from .ui import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Espresso3D — image to 3D, local.")
    parser.add_argument("--port", type=int, default=7860, help="HTTP port")
    parser.add_argument(
        "--share",
        action="store_true",
        help="creates a temporary public Gradio link",
    )
    parser.add_argument("--debug", action="store_true", help="verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    run(port=args.port, share=args.share)


if __name__ == "__main__":
    main()
