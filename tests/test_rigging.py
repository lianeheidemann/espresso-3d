from espresso3d.pipeline import rigging

BONES = rigging.HUMANOID_BONES


def test_accepts_valid_rotation():
    clean = rigging.validate_rotations({"head": [0, 25, 0]}, BONES)
    assert clean == {"head": [0.0, 25.0, 0.0]}


def test_discards_bone_that_does_not_exist_in_the_rig():
    clean = rigging.validate_rotations(
        {"left_wing": [0, 0, 0], "head": [1, 2, 3]}, BONES
    )
    assert list(clean) == ["head"]


def test_clamps_absurd_angle():
    clean = rigging.validate_rotations({"right_upper_arm": [900, -900, 0]}, BONES)
    assert clean["right_upper_arm"] == [180.0, -180.0, 0.0]


def test_discards_wrong_format():
    raw = {
        "head": [1, 2],            # missing one axis
        "neck": "very twisted",    # not even a list
        "spine": [1, 2, "x"],      # non-numeric value
        "hips": [0, 10, 0],        # this is the only good one
    }
    assert list(rigging.validate_rotations(raw, BONES)) == ["hips"]


def test_normalizes_the_bone_name():
    clean = rigging.validate_rotations({"Right Upper Arm": [0, 0, 10]}, BONES)
    assert "right_upper_arm" in clean


def test_empty_input():
    assert rigging.validate_rotations({}, BONES) == {}
    assert rigging.validate_rotations(None, BONES) == {}


def test_extracts_plain_json():
    assert rigging.extract_json('{"head": [0, 0, 0]}') == {"head": [0, 0, 0]}


def test_extracts_json_from_code_block():
    text = '```json\n{"neck": [1, 2, 3]}\n```'
    assert rigging.extract_json(text) == {"neck": [1, 2, 3]}


def test_extracts_json_with_chatter_around_it():
    text = 'Sure! Here you go: {"hips": [0, 0, 5]} — hope that helps!'
    assert rigging.extract_json(text) == {"hips": [0, 0, 5]}


def test_extracts_json_from_text_with_no_json():
    assert rigging.extract_json("couldn't do that") == {}
    assert rigging.extract_json("") == {}


def test_pose_from_text_end_to_end():
    class Brain:
        def complete(self, prompt):
            assert "right_upper_arm" in prompt  # received the real bone list
            return '{"right_upper_arm": [0, 0, -75], "wing": [1, 1, 1]}'

    pose = rigging.pose_from_text("right arm raised", BONES, Brain())
    assert pose == {"right_upper_arm": [0.0, 0.0, -75.0]}


def test_pose_from_empty_text_does_not_call_the_llm():
    class NeverCalled:
        def complete(self, prompt):
            raise AssertionError("shouldn't call the LLM with an empty description")

    assert rigging.pose_from_text("   ", BONES, NeverCalled()) == {}
