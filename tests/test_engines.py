import pytest

from espresso3d import engines
from espresso3d.config import License


def test_registry_has_the_three_engines():
    assert set(engines.ENGINES) == {"tripo_sr", "stable_fast_3d", "instant_mesh"}


def test_get_nonexistent_engine_lists_the_valid_ones():
    with pytest.raises(KeyError, match="tripo_sr"):
        engines.get("ghost_engine")


def test_filter_by_vram():
    fit_in_4gb = engines.list_engines(vram_gb=4)
    assert [m.info.id for m in fit_in_4gb] == ["tripo_sr"]

    fit_in_8gb = engines.list_engines(vram_gb=8)
    assert len(fit_in_8gb) == 3


def test_filter_by_commercial_license():
    """Stability's license restricts commercial use — the filter respects that."""
    commercial = {m.info.id for m in engines.list_engines(license=License.COMMERCIAL)}
    assert "stable_fast_3d" not in commercial
    assert "tripo_sr" in commercial


def test_private_license_allows_everything():
    private = engines.list_engines(license=License.PRIVATE)
    assert len(private) == 3


def test_suggest_picks_the_best_that_fits():
    assert engines.suggest(vram_gb=8).info.id == "instant_mesh"
    assert engines.suggest(vram_gb=6).info.id == "stable_fast_3d"
    assert engines.suggest(vram_gb=4).info.id == "tripo_sr"


def test_suggest_without_gpu_returns_the_lightest():
    assert engines.suggest(vram_gb=0).info.id == "tripo_sr"


def test_suggest_respects_license():
    chosen = engines.suggest(vram_gb=6, license=License.COMMERCIAL)
    assert chosen.info.commercial_use is True


def test_engine_refuses_small_gpu_with_a_useful_message():
    engine = engines.get("instant_mesh")
    from espresso3d.engines import base

    original = base._vram
    base._vram = lambda: 4.0
    try:
        with pytest.raises(RuntimeError, match="8 GB of VRAM"):
            engine.generate(None, None)
    finally:
        base._vram = original


def test_complete_metadata():
    for engine in engines.ENGINES.values():
        info = engine.info
        assert info.name and info.description and info.repo
        assert info.vram_min_gb > 0
        assert info.weights_license
