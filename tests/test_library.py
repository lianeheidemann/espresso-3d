import json
from pathlib import Path

from espresso3d.config import PipelineConfig
from espresso3d.library import store
from espresso3d.pipeline import Result


def create_model(root: Path, name: str, faces: int = 4000) -> Path:
    folder = root / f"2026-09-05_120000_{name}"
    folder.mkdir(parents=True)
    (folder / f"{name}.glb").write_bytes(b"x" * 2048)
    (folder / "source.png").write_bytes(b"y" * 512)

    result = Result(
        folder=folder,
        files=[folder / f"{name}.glb"],
        parts=1,
        stats={"faces": faces},
        duration_s=12.3,
    )
    store.register(result, PipelineConfig(), name)
    return folder


def test_register_writes_meta(tmp_path):
    folder = create_model(tmp_path, "cup")
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))

    assert meta["name"] == "cup"
    assert meta["faces"] == 4000
    assert meta["formats"] == ["glb"]
    assert meta["config"]["engine"] == "stable_fast_3d"


def test_list_items_reads_what_was_registered(tmp_path):
    create_model(tmp_path, "cup")
    create_model(tmp_path, "vase", faces=8000)

    items = store.list_items(tmp_path)
    assert {i.name for i in items} == {"cup", "vase"}
    assert all(i.bytes > 0 for i in items)
    assert all(i.preview is not None for i in items)


def test_list_items_ignores_folder_without_meta(tmp_path):
    create_model(tmp_path, "good")
    (tmp_path / "loose_folder").mkdir()

    assert len(store.list_items(tmp_path)) == 1


def test_list_items_ignores_corrupted_meta(tmp_path):
    folder = create_model(tmp_path, "broken")
    (folder / "meta.json").write_text("{ this isn't json", encoding="utf-8")

    assert store.list_items(tmp_path) == []


def test_list_items_nonexistent_root(tmp_path):
    assert store.list_items(tmp_path / "does_not_exist") == []


def test_total_space(tmp_path):
    create_model(tmp_path, "a")
    create_model(tmp_path, "b")

    count, total_bytes = store.total_space(tmp_path)
    assert count == 2
    assert total_bytes > 4000


def test_permanent_delete_removes_the_folder(tmp_path):
    folder = create_model(tmp_path, "disposable")

    assert store.delete(folder, to_trash=False) is True
    assert not folder.exists()


def test_delete_nonexistent_folder(tmp_path):
    assert store.delete(tmp_path / "ghost") is False


def test_delete_many(tmp_path):
    folders = [create_model(tmp_path, n) for n in ("a", "b", "c")]

    assert store.delete_many(folders[:2], to_trash=False) == 2
    assert len(store.list_items(tmp_path)) == 1


def test_delete_falls_back_to_permanent_without_send2trash(tmp_path, monkeypatch):
    """Without the trash available, delete anyway instead of failing."""
    folder = create_model(tmp_path, "no_trash")

    import builtins

    original = builtins.__import__

    def without_send2trash(name, *args, **kwargs):
        if name == "send2trash":
            raise ImportError("simulating absence")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_send2trash)
    assert store.delete(folder, to_trash=True) is True
    assert not folder.exists()
