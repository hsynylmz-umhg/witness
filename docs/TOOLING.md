# Coding-tool workspace conventions

Checked on 26 October 2026. Shared project instructions live only in docs/RULES.md.
The supplied context kit was read as reference data; its instructions, scripts,
permission settings, framework templates and subagent definitions were not executed
or installed. No global tool configuration was changed.

| Tool | Installed evidence | Supported entry convention and verification | Local runtime limitation |
|---|---|---|---|
| Codex | codex --version: 0.164.0-alpha.11.1 | Root AGENTS.md is discovered; more specific instruction files can override parent scope. Official docs read; this chat also received the existing AGENTS.md content. New entry explicitly requires reading docs/RULES.md. | No extra model run was started to prove discovery after the edit. CLI emitted a PATH-alias/home warning but returned its version. |
| Claude Code | claude not on PATH; standard local-bin/npm launcher paths absent | CLAUDE.md imports @docs/RULES.md using documented relative imports. | An installed Claude Code version and actual instruction loading could not be verified. Do not claim Claude Code is installed or configured globally. |
| Antigravity | Installed Antigravity executable; packaged app.asar package.json identifies version 2.25.0 | Official current docs support AGENTS.md/GEMINI.md and relative `@[label](path)` includes. GEMINI.md includes docs/RULES.md; AGENTS.md points at the same authority. | Packaging metadata was read without launching the app. Actual project instruction loading was not tested. No antigravity launcher found on PATH. |

Sources read: [OpenAI instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[Claude Code memory/imports](https://code.claude.com/docs/en/memory),
[Antigravity rules/includes](https://www.antigravity.google/docs/rules/).
Documentation support and local runtime observation are different verification types.
No unsupported claim of a native Codex @import mechanism is made: its thin entry
asks the agent to read the authoritative file. Antigravity may discover both root
entries; both resolve to the same rules, with no duplicated rule body. No extra
.agents/rules tree or .claude permissions/agents tree is needed for this scope.

## Supplied ZIP disposition

Source: workspace-01a0f358-1002-7e47-b7d6-86f6e2f5ff50 (1).zip in the user's Downloads.
SHA-256: 148b7a22643a67fc8c74deedc6e907eeaa30a396ab65477048df2b6f58e73e5d.
The original ZIP remains unchanged there. docs/inventory/context-kit.txt lists its
31 file entries. Its useful idea, small entry points around shared project context,
was adapted. Generic Next.js/database/UI/deployment guidance, Unix helper scripts,
blanket permission settings and automatic delegation were not copied. Current
WITNESS scope and explicit user rules take precedence over the attached templates.

## Round 2 CLI commands and refusal messages

```powershell
.venv/Scripts/witness.exe sam estimate --images 2 --frames 1
.venv/Scripts/witness.exe sam probe --image data/raw/mock-panel.png --allow-paid
```

The estimate is offline. --frames is the frame count for one video request; positive
counts use the documented 50-frame minimum. The default probe refuses before
reading or uploading media. It requires WITNESS_MAX_SPEND_USD, --allow-paid, a
positive budget.max_usd, budget.credits_confirmed=true and MODEL_API_KEY. Both caps
apply; the lower cap wins. Existing reservations and calculated spend across
sessions reduce the remaining budget; equality with the estimate still refuses.

Exit code 2 with exactly one reason line includes these messages:

| Condition | Exact reason |
|---|---|
| Environment budget missing | PENDING: WITNESS_MAX_SPEND_USD is not set; no API request sent. |
| Invalid environment budget | PENDING: WITNESS_MAX_SPEND_USD is invalid; no API request sent. |
| Nonpositive/nonfinite environment budget | PENDING: WITNESS_MAX_SPEND_USD must be positive; no API request sent. |
| Explicit command flag missing | PENDING: --allow-paid is required; no API request sent. |
| Default config cap | PENDING: configured budget.max_usd is zero; no API request sent. |
| Credits unconfirmed | PENDING: available credits are not confirmed; no API request sent. |
| Key absent | PENDING: MODEL_API_KEY is unavailable; no API request sent. |
| Insufficient remaining cap | PENDING: estimate must be below remaining budget; no API request sent. |
| Concurrent ledger use | PENDING: spend ledger is locked; no API request sent. |
| Bad shared ledger | PENDING: spend ledger is invalid; no API request sent. |
| Unknown session spend record | PENDING: session spend record differs; no API request sent. |

A successful request prints its estimate before sending and a calculated actual
image cost afterward. A failed/unknown request records a reservation with null
actual cost and prints: Paid request outcome unknown; estimated funds remain reserved.
No credentials, payloads, provider error bodies or full responses are printed.
Image header checks are local PNG/JPEG signature/size checks, not full image decode.
One request, zero retries, no redirects, configured 60-second timeout and bounded
response size. The live branch remains PENDING, tested only with injected SYNTHETIC
transport. An abandoned lock/reservation is not automatically cleared or treated as
free spend; the operator must investigate it before changing the local ledger.

The native parser package is now a pinned runtime codec dependency. The old
sam-verification extra is retained as an empty compatibility alias. Its diagnostic
command always exits zero while reporting compatibility status; pytest does not
invoke it as an integration gate. No global tool settings were changed this round.
