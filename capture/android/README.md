# TwinForge capture companion (Android / ARCore)

Streams ARCore depth frames to the orchestrator's `POST /capture` as `.npz` chunks — the
exact format `reconstruction/fast_path/fusion.py` back-projects (`depth` in metres,
`intrinsics` 3x3, `pose` 4x4 camera→world in the Z-up map frame).

```bash
./gradlew installDebug -PorchestratorUrl=http://<laptop-ip>:8000
```

Point it at a room, then tap **Finish scan** — that calls
`POST /capture/{scan_id}/complete` and prints the scan id to feed `POST /reconstruct`.

Requires a Depth API–capable device. Chunk indices are stable, so re-sending an index
overwrites it and an interrupted scan resumes.

**Not built or run in CI** — there is no Android SDK in this repo's toolchain. The `.npy`
header layout in `NpzWriter` was verified against numpy independently; everything
ARCore-facing is untested on hardware.
