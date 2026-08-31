"""Repository-level preflight checks for Warrant.

This intentionally supplements rather than replaces genvm-lint and Direct Mode.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "contracts" / "warrant.py"
CONSUMER = ROOT / "examples" / "protected_treasury.py"
TESTS = ROOT / "tests" / "test_warrant.py"

errors: list[str] = []
checks: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        checks.append(message)
    else:
        errors.append(message)


for path in (PRIMARY, CONSUMER, TESTS):
    check(path.exists(), f"exists: {path.relative_to(ROOT)}")
    if path.exists():
        try:
            ast.parse(path.read_text(encoding="utf-8"))
            checks.append(f"python syntax: {path.relative_to(ROOT)}")
        except SyntaxError as exc:
            errors.append(f"python syntax: {path.relative_to(ROOT)}: {exc}")

primary = PRIMARY.read_text(encoding="utf-8") if PRIMARY.exists() else ""
consumer = CONSUMER.read_text(encoding="utf-8") if CONSUMER.exists() else ""
tests = TESTS.read_text(encoding="utf-8") if TESTS.exists() else ""

check("class Warrant(gl.Contract)" in primary, "canonical Warrant contract present")
check("run_nondet_unsafe" in primary, "custom consensus present")
check("INDEPENDENTLY CLASSIFY DELEGATION SUBSET" in primary, "independent delegation validation present")
check("INDEPENDENTLY CLASSIFY ACTION SCOPE" in primary, "independent action validation present")
check("def create_root" in primary and "_classify_subset" not in primary.split("def create_root", 1)[1].split("def delegate", 1)[0], "root authority is explicit, not AI-granted")
check("def _reserve_chain" in primary, "transitive ancestor exposure accounting present")
check("def revoke" in primary and "def _effective_at" in primary, "revocation/effective-lineage logic present")
check("def permit_valid_for" in primary, "consumer permit gate present")
check('emit(on="finalized").record_consumption' in consumer, "consumer uses finalized consumption callback")
check("used_permits" in consumer, "consumer local replay guard present")
check("warrant.view().permit_valid_for" in consumer, "consumer performs synchronous Warrant validation")
check("run_validator() is False" in tests, "adversarial validator-disagreement tests present")
check(tests.count("def test_") >= 25, "at least 25 Direct Mode scenarios present")

for forbidden in ("frontend", "app", "pages", "src/components"):
    check(not (ROOT / forbidden).exists(), f"no frontend boundary: {forbidden}")

for path in ROOT.rglob("*"):
    if path.is_file() and path.name in {".env", "id_rsa"}:
        errors.append(f"sensitive file present: {path.relative_to(ROOT)}")

if PRIMARY.exists():
    digest = hashlib.sha256(PRIMARY.read_bytes()).hexdigest().upper()
    checks.append(f"warrant sha256: {digest}")
if CONSUMER.exists():
    digest = hashlib.sha256(CONSUMER.read_bytes()).hexdigest().upper()
    checks.append(f"consumer sha256: {digest}")

print(f"Warrant preflight: {len(checks)} passed, {len(errors)} failed")
for item in checks:
    print(f"PASS  {item}")
for item in errors:
    print(f"FAIL  {item}")

sys.exit(1 if errors else 0)
