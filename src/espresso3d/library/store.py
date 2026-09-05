"""Library of generated models.

The filesystem is the source of truth: the list comes from scanning
``outputs/*/meta.json``. There's no database to get out of sync — the
user can move, copy or delete folders from outside and nothing breaks.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

ROOT = Path("outputs")
META = "meta.json"


@dataclass
class Item:
    """A generated model, built from the folder's meta.json."""

    folder: Path
    name: str
    created_at: str
    engine: str
    faces: int
    formats: list[str]
    parts: int
    bytes: int
    warnings: list[str]

    @property
    def mb(self) -> float:
        return round(self.bytes / (1024 * 1024), 1)

    @property
    def preview(self) -> Path | None:
        for candidate in sorted(self.folder.glob("*.glb")):
            return candidate
        return None

    @property
    def source_image(self) -> Path | None:
        source = self.folder / "source.png"
        return source if source.exists() else None


def register(result, cfg, name: str) -> Path:
    """Writes the ``meta.json`` that makes the folder show up in the library."""
    meta = {
        "name": name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "engine": cfg.engine,
        "faces": result.stats.get("faces", 0),
        "formats": sorted({a.suffix.lstrip(".") for a in result.files}),
        "parts": result.parts,
        "duration_s": result.duration_s,
        "warnings": result.warnings,
        "config": cfg.to_dict(),
    }
    path = Path(result.folder) / META
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def list_items(root: Path = ROOT) -> list[Item]:
    """All models, from newest to oldest."""
    root = Path(root)
    if not root.exists():
        return []

    items: list[Item] = []
    for folder in sorted(root.iterdir(), reverse=True):
        if not folder.is_dir():
            continue
        item = _read(folder)
        if item is not None:
            items.append(item)
    return items


def _read(folder: Path) -> Item | None:
    path = folder / META
    if not path.exists():
        return None
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Unreadable meta.json in %s: %s", folder, exc)
        return None

    return Item(
        folder=folder,
        name=meta.get("name", folder.name),
        created_at=meta.get("created_at", ""),
        engine=meta.get("engine", "?"),
        faces=int(meta.get("faces", 0) or 0),
        formats=list(meta.get("formats", [])),
        parts=int(meta.get("parts", 1) or 1),
        bytes=folder_size(folder),
        warnings=list(meta.get("warnings", [])),
    )


def folder_size(folder: Path) -> int:
    """Bytes occupied by a model folder."""
    return sum(f.stat().st_size for f in Path(folder).rglob("*") if f.is_file())


def total_space(root: Path = ROOT) -> tuple[int, int]:
    """(number of models, bytes on disk)."""
    items = list_items(root)
    return len(items), sum(i.bytes for i in items)


def delete(folder: Path, to_trash: bool = True) -> bool:
    """Removes a model folder.

    Sends it to the system trash by default, which is recoverable.
    Permanently deleting a user's file is something done only when the
    person explicitly asks for it.
    """
    folder = Path(folder)
    if not folder.exists():
        return False

    if to_trash:
        try:
            from send2trash import send2trash

            send2trash(str(folder))
            return True
        except ImportError:
            log.warning(
                "send2trash not installed — deleting permanently. "
                "Install with: pip install send2trash"
            )
        except Exception as exc:
            log.warning("Trash unavailable (%s) — deleting permanently.", exc)

    shutil.rmtree(folder)
    return True


def delete_many(folders: list[Path], to_trash: bool = True) -> int:
    return sum(1 for p in folders if delete(p, to_trash))
