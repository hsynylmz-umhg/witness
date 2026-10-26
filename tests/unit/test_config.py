"""Configuration errors must be explicit before any media processing."""

from pathlib import Path

import pytest

from witness.cli import load_config, main
from witness.errors import WitnessError


@pytest.mark.parametrize(
    "content",
    [
        "[api]\nlive_calls_enabled = true\n",
        "[media]\nunknown_field = 1\n",
        "[media]\ncandidate_sample_fps = 'five'\n",
        "[media]\ncandidate_sample_fps = nan\n",
        "[media]\nmax_frame_count = true\n",
    ],
)
def test_invalid_or_unconsumed_config_is_rejected(tmp_path, content):
    path = tmp_path / "config.toml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(WitnessError):
        load_config(path)


def test_shipped_config_is_consumed_without_silent_fields():
    config_path = Path(__file__).parents[2] / "config/defaults.toml"
    assert load_config(config_path).candidate_sample_fps == 5


def test_invalid_cli_rate_is_an_english_error(tmp_path, capsys):
    assert (
        main(
            [
                "ingest",
                str(tmp_path / "missing.mp4"),
                "--data-origin",
                "synthetic",
                "--candidate-fps",
                "nan",
            ]
        )
        == 2
    )
    assert "finite and positive" in capsys.readouterr().err
