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

## Silicon utilization

TwinForge places each workload on the cheapest silicon that meets its latency budget,
rather than putting everything on the largest available accelerator.

| Tier | Silicon | Compute unit | Workload |
|---|---|---|---|
| Perception | OnePlus 15 · Snapdragon 8 Elite | Hexagon NPU | YOLOv11-seg + MobileSAM, INT8 |
| Orchestration | Snapdragon X Elite AI PC | NPU | Reconstruction, twin generation, planning |
| Actuation | Arduino UNO Q · QRB2210 | **CPU — no NPU** | INT8 linear policy |

The UNO Q row is deliberate. The QRB2210 has a quad Cortex-A53, an Adreno 702 and a
low-power Hexagon DSP — **no tensor NPU** — so nothing here claims one. The measured
control-loop cost of the INT8 policy is ~1.3 µs per inference (`python -m
robot.policy_runner`), which is the point: a policy that cheap does not need an
accelerator, which is precisely why the heavy perception work belongs on the phone.

### Reproducing the benchmarks

Numbers come from profile jobs that ran on **physical devices** in the Qualcomm AI Hub
device cloud — not compile-time estimates. The toolchain needs Python ≤3.13
(`qai-hub-models` does not support 3.14):

```bash
python3.13 -m venv .venv-npu
.venv-npu/bin/pip install -r requirements-npu.txt

# Per-model extras are separate.
.venv-npu/bin/pip install "qai-hub-models[yolov11-seg]" "qai-hub-models[mobilesam]"

# mobilesam additionally needs mobile_sam, which its extra does NOT pull in
# (qai-hub-models 0.48.0 imports it but omits it from the model's requirements.txt).
# Not on PyPI — only the upstream repo. Skip this if you are not profiling mobilesam.
.venv-npu/bin/pip install "git+https://github.com/ChaoningZhang/MobileSAM.git"

# Token from https://app.aihub.qualcomm.com -> Settings -> API token
.venv-npu/bin/qai-hub configure --api_token <token>

.venv-npu/bin/python -m deployment.aihub_export.profile_models --list-devices
.venv-npu/bin/python -m deployment.aihub_export.profile_models \
    --model yolov11_seg --model mobilenet_v2 --device "Snapdragon 8 Elite" --compare
```

INT8 for a zoo model is a three-job pipeline, not a compile flag: ONNX compile →
`submit_quantize_job` with real calibration data → QNN compile. The harness delegates to
each model's own `export.py::export_model` rather than reimplementing that, because
passing `--quantize_full_type int8` to a single compile would produce an unquantized
graph labelled int8. Calibration uses the model's real sample data, never random noise.

Results land in `benchmarks/` and render in the dashboard's **Edge telemetry** panel.
`--compare` adds a CPU baseline on the same device, so latency becomes a ratio rather
than an absolute — which is what an efficiency claim requires.

Coverage is reported two ways, because layer count alone is misleading:

- **`op_coverage_pct`** — share of layers that compiled to the NPU.
- **`time_on_npu_pct`** — share of wall-clock time spent there.

A detector can be 98% NPU by layer count while a single `NonMaxSuppression` op on the CPU
eats 38% of the clock. `top_fallback_layers` names the offenders, worst first. Any model
under 80% layer coverage is flagged as needing a GPU fallback rather than being reported
as "NPU-deployed".

Latency comes from `all_inference_times` — every timed run, reported as p50/p95/p99 rather
than a single point estimate, since a control loop is judged on its tail.

The CPU baseline profiles the **same compiled binary** with `--compute_unit cpu`, so the
compute unit is the only variable that changes. Recompiling to a different runtime for the
baseline would confound the comparison.

### What is measured vs. estimated

| Number | Source |
|---|---|
| `benchmarks/*.json` latency, op coverage, peak memory | AI Hub device cloud, real hardware |
| `/optimize` `est_latency_ms` on the local path | Host CPU numpy timing (`latency_source: host-cpu`) |
| `/optimize` `op_coverage` on the local path | `null` — a locally-quantized bundle never touched an NPU |
| `robot.policy_runner` p50/p95 | Wall-clock on the host running the control loop |

Without an AI Hub token the export path still produces a real, loadable INT8 bundle — it
just reports `backend: local` and a null op coverage. A local bundle is never presented as
a Hexagon-compiled one.

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
