import pytest

from espresso3d.config import (
    License,
    PipelineConfig,
    Pose,
    TextureResolution,
    Topology,
    formats_by_group,
)


def test_default_is_valid():
    PipelineConfig().validate()


def test_requires_at_least_one_format():
    with pytest.raises(ValueError, match="at least one export format"):
        PipelineConfig(formats=[]).validate()


def test_rejects_unknown_format():
    with pytest.raises(ValueError, match="Unknown"):
        PipelineConfig(formats=["glb", "xyz"]).validate()


def test_poly_count_out_of_range():
    with pytest.raises(ValueError, match="Polygon count"):
        PipelineConfig(poly_count_target=99).validate()
    with pytest.raises(ValueError, match="Polygon count"):
        PipelineConfig(poly_count_target=999_999).validate()


def test_custom_pose_requires_description_or_photo():
    with pytest.raises(ValueError, match="text description"):
        PipelineConfig(pose=Pose.CUSTOM).validate()

    PipelineConfig(pose=Pose.CUSTOM, pose_prompt="arms open").validate()
    PipelineConfig(pose=Pose.CUSTOM, pose_ref_image="/tmp/photo.png").validate()


def test_stl_texture_warning():
    warnings = PipelineConfig(formats=["stl"], generate_texture=True).warnings()
    assert any("stl" in a and "texture" in a for a in warnings)


def test_no_texture_warning_when_texture_disabled():
    warnings = PipelineConfig(formats=["stl"], generate_texture=False).warnings()
    assert not any("doesn't store texture" in a for a in warnings)


def test_lost_rig_warning_only_with_pose():
    with_pose = PipelineConfig(
        formats=["obj"], pose=Pose.T_POSE
    ).warnings()
    assert any("skeleton" in a for a in with_pose)

    without_pose = PipelineConfig(formats=["obj"], pose=Pose.NONE).warnings()
    assert not any("skeleton" in a for a in without_pose)


def test_glb_generates_no_loss_warning():
    warnings = PipelineConfig(formats=["glb"], pose=Pose.T_POSE).warnings()
    assert warnings == []


def test_formats_that_need_blender():
    cfg = PipelineConfig(formats=["glb", "fbx", "usdz", "stl"])
    assert sorted(cfg.needs_blender) == ["fbx", "usdz"]


def test_roundtrip_dict():
    original = PipelineConfig(
        engine="tripo_sr",
        topology=Topology.SMART,
        pose=Pose.CUSTOM,
        pose_prompt="seated",
        license=License.COMMERCIAL,
        texture_resolution=TextureResolution.ULTRA_2K,
        formats=["glb", "fbx"],
    )
    restored = PipelineConfig.from_dict(original.to_dict())
    assert restored == original
    assert restored.texture_resolution.pixels == 2048


def test_from_dict_ignores_unknown_key():
    cfg = PipelineConfig.from_dict({"engine": "tripo_sr", "made_up_field": 42})
    assert cfg.engine == "tripo_sr"


def test_grouped_formats_cover_the_catalog():
    groups = formats_by_group()
    total = sum(len(v) for v in groups.values())
    assert total >= 13
    assert "Web and Android AR" in groups
