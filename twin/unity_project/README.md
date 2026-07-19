# Unity batch-mode twin generator

Consumes the `scene.json` written by `twin/generator.py` (`POST /generate-twin`) and
produces a baked Unity scene.

```bash
Unity -batchmode -quit -nographics \
      -projectPath twin/unity_project \
      -executeMethod TwinForge.TwinGenerator.Build \
      -scene ../../data/twins/<mesh_id>/scene.json \
      -out Assets/Generated/Twin.unity
```

Prefabs are looked up by the `prefab` path in `twin/rules/mapping.yaml` under any
`Assets/Resources/` folder (e.g. `Assets/Resources/Furniture/RectTable.prefab`). None ship
with the repo — an unresolved prefab falls back to a correctly sized primitive, so the bake
and the collider geometry the planner depends on still come out right.

The `navmesh.json` next to `scene.json` is the Python planner's occupancy grid; Unity bakes
its own navmesh from these colliders.

## ML-Agents robot behavior (Phase C, v3 §6.2)

`TwinGenerator.Spawn()` can attach an ML-Agents `BehaviorParameters` component to any spawned
object whose `label == "robot"`, but this is compiled out by default — `Packages/manifest.json`
does not reference `com.unity.ml-agents`, and the project has no `.asmdef` under
`Assets/Editor/` to key a version-define off the package. The addition is guarded by the
`UNITY_ML_AGENTS` preprocessor symbol instead, so the generator compiles and behaves exactly
as before until you opt in. To enable it:

1. Install `com.unity.ml-agents` via Package Manager (Window > Package Manager > Add package
   by name).
2. Add `UNITY_ML_AGENTS` to Project Settings > Player > Other Settings > Scripting Define
   Symbols for the relevant build target (e.g. Standalone). This is a manual step — installing
   the package alone does not define the symbol.
3. Re-run the batch-mode build. Every "robot" object now gets a `BehaviorParameters` component
   with `BehaviorName = "TwinForgeRobot"` (placeholder default).
4. On the buggy prefab, replace that placeholder and drop on a reward script matching one of
   `policy/rl/config.py`'s `ACTIVITY_TEMPLATES` (`walk_to_point` → `BehaviorName`
   `"WalkToPoint"`, `pick_object` → `"PickObject"`, `follow_path` → `"FollowPath"`) so the
   `BehaviorName` lines up with what `mlagents-learn` and the trained policy expect.
