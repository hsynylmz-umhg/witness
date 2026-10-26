"""Hermetic spending-gate tests: injected SYNTHETIC transport, never a paid call."""

import json
from dataclasses import replace
from decimal import Decimal

import pytest

from witness.adapters.sam_probe import probe_image
from witness.budget import approved_budget, estimate_cost
from witness.cli import main
from witness.config import BudgetConfig, load_settings
from witness.errors import WitnessError


@pytest.fixture
def settings():
    settings = load_settings()
    return replace(settings, budget=BudgetConfig(Decimal("0.01"), True))


def test_prices_and_per_request_video_minimum_are_explicit(settings):
    cost = estimate_cost(2, 1, settings)
    assert cost.billed_frames == 50
    assert cost.image_usd == Decimal("0.005")
    assert cost.video_usd == Decimal("0.01")
    assert estimate_cost(0, 0, settings).total_usd == 0


@pytest.mark.parametrize(
    "amount,flag,reason",
    [
        (None, True, "not set"),
        ("0", True, "positive"),
        ("-1", True, "positive"),
        ("NaN", True, "positive"),
        ("Infinity", True, "positive"),
        ("invalid", True, "invalid"),
        ("1", False, "--allow-paid"),
    ],
)
def test_missing_gates_refuse(settings, amount, flag, reason):
    with pytest.raises(WitnessError, match=reason):
        approved_budget(amount, flag, settings)


def test_zero_config_budget_and_unconfirmed_credits_refuse(settings):
    with pytest.raises(WitnessError, match="zero"):
        approved_budget("1", True, replace(settings, budget=BudgetConfig(Decimal(0), True)))
    with pytest.raises(WitnessError, match="credits"):
        approved_budget("1", True, replace(settings, budget=BudgetConfig(Decimal(1), False)))


def test_probe_cli_without_opt_in_never_reaches_transport(monkeypatch, capsys):
    monkeypatch.delenv("WITNESS_MAX_SPEND_USD", raising=False)
    assert main(["sam", "probe", "--image", "unused.png", "--allow-paid"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.count("\n") == 1
    assert "PENDING" in captured.err


def test_estimate_cli_is_offline_and_includes_billable_minimum(capsys):
    assert main(["sam", "estimate", "--images", "2", "--frames", "1"]) == 0
    output = capsys.readouterr().out
    assert "0.015000" in output
    assert "50" in output


def run_synthetic_probe(tmp_path, settings, transport, session="SYNTHETIC_session", **overrides):
    image = tmp_path / "SYNTHETIC_image.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\nSYNTHETIC_HEADER_ONLY")
    arguments = dict(
        settings=settings,
        allow_paid=True,
        env_budget="0.01",
        api_key="SYNTHETIC_TEST_TOKEN",
        ledger_root=tmp_path / "ledger",
        transport=transport,
        provenance="synthetic_test",
        announce=lambda line: None,
    )
    arguments.update(overrides)
    return probe_image(image, tmp_path / session, **arguments)


def test_success_records_only_calculated_cost_and_safe_metadata(tmp_path, settings):
    calls = []

    def transport(*args):
        calls.append(True)
        return {"completed_images": 1}

    entry = run_synthetic_probe(tmp_path, settings, transport)
    assert len(calls) == 1
    assert entry["status"] == "completed"
    assert Decimal(entry["actual_usd"]) == Decimal("0.0025")
    raw = (tmp_path / "SYNTHETIC_session/spend.json").read_text(encoding="utf-8")
    assert "SYNTHETIC_TEST_TOKEN" not in raw
    assert "SYNTHETIC_HEADER_ONLY" not in raw
    assert json.loads(raw)["requests"][0]["data_origin"] == "synthetic_test"


def test_remaining_budget_is_shared_across_sessions_and_equality_refuses(tmp_path, settings):
    def transport(*args):
        return {"completed_images": 1}

    for index in range(3):
        run_synthetic_probe(tmp_path, settings, transport, session=f"SYNTHETIC_{index}")
    with pytest.raises(WitnessError, match="below remaining"):
        run_synthetic_probe(tmp_path, settings, transport, session="SYNTHETIC_fourth")
    assert len(json.loads((tmp_path / "ledger/spend-ledger.json").read_text())["requests"]) == 3


def test_unknown_outcome_keeps_reservation_and_never_retries(tmp_path, settings):
    calls = []

    def broken(*args):
        calls.append(True)
        raise TimeoutError("SYNTHETIC failure containing sensitive request data")

    with pytest.raises(WitnessError, match="funds remain reserved") as caught:
        run_synthetic_probe(tmp_path, settings, broken)
    assert "sensitive request data" not in str(caught.value)
    entry = json.loads((tmp_path / "SYNTHETIC_session/spend.json").read_text())["requests"][0]
    assert entry["status"] == "uncertain"
    assert entry["actual_usd"] is None
    assert entry["reservation_usd"] == "0.0025"
    assert len(calls) == 1


def test_missing_key_refuses_before_any_image_read_or_transport(tmp_path, settings):
    with pytest.raises(WitnessError, match="MODEL_API_KEY"):
        probe_image(
            tmp_path / "missing.png",
            tmp_path / "session",
            settings=settings,
            allow_paid=True,
            env_budget="1",
            api_key=None,
            ledger_root=tmp_path / "ledger",
        )
    assert not (tmp_path / "ledger").exists()


def test_locked_ledger_refuses_without_sending(tmp_path, settings):
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    (ledger / ".spend.lock").write_text("SYNTHETIC_OTHER_PROCESS", encoding="ascii")
    with pytest.raises(WitnessError, match="ledger is locked"):
        run_synthetic_probe(tmp_path, settings, lambda *args: pytest.fail("Transport reached"))
    assert (ledger / ".spend.lock").exists()


def test_invalid_ledger_cannot_credit_a_negative_amount(tmp_path, settings):
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    (ledger / "spend-ledger.json").write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "requests": [{"actual_usd": "-1", "reservation_usd": "1"}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(WitnessError, match="ledger is invalid"):
        run_synthetic_probe(tmp_path, settings, lambda *args: pytest.fail("Transport reached"))


def test_unrecognized_session_spend_is_preserved(tmp_path, settings):
    session = tmp_path / "SYNTHETIC_session"
    session.mkdir()
    path = session / "spend.json"
    original = '{"private_existing_record":true}'
    path.write_text(original, encoding="utf-8")
    with pytest.raises(WitnessError, match="session spend record differs"):
        run_synthetic_probe(tmp_path, settings, lambda *args: pytest.fail("Transport reached"))
    assert path.read_text(encoding="utf-8") == original


def test_image_transport_builds_one_verified_request_without_network(settings, monkeypatch):
    from witness.adapters import sam_probe

    calls = []

    class Reply:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            return b'{"status":"completed"}'

    class Opener:
        def open(self, request, timeout):
            calls.append((request, timeout))
            return Reply()

    monkeypatch.setattr(sam_probe, "build_opener", lambda handler: Opener())
    assert sam_probe.send_image(b"SYNTHETIC", "image/png", "SYNTHETIC_TOKEN", settings) == {
        "completed_images": 1,
    }
    assert len(calls) == 1
    request, timeout = calls[0]
    body = json.loads(request.data)
    assert body["model"] == "sam-3.1"
    assert body["input"][0]["content"][1]["image_url"].startswith("data:image/png;base64,")
    assert timeout == settings.sam.timeout_seconds
