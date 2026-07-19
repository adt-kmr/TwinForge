import json

import pytest
import yaml

from policy.rl.config import ACTIVITY_TEMPLATES, build_trainer_config

NAVMESH = {"origin": [0, 0], "cell": 0.1, "width": 40, "height": 40,
           "grid": [[0] * 40 for _ in range(40)]}


@pytest.fixture
def twin(tmp_path):
    navmesh_path = tmp_path / "navmesh.json"
    navmesh_path.write_text(json.dumps(NAVMESH))
    return {"navmesh_url": str(navmesh_path)}


@pytest.mark.parametrize("activity", list(ACTIVITY_TEMPLATES))
def test_build_trainer_config_is_valid_ppo_yaml(activity, twin, tmp_path):
    out_path = build_trainer_config(activity, twin, str(tmp_path / f"{activity}.yaml"))
    assert out_path == str(tmp_path / f"{activity}.yaml")

    config = yaml.safe_load(open(out_path))
    behavior_name = ACTIVITY_TEMPLATES[activity]["behavior_name"]
    behavior = config["behaviors"][behavior_name]

    assert behavior["trainer_type"] == "ppo"
    assert behavior["hyperparameters"]["batch_size"] > 0
    assert behavior["reward_signals"]["extrinsic"]["gamma"] == pytest.approx(0.99)
    assert behavior["max_steps"] > 0

    assert config["observation_space"]["size"] == 4
    assert config["environment"]["navmesh"]["width"] == NAVMESH["width"]
    assert config["environment"]["navmesh"]["height"] == NAVMESH["height"]

    reward_shaping = config["reward_shaping"]
    assert reward_shaping["success_bonus"] > 0
    assert "behavior_name" not in reward_shaping  # internal template key, not a reward term


def test_walk_to_point_has_distance_and_time_shaping(twin, tmp_path):
    out_path = build_trainer_config("walk_to_point", twin, str(tmp_path / "w.yaml"))
    reward_shaping = yaml.safe_load(open(out_path))["reward_shaping"]
    assert reward_shaping["distance_weight"] < 0
    assert reward_shaping["time_penalty"] < 0


def test_pick_object_has_grasp_and_lift_shaping(twin, tmp_path):
    out_path = build_trainer_config("pick_object", twin, str(tmp_path / "p.yaml"))
    reward_shaping = yaml.safe_load(open(out_path))["reward_shaping"]
    assert reward_shaping["grasp_bonus"] > 0
    assert reward_shaping["lift_bonus"] > 0


def test_follow_path_has_centerline_and_progress_shaping(twin, tmp_path):
    out_path = build_trainer_config("follow_path", twin, str(tmp_path / "f.yaml"))
    reward_shaping = yaml.safe_load(open(out_path))["reward_shaping"]
    assert reward_shaping["centerline_weight"] < 0
    assert reward_shaping["progress_bonus"] > 0


def test_invalid_activity_raises_key_error(twin, tmp_path):
    with pytest.raises(KeyError):
        build_trainer_config("juggle", twin, str(tmp_path / "x.yaml"))
