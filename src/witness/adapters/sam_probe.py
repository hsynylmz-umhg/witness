"""One bounded image request behind spending/credit gates; no video integration."""

import base64
import hashlib
import json
import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4

from witness.budget import approved_budget, estimate_cost, require_remaining_budget
from witness.config import Settings
from witness.errors import WitnessError
from witness.evidence.manifest import canonical_json


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def send_image(image: bytes, mime: str, key: str, settings: Settings) -> dict:
    """Single POST, no redirect/retry; no raw request/response is retained or logged."""
    body = {
        "model": "sam-3.1",
        "stream": False,
        "metadata": {"mask_encoding": "one_bit"},
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "tool"},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime};base64,"
                        + base64.b64encode(image).decode("ascii"),
                    },
                ],
            }
        ],
    }
    request = Request(
        "https://api.meta.ai/v1/responses",
        data=canonical_json(body),
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with build_opener(_NoRedirect()).open(
            request, timeout=settings.sam.timeout_seconds
        ) as reply:
            raw = reply.read(settings.sam.max_response_bytes + 1)
        if len(raw) > settings.sam.max_response_bytes:
            raise WitnessError("Provider response exceeded the local byte limit.")
        result = json.loads(raw)
        if not isinstance(result, dict) or result.get("status") != "completed":
            raise WitnessError("Provider did not return a completed image response.")
        return {"completed_images": 1}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        if isinstance(error, WitnessError):
            raise
        raise WitnessError("Provider request failed or its outcome is unknown.") from None


def _save(path: Path, content: dict) -> None:
    temporary = path.with_name(path.name + f".{uuid4().hex}.tmp")
    with temporary.open("xb") as stream:
        stream.write(canonical_json(content))
    os.replace(temporary, path)


def probe_image(
    image_path: Path,
    session_dir: Path,
    *,
    settings: Settings,
    allow_paid: bool,
    env_budget: str | None,
    api_key: str | None,
    ledger_root: Path,
    transport: Callable = send_image,
    provenance: str = "live_api",
    announce: Callable[[str], None] = print,
) -> dict:
    """Reserve against one shared ledger before sending; preserve unknown exposure.

    A successful single-image request has a calculated cost at the documented
    per-image rate. This is not an account invoice. Failures retain the reservation
    and record actual_usd=null; they are never silently treated as free.
    """
    budget = approved_budget(env_budget, allow_paid, settings)
    cost = estimate_cost(1, 0, settings).total_usd
    require_remaining_budget(cost, budget)
    if not api_key:
        raise WitnessError("PENDING: MODEL_API_KEY is unavailable; no API request sent.")
    if (
        not image_path.is_file()
        or not 0 < image_path.stat().st_size <= settings.sam.max_image_bytes
    ):
        raise WitnessError("PENDING: image is missing, empty or over the local size cap.")
    with image_path.open("rb") as stream:
        image = stream.read(settings.sam.max_image_bytes + 1)
    if len(image) > settings.sam.max_image_bytes:
        raise WitnessError("PENDING: image exceeds the local byte cap; no API request sent.")
    if image.startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    elif image.startswith(b"\xff\xd8\xff"):
        mime = "image/jpeg"
    else:
        raise WitnessError("PENDING: image must have a PNG or JPEG signature; no API request sent.")
    ledger_root.mkdir(parents=True, exist_ok=True)
    ledger_path, lock_path = ledger_root / "spend-ledger.json", ledger_root / ".spend.lock"
    try:
        lock = lock_path.open("x", encoding="ascii")
    except FileExistsError:
        raise WitnessError("PENDING: spend ledger is locked; no API request sent.") from None
    try:
        with lock:
            lock.write("exclusive request reservation\n")
        ledger = {"schema_version": "0.1", "requests": []}
        if ledger_path.exists():
            try:
                ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
                if ledger["schema_version"] != "0.1" or not isinstance(ledger["requests"], list):
                    raise ValueError
                amounts = []
                for row in ledger["requests"]:
                    amount = Decimal(
                        row["actual_usd"]
                        if row["actual_usd"] is not None
                        else row["reservation_usd"]
                    )
                    if not amount.is_finite() or amount <= 0:
                        raise ValueError
                    amounts.append(amount)
                spent = sum(amounts, Decimal(0))
            except (ValueError, KeyError, TypeError, ArithmeticError):
                raise WitnessError(
                    "PENDING: spend ledger is invalid; no API request sent."
                ) from None
        else:
            spent = Decimal(0)
        remaining = budget - spent
        require_remaining_budget(cost, remaining)
        session_dir.mkdir(parents=True, exist_ok=True)
        session_spend = session_dir / "spend.json"
        if session_spend.exists():
            try:
                old = json.loads(session_spend.read_text(encoding="utf-8"))
                expected_rows = [
                    row for row in ledger["requests"] if row["session_id"] == session_dir.name
                ]
                if old != {"schema_version": "0.1", "requests": expected_rows}:
                    raise ValueError
            except (ValueError, KeyError, TypeError):
                raise WitnessError(
                    "PENDING: session spend record differs; no API request sent."
                ) from None
        entry = {
            "request_id": str(uuid4()),
            "session_id": session_dir.name,
            "created_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "data_origin": provenance,
            "model": "sam-3.1",
            "status": "pending",
            "reservation_usd": str(cost),
            "actual_usd": None,
            "approved_budget_usd": str(budget),
            "remaining_before_usd": str(remaining),
            "credits_confirmed_by_operator": settings.budget.credits_confirmed,
            "cost_basis": "completed image count times published unit price; not an invoice",
            "source_sha256": hashlib.sha256(image).hexdigest(),
            "max_retries": 0,
        }
        ledger["requests"].append(entry)

        def persist() -> None:
            _save(ledger_path, ledger)
            _save(
                session_dir / "spend.json",
                {
                    "schema_version": "0.1",
                    "requests": [
                        row for row in ledger["requests"] if row["session_id"] == session_dir.name
                    ],
                },
            )

        persist()
        announce(f"Estimated USD {cost:.6f}; remaining USD {remaining:.6f}; maximum one request.")
        try:
            result = transport(image, mime, api_key, settings)
            if result.get("completed_images") != 1:
                raise WitnessError("Image billing units could not be confirmed.")
        except Exception:
            entry["status"] = "uncertain"
            persist()
            raise WitnessError(
                "Paid request outcome unknown; estimated funds remain reserved."
            ) from None
        entry["status"], entry["actual_usd"] = "completed", str(cost)
        persist()
        announce(f"Calculated actual USD {cost:.6f}; account invoice unverified.")
        return entry
    finally:
        lock_path.unlink()
