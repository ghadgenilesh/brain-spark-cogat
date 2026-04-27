"""Shared fixtures for all BrainSpark test suites."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
QUESTIONS_JSON = REPO_ROOT / "questions.json"
GETSMART_HTML = REPO_ROOT / "getsmart.html"

# ---------------------------------------------------------------------------
# questions.json fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def questions():
    """Load and return the full questions list from questions.json."""
    with QUESTIONS_JSON.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def questions_by_id(questions):
    """Dict of question id → question for fast lookup."""
    return {q["id"]: q for q in questions}


# ---------------------------------------------------------------------------
# Generator output fixture (one-time run per session)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def generated_questions(tmp_path_factory):
    """Run gen_questions.py in a temp dir and return the generated list."""
    import importlib.util
    import io
    import contextlib
    import os

    tmp = tmp_path_factory.mktemp("gen")
    # Patch the output path so the generator writes to tmp
    src = (REPO_ROOT / "gen_questions.py").read_text(encoding="utf-8")
    patched = src.replace(
        'f"/Users/nilesh/Projects/brainspark/questions_{timestamp}.json"',
        f'str(tmp / f"questions_{{timestamp}}.json")',
    )
    # Inject tmp variable into the script's namespace via exec
    ns = {"__name__": "__not_main__", "tmp": tmp}
    exec(compile(patched, "gen_questions.py", "exec"), ns)  # noqa: S102

    # Find the written file
    files = list(tmp.glob("questions_*.json"))
    assert files, "gen_questions.py did not produce an output file"
    out_file = files[0]

    results = []
    with out_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


# ---------------------------------------------------------------------------
# Local HTTP server for E2E tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def local_server():
    """Spin up python -m http.server on the repo root for E2E tests."""
    import socket
    import time

    port = 8788  # unlikely to clash
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--directory", str(REPO_ROOT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Wait for server to be ready
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            time.sleep(0.1)
    else:
        proc.terminate()
        pytest.fail("Local HTTP server did not start in time")

    yield f"http://127.0.0.1:{port}"

    proc.terminate()
    proc.wait()
