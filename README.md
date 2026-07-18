# TwinForge

**Edge-first Physical AI operating layer.** Point a phone at any real space and get a
simulation-ready digital twin, a robot that can be taught a task by voice in any language,
and a policy that runs — fully offline — on Snapdragon silicon.

TwinForge automates the full loop **capture → reconstruct → semantic-label → generate
simulation-ready twin → adapt policy → edge-optimize → deploy**, exposed as one REST API
and one Python SDK, running on commodity edge hardware (phone + AI PC + microcontroller)
instead of a cloud GPU cluster. See [`detailed implementation doc.md`](detailed%20implementation%20doc.md)
for the full system design blueprint (architecture, API spec, DB schema, judging-criteria
mapping).

Built for the Snapdragon Multiverse Hackathon (Noida, July 2026).

## Team — TwinForge

| Name | Email |
| --- | --- |
| _TBD_ | _TBD_ |
| _TBD_ | _TBD_ |

Repository: https://github.com/adt-kmr/TwinForge

## Structure

```
TwinForge/
├── README.md
├── docs/                    # Architecture ADRs, OpenAPI specs, references
├── sdk/twinforge/           # pip-installable client: capture(), reconstruct(), train(), deploy()
├── orchestrator/            # Pipeline state machine, job queue, REST gateway
├── capture/
│   ├── android/             # OnePlus 15 companion app (ARCore session, chunked upload)
│   └── service/             # Thin FastAPI receiver
├── reconstruction/
│   ├── fast_path/           # Open3D TSDF fusion
│   └── fidelity_path/       # COLMAP + gsplat/nerfstudio pipeline glue
├── semantic/service/        # YOLO-World + MobileSAM inference, label ontology
├── twin/
│   ├── unity_project/       # Unity batch-mode generator, prefab library
│   └── rules/               # label → prefab/collider mapping (YAML)
├── robot/
│   ├── ros2_ws/             # ROS2 packages: nav, adapters
│   ├── adapters/            # TwinForgeRobot: SimRobot, UnoQRobot
│   └── unoq_bridge/         # sketch/ + python/ per Arduino App Lab structure
├── policy/
│   ├── baselines/           # Pretrained checkpoints
│   └── finetune/            # Behaviour-cloning fine-tune scripts
├── deployment/
│   ├── aihub_export/        # Export scripts per model, WSL build-host notes
│   └── qairt/               # Local conversion fallback
├── sarvam/task_engine/      # Provider interface, FunctionGemma offline fallback
├── dashboard/               # React app
├── examples/                # Demo scenario configs (warehouse, factory, hospital, museum)
├── scripts/                 # One-shot setup/dev scripts
├── docker/                  # Dockerfiles + docker-compose.yml
├── k8s/                     # Optional/future Kubernetes manifests
├── tests/
├── models/                  # Exported artifacts (gitignored, pulled via script)
├── configs/                 # Default configuration files
├── .gitignore / .gitattributes / .editorconfig / .pre-commit-config.yaml
├── pyproject.toml / setup.cfg / requirements*.txt
├── Makefile / LICENSE / CHANGELOG.md
├── CONTRIBUTING.md / CODE_OF_CONDUCT.md / SECURITY.md
└── .github/                 # CI workflows + issue templates
```

## Setup From Scratch

Requires Python 3.10+ and Docker (for the multi-service run path).

```bash
# 1. Clone
git clone https://github.com/adt-kmr/TwinForge.git
cd TwinForge

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install the SDK + runtime dependencies
make install
# (dev dependencies + pre-commit hooks: make install-dev)
```

No external accounts are required to install or run the test suite. Live pipeline runs
against real models additionally need (all optional, see `.env.example`):

- `AI_HUB_API_TOKEN` — Qualcomm AI Hub, for NPU export/quantization (`deployment/aihub_export/`)
- `SARVAM_API_KEY` — Sarvam Task Engine, for online NL→task-graph planning (falls back to
  the on-device FunctionGemma provider if unset)

## Run

**Single service, locally (no Docker):**

```bash
uvicorn orchestrator.service:app --reload --port 8000
```

**Full stack via Docker Compose** (orchestrator + capture + semantic services):

```bash
docker compose -f docker/docker-compose.yml up --build
```

Orchestrator REST API is then available at `http://localhost:8000` (see
[`docs/api/openapi.yaml`](docs/api/openapi.yaml) for the full surface, or Section 16 of
the implementation doc).

**Python SDK:**

Each stage is a method on the client, and `run_pipeline` chains all eight:

```python
from twinforge import TwinForge

tf = TwinForge("http://localhost:8000")

# Frames are .npz files with depth (H,W float32 m), intrinsics (3,3),
# pose (4,4 camera->world), and optional color (H,W,3 uint8).
result = tf.run_pipeline(["frame_00000.npz"], text="go to the table")
print(result["sim_success_rate"], result["deployment_id"])
```

Or drive the stages individually:

```python
scan = tf.capture(["frame_00000.npz"], meta={"device": "oneplus15"})
mesh = tf.reconstruct(scan["scan_id"], mode="fast")
objects = tf.segment(mesh["mesh_id"])
twin = tf.generate_twin(mesh["mesh_id"], objects["objects_id"])
graph = tf.plan(twin["twin_id"], "go to the table then wait")
policy = tf.train(twin["twin_id"], graph["task_graph_id"])   # 409 if sim gate fails
artifact = tf.optimize(policy["policy_id"], device_label="Snapdragon X Elite CRD")
tf.deploy(artifact["artifact_id"], kind="sim")
```

`train` enforces the section 11.5 gate: a policy that scores below 0.6 over 20 sim
episodes is rejected with HTTP 409 rather than exported.

## Test

```bash
make test        # pytest
make coverage     # pytest with coverage report
```

## License

MIT — see [LICENSE](LICENSE). Third-party component licenses are documented in
[`docs/THIRD_PARTY_LICENSES.md`](docs/THIRD_PARTY_LICENSES.md).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow.
