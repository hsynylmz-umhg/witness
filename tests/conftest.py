from pathlib import Path


def pytest_configure(config):
    # D025: pytest creates --basetemp without parents, so a fresh checkout lacks .tmp/.
    basetemp = config.getoption("basetemp")
    if basetemp:
        Path(basetemp).parent.mkdir(parents=True, exist_ok=True)
