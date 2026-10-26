# Local development environment

Established 26 October 2026 inside the project. No global Python packages were
installed or modified. .venv and .cache/uv are ignored. Base interpreter: existing
Anaconda Python 3.13.14, Windows x64. The py launcher reported no registered Python
installations; the working python executable was used directly. Python 3.11+ is
the project requirement, but this delivery was executed only on 3.13.14.

| Component | Actual local version | Purpose |
|---|---|---|
| Python | 3.13.14 | CLI, standard-library media/manifest handling |
| uv | 0.10.5 | Local environment and hashed universal resolution |
| ffmpeg / ffprobe | 8.0.1 essentials, Gyan build | Generated test clips / local decoded-frame metadata |
| NumPy | 2.5.4 | Binary-mask geometry and PCA |
| pytest | 9.1.1 | Focused offline behavior tests |
| Ruff | 0.17.2 | Lint and format checks |
| setuptools | 84.2.1 | Editable packaging; build requirement pinned explicitly |
| meta-sam-parser | 0.1.0 | Verified public runtime codec plus independent offline diagnostic; live integration unverified |

uv.lock pins transitive versions, source URLs and artifact hashes. It contains
Python-version branches, including NumPy 2.4.6 for Python <3.12; those environments
were resolved, not executed. No OpenAI SDK, web framework or second model provider
was installed. ffmpeg/ffprobe are external binaries rather than Python dependencies;
their installed versions/build identity are recorded, not downloaded or silently
pinned by uv. Cross-platform equivalence and bit-identical ffmpeg output are not
claimed. No repository software license was chosen on behalf of the user.

Recreate from a checkout with compatible local Python and ffprobe:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.cache/uv'
uv venv --python python .venv
uv sync --locked
```

Skip venv creation when .venv exists. The former sam-verification extra is an empty
compatibility alias; normal sync installs the pinned codec. After caches exist,
uv sync --locked --offline succeeds
for this recorded environment. uv lock --check --offline checks the project/lock
relationship without updating the resolution. Future dependency changes require
regenerating the lock and running the relevant checks.

Initial sandboxed PyPI access failed; the normal dependency download completed
through the approved network-capable command execution path. No model API was called.
An attempted uv pip index command was unsupported by installed uv and did not install
anything. Package registry metadata was checked separately. No .env contents or
credential values were read or printed; presence checks found no local .env or
META_API_KEY/MODEL_API_KEY in this process.

Round 2 promoted the already installed/pinned codec into runtime requirements and
regenerated the universal lock offline. No new framework or provider SDK was added.
The standard-library one-image HTTP adapter is gated and was not exercised live.
Marked ffmpeg tests are separated from the hermetic unmarked suite, which was run
with both ffmpeg and ffprobe absent from PATH. A fresh-checkout test omits all private
operator material and still validates published files and available provenance.
