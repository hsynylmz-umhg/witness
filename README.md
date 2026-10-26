# WITNESS

Evidence-linked observations from one fixed-camera civil assembly video.

WITNESS aims to help CubeSat/model-satellite teams review visible tool motion
against procedure steps and replay supporting evidence. It does not measure torque,
prove correct assembly, certify flight readiness or infer omission from missing
evidence. Local hashes require trusted references and do not prevent rewriting a
complete record.

**Current delivery: offline perception contract and synthetic risk gate.** Local
video ingest, PTS-based sampling, strict SAM mask/line-subset decoding and a pure
rotation/stop candidate detector work offline. The synthetic experiment measures
precision 10/11 and recall 10/13 across 25 cases. These are estimator results, not
real perception quality. A paid single-image probe exists behind explicit gates;
its live branch is PENDING. No real video/SAM integration has run.

## Run locally

Use compatible Python 3.11+ and the project-local environment. Tested: Python
3.13.14, uv 0.10.5, FFmpeg 8.0.1. Exact dependency resolutions/hashes are in uv.lock.
ffprobe is needed for ingest; ffmpeg is also needed for marked media tests.

Run separate PowerShell commands from the project root:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.cache/uv'
uv venv --python python .venv
uv sync --locked
.venv/Scripts/witness.exe --help
.venv/Scripts/witness.exe ingest data/raw/mock-panel.mp4 --data-origin real --config config/defaults.toml
```

Skip venv creation if .venv exists. No keys or network are needed for ingest. The
CLI does not load .env. Use --data-origin synthetic for generated footage. Candidate
5 fps remains experimental; override with --candidate-fps only as an experiment.
No frame extraction, transcoding or video upload is performed.

A successful ingest writes session.json, timeline.json, legacy samples.json, new
sampling.json, effective config.json and the initial manifest/digest under a fresh
UUID directory in artifacts/sessions. sampling.json preserves original frame/PTS
identity and records unknown-time source indices without interpolation. Defaults
bound local inputs to 120 seconds, 1 GiB, 20,000 decoded frames and a 60-second
ffprobe timeout. Supported local containers are broader than SAM's documented media
formats. Inputs remain unchanged and output sessions stay outside version control.

## Offline contract, estimator and spend checks

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m pytest -m 'not ffmpeg' -q
.venv/Scripts/ruff.exe check src tests scripts
.venv/Scripts/ruff.exe format --check src tests scripts
.venv/Scripts/python.exe scripts/validate_workspace.py
.venv/Scripts/python.exe scripts/check_sam_contract.py
.venv/Scripts/python.exe -m scripts.run_risk_gate
.venv/Scripts/witness.exe sam estimate --images 2 --frames 1
```

The native parser diagnostic is informational and uses only a documented SYNTHETIC
vector. Its earlier failure was caused by an extra marker in our diagnostic;
D017 records the correction. The test suite covers 21 conformance fixtures, 200
random-mask round trips, uncertain tails, bad gates, timestamp gaps, sampling and
budget refusals. The unmarked suite also passes with ffmpeg/ffprobe absent from PATH.

A live command is available as witness sam probe --image <local PNG/JPEG> --allow-paid.
It refuses unless positive environment/config caps, operator-confirmed available
credits, a local key and a strictly sufficient remaining budget are all present.
Defaults deny it. One bounded request, no retry/redirect; a shared ledger reserves
cost before sending and mirrors a spend sidecar to the selected session. Failure
keeps uncertain cost reserved. Published-rate calculated cost is not an account
invoice. See TOOLING for exact refusal messages; no paid request ran this round.

## Project context and next gate

Shared instructions live only in [RULES](docs/RULES.md); AGENTS.md, CLAUDE.md and
GEMINI.md are thin references. Historical design material and archived scaffold
are held privately by the operator, preserved unchanged and not published. Fresh
checkouts can omit them; the validator checks available recorded hashes and emits
one informational skip line for missing private material. The baseline inventory
remains unchanged. The operator alone performs Git mutations.

Read [STATUS](docs/STATUS.md), [measured RISK_GATE](docs/RISK_GATE.md),
[product brief](docs/PROJECT_BRIEF.md), [roadmap](docs/ROADMAP.md),
[API verification](docs/API_VERIFICATION.md), [data contracts](docs/DATA_CONTRACTS.md),
[recording/evaluation](docs/EVALUATION.md), [tooling](docs/TOOLING.md),
[environment](docs/ENVIRONMENT.md), [decisions](docs/DECISIONS.md),
[provenance](docs/NEW_WORK.md), [sources](docs/PRIOR_ART.md) and [demo plan](docs/DEMO.md).

The next gate requires a permitted 30-second fixed-camera mock-panel recording,
then real mask/ID and source-time validation. Procedure parsing, ordering audit,
reports/PDF/UI, coverage planning, voice, generated cards, alternative providers,
CI, deployment and publication were not implemented this round.
