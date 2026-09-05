from espresso3d.agent import parser
from espresso3d.config import License, PipelineConfig, Pose, TextureResolution


class FakeBrain:
    """Returns a fixed response, to test with no LLM at all."""

    def __init__(self, response):
        self.response = response

    def complete(self, prompt):
        return self.response


def test_keywords_detects_split():
    cfg = parser.by_keywords("generate the cup separated from the saucer")
    assert cfg.split_parts is True


def test_keywords_high_quality():
    cfg = parser.by_keywords("I want it in high quality")
    assert cfg.engine == "instant_mesh"
    assert cfg.texture_resolution is TextureResolution.ULTRA_2K


def test_keywords_fast():
    cfg = parser.by_keywords("make it fast, it's just a draft")
    assert cfg.engine == "tripo_sr"


def test_keywords_format():
    cfg = parser.by_keywords("export as .fbx and .usdz")
    assert sorted(cfg.formats) == ["fbx", "usdz"]


def test_keywords_no_texture():
    cfg = parser.by_keywords("just the mesh, no texture")
    assert cfg.generate_texture is False


def test_keywords_pose():
    assert parser.by_keywords("in t-pose").pose is Pose.T_POSE
    assert parser.by_keywords("in a-pose").pose is Pose.A_POSE


def test_keywords_commercial_license():
    assert parser.by_keywords("commercial use").license is License.COMMERCIAL


def test_keywords_polygon_count():
    cfg = parser.by_keywords("with 8,000 polygons")
    assert cfg.poly_count_target == 8000


def test_keywords_preserves_the_rest():
    base = PipelineConfig(enhance_image=False, formats=["glb"])
    cfg = parser.by_keywords("separated", base)
    assert cfg.enhance_image is False
    assert cfg.formats == ["glb"]


def test_apply_ignores_nonexistent_engine():
    cfg = parser.apply({"engine": "engine_that_does_not_exist"}, PipelineConfig())
    assert cfg.engine == "stable_fast_3d"


def test_apply_clamps_poly_count():
    assert parser.apply({"poly_count_target": 99_999}, PipelineConfig()).poly_count_target == 20_000
    assert parser.apply({"poly_count_target": 1}, PipelineConfig()).poly_count_target == 500


def test_apply_ignores_invalid_enum():
    cfg = parser.apply({"pose": "flying"}, PipelineConfig())
    assert cfg.pose is Pose.NONE


def test_pose_prompt_enables_custom_pose():
    cfg = parser.apply({"pose_prompt": "sitting on the floor"}, PipelineConfig())
    assert cfg.pose is Pose.CUSTOM


def test_llm_with_valid_json():
    brain = FakeBrain('{"engine": "tripo_sr", "split_parts": true}')
    cfg = parser.do_llm("whatever", brain)
    assert cfg.engine == "tripo_sr"
    assert cfg.split_parts is True


def test_llm_with_json_wrapped_in_chatter():
    brain = FakeBrain(
        'Sure! Here it is:\n```json\n{"poly_count_target": 9000}\n```\nHope that helped.'
    )
    cfg = parser.do_llm("...", brain)
    assert cfg.poly_count_target == 9000


def test_llm_without_json_falls_back_to_basic_mode():
    brain = FakeBrain("sorry, I didn't understand")
    cfg = parser.do_llm("I want it separated from the saucer", brain)
    assert cfg.split_parts is True


def test_llm_that_blows_up_falls_back_to_basic_mode():
    class Broken:
        def complete(self, prompt):
            raise RuntimeError("ollama offline")

    cfg = parser.do_llm("in high quality", Broken())
    assert cfg.engine == "instant_mesh"


def test_summary_has_the_cards_keys():
    summary = parser.summary(PipelineConfig())
    assert "Engine" in summary
    assert "Formats" in summary
    assert summary["Formats"] == ".glb"
