# TwinForge

End-to-end digital twin pipeline: capture → reconstruct → semantic label → twin generation → deploy.

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

## Quick Start

```bash
pip install -e sdk/
pip install -r requirements.txt
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.
