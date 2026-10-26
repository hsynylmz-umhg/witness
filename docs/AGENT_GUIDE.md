# Agent guide

Working guide for any coding agent in this repo. `docs/RULES.md` is the authoritative rule
source; this file restates six of those rules and adds the commands and the tool map. If the
two disagree, `docs/RULES.md` wins.

witness is an offline-first video-integrity auditor. Given a clip, it decides which frames are
*clipped* or *blanked* to hide something, and emits an evidence report whose hash chain can be
recomputed from the output bytes. Solo hackathon entry, indie track. Judges are engineers and
VCs; the scoring criteria carry equal weight.

The claim of this repo is narrow and it must stay narrow: **a finding either carries an
evidence id or it does not exist.** Nothing here is a perception benchmark, and nothing
here may present a synthetic fixture as real-world accuracy.

---

## Commands

Windows, from the repo root. Use `.venv/Scripts/python.exe`, never bare `python` or bare
`pytest`: on this machine those resolve to a base Anaconda interpreter that does not have the
project installed.

```powershell
.venv/Scripts/python.exe -m pytest -q                        # full suite
.venv/Scripts/python.exe -m pytest -q -m "not ffmpeg"        # hermetic subset
.venv/Scripts/python.exe scripts/run_risk_gate.py            # risk gate, standalone
.venv/Scripts/python.exe -m ruff check .                     # lint
.venv/Scripts/python.exe -m ruff format --check .            # format check, never a reformat
.venv/Scripts/python.exe scripts/validate_workspace.py       # workspace validator
.venv/Scripts/python.exe -m witness build --session SESSION_DIR --procedure data/procedures/mock_panel_v1.json --out artifacts/OUT_DIR
```

Ruff is the only lint and format tool, configured in `pyproject.toml`. There is no type
checker. Do not add a tool without being asked; the dependency set is locked on purpose.

---

## The six rules. These are not preferences.

**1. Never report a test result you did not just see.**
Every claim about pytest must be accompanied by the last three lines of that exact command,
pasted verbatim in the final message. "Collected" is not "passed". A filtered run is not the
full run. If a command was not run, the answer is "not run".

This rule exists because three handoffs in a row claimed a green suite that was not green.
`docs/STATUS.md` is the single source of truth for numbers. Do not write a test count anywhere
else.

**2. The private operator folder is private.**
It is never tracked, never linked from a tracked file, never quoted into an issue or a commit.
Tracked files do not name its path; the validator rejects Markdown that does.

**3. Do not invent anything.**
No credentials, no projects, no metrics, no test results, no citations, no "integration test
passed" for a test that did not execute. If a needed file was not provided, stop and ask
for it instead of assuming its contents.

**4. One milestone per run.**
No UI, no coverage agent, no second provider, no voice, no procedure cards, no deployment,
no publication inside an early milestone prompt. If a task seems to require one of these,
that is a scope bug: say so rather than expanding.

**5. Never commit a template.**
If a staged or written file contains an unfilled angle-bracket placeholder (a less-than sign
followed by a digit or a name), stop before writing anything. Two commits have already been
produced with an unfilled pass/fail count in one.

**6. The tool taxonomy decides itself.** See the next section. Do not install a skill that is
marked KURMA in `docs/TOOLING.md`, and do not install anything that is not listed there
without writing the decision down first. The user installs; agents do not.

---

## Which tool for which job

This file is the policy; `docs/TOOLING.md` is the inventory and the reasoning. Only the
three skills below are installed. They are development aids: **none of them may run inside
the pipeline, and none of their output ships as product code.**

| The job | The tool | Why this one |
|---|---|---|
| Implementing a fix in `witness/` | **ponytail** | Removes code instead of adding it; never cuts validation, error handling or security. Matches rule 1 exactly |
| Making `report.html` not look generated | **hallmark** | Structural variety, no template fingerprints, 57-check slop test |
| README, demo script, submission copy | **humanizer** | 26–29 AI-writing tells, will not invent a fact or a number |
| Any question about the codebase shape | **graphify** (deferred) | Cheap local AST map. Not installed; the repo is ~45 files and does not need it yet |
| The 3-minute demo video | **Remotion**, separate `demo-video/` folder | Not a skill and not a dependency of `src/`. Never imported by the product |

**Explicitly rejected, with the reason in `docs/TOOLING.md` §4:** `hindsight`, `open-glean`,
`laya`, `claude-mem`, `omniroute`, `headroom`, `founder-skill`.

One of these deserves a sentence, because it will look attractive:

> **omniroute** is a multi-provider gateway that falls back off Claude when a quota runs out.
> This project is required to run on Meta models. A router that silently changes the model
> underneath a run is a disqualification risk, not an optimisation. **laya** is a 33 ms
> learned decision model whose base checkpoints score near chance (0.36 vs 0.318 random) and
> need fine-tuning; adding a learned classifier would break the thesis that every decision is
> deterministic geometry. **claude-mem** and **hindsight** would index the private operator
> folder.

If the user asks for one of these by name, say what the objection is, then do what the user
decides. Consultation over defence.

---

## Where the truth lives

| File | Contents |
|---|---|
| `docs/RULES.md` | The authoritative rule source. This guide restates six of them, nothing more |
| `docs/DECISIONS.md` | Append-only. A wrong decision gets **amended**, never deleted |
| `docs/RISK_GATE.md` | Risk gate behaviour, thresholds and the labelling audit |
| `docs/STATUS.md` | Current measured state. The only place numbers may be written; read its `## Current` block for what is open |
| `docs/TOOLING.md` | Agent-skill inventory and the install/reject reasoning |
| `tests/` | Fixtures are `SYNTHETIC_`-prefixed and named after the rule they pin |

Codec contract: `data = H, W, marker, payload`. There is no fallback decoder, and adding
one would be a decision, not a fix.

Budget: `WITNESS_MAX_SPEND_USD` is the only key that unlocks `--allow-paid`. Unset means
exit code 2. The approved ceiling is USD 1.00; it stays unspent until credits exist.

---

## Handoff

Commit messages in English; chat with the operator may be in Turkish. The operator runs every
Git command that writes to the index or a tag. When you finish a run, the final message ends
with the three pasted tails (suite, hermetic subset, risk gate). That is the whole handoff
contract.
