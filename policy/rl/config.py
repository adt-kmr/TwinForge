"""ML-Agents PPO trainer config generation for the twin's navigation/manipulation activities.

Blueprint v3 §6.2 replaces behaviour-cloning-only training with genuine on-policy PPO run
inside the generated Unity twin (Phase C). This module is pure config generation: it writes
an ML-Agents-format YAML trainer config to disk. No `mlagents` import, no training, no
subprocess -- that's a later task (Task 11, which will shell out to `mlagents-learn` with
the file this module produces).

Design decisions (binding on later tasks unless revisited):

* ``twin`` parameter shape -- a *twin DB record*, not a raw navmesh dict. This matches the
  convention already established in ``orchestrator/service.py``'s ``_load_navmesh(twin)``:
  the ``twins`` table (``orchestrator/db.py``) stores ``navmesh_url``, a filesystem path to
  the ``navmesh.json`` written by ``twin.generator.generate_twin()`` (see
  ``twin/generator.py:_navmesh``), not the grid itself. Loading from ``navmesh_url`` here
  keeps this function callable the same way ``_load_navmesh`` already is -- pass it the twin
  row, not a pre-loaded blob.

* Observation-space size -- fixed at 4: ``[pos_x, pos_y, goal_x, goal_y]`` in navmesh world
  coordinates. The existing BC pipeline (``policy/evaluate.py``) already treats this as a
  low-dimensional 2D navigation problem (its linear policy is ``obs_dim=2``, a delta
  vector); doubling that to include absolute position and goal is the natural PPO
  equivalent and keeps observations independent of grid resolution. Using the navmesh's
  ``width``/``height`` cell counts directly as the observation size was considered and
  rejected: a 50x50 room would mean a 2500-float observation vector, which is a pixel-grid
  encoding decision no one has asked for here. Instead, the navmesh bounds are surfaced
  verbatim under the ``environment`` key so a later task (or the actual Unity
  Academy/Agent C# script) can clip/normalize world-frame observations against them.

* Reward-shaping coefficients -- not stock ML-Agents keys (ML-Agents' own
  ``reward_signals`` block is for reward *signal* configuration like extrinsic/curiosity
  weighting, not per-term shaping coefficients). They're written as a sibling top-level
  ``reward_shaping`` key, documented here rather than smuggled into ``hyperparameters``.
  The custom Unity Agent script (a later task) is expected to read this key directly.
"""
import json
import os

import yaml

# Conventional ML-Agents PPO defaults (see ML-Agents' default_config.yaml / training
# config docs) -- not specified by the v3 brief, so left at their stock values.
_DEFAULT_HYPERPARAMETERS = {
    "batch_size": 64,
    "buffer_size": 2048,
    "learning_rate": 3e-4,
    "beta": 5e-3,
    "epsilon": 0.2,
    "lambd": 0.95,
    "num_epoch": 3,
}
_DEFAULT_NETWORK_SETTINGS = {
    "normalize": False,
    "hidden_units": 128,
    "num_layers": 2,
}
_DEFAULT_REWARD_SIGNALS = {
    "extrinsic": {"gamma": 0.99, "strength": 1.0},
}
_DEFAULT_MAX_STEPS = 500000
_DEFAULT_TIME_HORIZON = 64
_DEFAULT_SUMMARY_FREQ = 10000

# Observation vector: [pos_x, pos_y, goal_x, goal_y] in navmesh world coords. See the
# module docstring for why this is a fixed size rather than derived from the grid.
_OBSERVATION_SIZE = 4

# Activity -> Unity BehaviorName + reward-shaping coefficients (v3 §6.2). Each template's
# coefficients are read by the custom Unity Agent script, not by mlagents-learn itself.
ACTIVITY_TEMPLATES = {
    "walk_to_point": {
        "behavior_name": "WalkToPoint",
        "distance_weight": -1.0,   # per-step penalty proportional to distance-to-goal
        "time_penalty": -0.01,     # per-step cost, encourages shorter episodes
        "success_bonus": 10.0,     # terminal reward on reaching the goal
    },
    "pick_object": {
        "behavior_name": "PickObject",
        "distance_weight": -1.0,   # per-step penalty proportional to gripper-to-object distance
        "time_penalty": -0.01,     # per-step cost
        "grasp_bonus": 5.0,        # reward on a successful grasp contact
        "lift_bonus": 5.0,         # reward for lifting the grasped object off its surface
        "success_bonus": 10.0,     # terminal reward: object delivered/held at target height
    },
    "follow_path": {
        "behavior_name": "FollowPath",
        "centerline_weight": -1.0,  # per-step penalty for lateral deviation from the path
        "progress_bonus": 0.5,      # per-step reward for forward progress along the path
        "time_penalty": -0.01,      # per-step cost
        "success_bonus": 10.0,      # terminal reward on reaching the path's end
    },
}


def _load_navmesh(twin: dict) -> dict:
    """twin DB record ({'navmesh_url': <path>, ...}) -> the navmesh.json dict it points to.

    Mirrors orchestrator/service.py's _load_navmesh -- same twin shape, same convention.
    """
    with open(twin["navmesh_url"]) as f:
        return json.load(f)


def build_trainer_config(activity: str, twin: dict, out_path: str) -> str:
    """Write an ML-Agents-format PPO trainer config YAML for `activity`, return out_path.

    `activity` must be a key of ACTIVITY_TEMPLATES; raises KeyError otherwise (the
    template lookup below fails naturally -- no need to re-wrap it).

    `twin` is a twin DB record: a dict with a `navmesh_url` key pointing at the
    navmesh.json written by twin.generator.generate_twin(). See the module docstring for
    why this shape was chosen over passing the navmesh dict directly.
    """
    template = ACTIVITY_TEMPLATES[activity]
    navmesh = _load_navmesh(twin)

    config = {
        "behaviors": {
            template["behavior_name"]: {
                "trainer_type": "ppo",
                "hyperparameters": dict(_DEFAULT_HYPERPARAMETERS),
                "network_settings": dict(_DEFAULT_NETWORK_SETTINGS),
                "reward_signals": {k: dict(v) for k, v in _DEFAULT_REWARD_SIGNALS.items()},
                "max_steps": _DEFAULT_MAX_STEPS,
                "time_horizon": _DEFAULT_TIME_HORIZON,
                "summary_freq": _DEFAULT_SUMMARY_FREQ,
            },
        },
        "observation_space": {
            "size": _OBSERVATION_SIZE,
            "description": "[pos_x, pos_y, goal_x, goal_y] in navmesh world coordinates",
        },
        "environment": {
            "navmesh": {
                "origin": navmesh["origin"],
                "cell": navmesh["cell"],
                "width": navmesh["width"],
                "height": navmesh["height"],
            },
        },
        "reward_shaping": {k: v for k, v in template.items() if k != "behavior_name"},
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)
    return out_path
