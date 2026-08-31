# BOA (BIG O API) — Python Full-Stack Development Framework

BOA is a Python framework for composing **CPU workflows** and **GPU Prismatics** behind a small, backend-neutral API. The foundation is designed for distributed processing, graphics workloads, transport abstractions, and incremental native acceleration.

## Architecture

### CPU Workflow

```text
View → Data → Grid → Controller → Secret → Session → Sequence → Model → Packet → Frame → Medium
```

At the framework boundary, the pipeline is exposed through `Workflow` / `CPUWorkflow` and a shared `BOAContext` data contract.

### GPU Prismatics

```text
Prismatics(Pitch, Roll, Index, Scatter)
                         │
              ┌──────────┼──────────┐
              │          │          │
           Vulkan      OpenGL     WebGL
```

Prismatics is backend-neutral: operations are composed first and delegated to a `ComputeBackend` implementation at execution time.

## Package Layout

```text
boa-bigapi-framework/
├── boa_bigapi/                 # Public framework API
│   ├── __init__.py
│   ├── workflow.py             # BOA / Workflow / CPUWorkflow
│   ├── context.py              # Shared BOAContext contract
│   └── prismatics.py           # Backend-neutral GPU operations
├── core/                       # Framework foundation
├── cpu_workflow/               # CPU pipeline implementations
├── gpu_method/                 # GPU operation implementations/backends
├── utils/                      # Logging, decorators, helpers
├── examples/                   # CPU and GPU examples
├── tests/                      # Unit/integration tests
├── .github/workflows/          # Continuous integration
├── pyproject.toml              # Packaging + development tooling
├── requirements.txt
└── LICENSE
```

## Core API

```python
from boa_bigapi import BOA, CPUWorkflow

workflow = CPUWorkflow()
boa = BOA(workflow=workflow)
result = boa.execute({"message": "hello"})
```

The public API intentionally separates orchestration from implementation. Components can be introduced through `workflow.use(component)` when they expose a `process(data)` method.

### Data Contract

```python
from boa_bigapi.context import BOAContext

context = BOAContext.create(
    payload={"message": "hello"},
    metadata={"source": "api"},
)
```

`BOAContext` carries a request identifier, timestamp, metadata, and payload so later distributed, tracing, serialization, and GPU-handoff features have a stable envelope.

### Prismatics

```python
from boa_bigapi.prismatics import Prismatics

# backend must implement ComputeBackend
prismatics = Prismatics(backend)
result = (
    prismatics
    .pitch(45)
    .roll(30)
    .index(mapping)
    .scatter(data_points)
    .compute()
)
```

## Installation

```bash
git clone https://github.com/somsung46813-creator/boa-bigapi-framework.git
cd boa-bigapi-framework
python -m pip install -e ".[dev]"
```

## CI

GitHub Actions validates the project with Python 3.10, 3.11, and 3.12 using:

```text
ruff check .
mypy boa_bigapi
pytest -q
```

Run the same checks locally before pushing:

```bash
ruff check .
mypy boa_bigapi
pytest -q
```

## Development Principles

1. Keep `boa_bigapi` as the stable public API boundary.
2. Keep CPU stages and GPU backends replaceable behind explicit contracts.
3. Treat `BOAContext` as the shared data envelope between processing stages.
4. Add tests for public behavior and new abstractions.
5. Keep native GPU bindings optional until backend contracts are stable.

## Documentation

The repository currently focuses on the stable foundation. Detailed API documentation can be added under `/docs` as the public contracts mature.

## License

GNU General Public License v3.0 — see `LICENSE`.

## Author

Created by `somsung46813-creator`.

## Repository

urlBOA GitHub repositoryhttps://github.com/somsung46813-creator/boa-bigapi-framework

---

**BOA Framework v1.0.0** — a composable foundation for full-stack distributed computing and GPU-accelerated processing.
