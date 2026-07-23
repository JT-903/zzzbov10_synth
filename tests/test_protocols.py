"""Simulate every Opentrons protocol in protocols/ to catch syntax/API breakage."""

import subprocess
import sys
from pathlib import Path

import pytest

PROTOCOLS_DIR = Path(__file__).parent.parent / "protocols"
PROTOCOL_FILES = sorted(PROTOCOLS_DIR.glob("*.py"))

# opentrons>=9.1.0 dropped simulation support for the OT-2 robot type
# (opentrons.simulate raises RuntimeError unconditionally), so this
# protocol can't be simulated until Mara's script is ported to Flex
# or run against an older opentrons release.
KNOWN_UNSIMULATABLE = {"meatball_Maranara.py"}


def _protocol_id(path: Path) -> str:
    return path.name


@pytest.mark.parametrize("protocol_path", PROTOCOL_FILES, ids=_protocol_id)
def test_protocol_simulates(protocol_path: Path):
    if protocol_path.name in KNOWN_UNSIMULATABLE:
        pytest.xfail(
            f"{protocol_path.name} targets an OT-2, which the installed "
            "opentrons version can no longer simulate"
        )

    result = subprocess.run(
        [sys.executable, "-m", "opentrons.simulate", str(protocol_path), "-o", "nothing"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"Simulation of {protocol_path.name} failed:\n{result.stdout}\n{result.stderr}"
    )
