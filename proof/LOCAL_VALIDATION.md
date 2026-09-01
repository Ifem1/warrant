# Local Validation Status

This file records only checks actually completed in the package-generation environment.

## Completed

- `python scripts/preflight.py`: **25 passed, 0 failed**
- Python syntax/bytecode compilation for:
  - `contracts/warrant.py`
  - `examples/protected_treasury.py`
  - `tests/conftest.py`
  - `tests/test_warrant.py`
- Frontend boundary check: no `frontend/`, `app/`, `pages/`, or `src/components/` application surface is present.
- Contract source SHA-256: `83870F93E24FBA37CADD5946BDFFF82E81006352BDF9B6C250C8060AF508973D`
- Consumer source SHA-256: `09C439BB688359823AAD7DBA6F060849AA19D15EE698328EFEBC864F3D6280EB`

## Not completed in this environment

Windows Direct Mode cannot initialize the injected SDK calldata context, so its result is not claimed here. Address-based cross-contract calls are also unsupported by genlayer-test Direct Mode; composition belongs to StudioNet. The following checks were completed in clean Linux GitHub Actions run `33442549070`:

- `genvm-lint check`, `typecheck`, and `schema` for both contracts
- 35 Direct Mode tests passed and one unsupported composition test skipped
- StudioNet deployments are finalized; the lifecycle remains incomplete in `LIVE_PROOF.md`

The finishing agent must run those checks with current GenLayer tooling, fix real compatibility errors without weakening the security invariants, add regression tests for fixes, then deploy both Warrant and `ProtectedTreasury` and fill `proof/LIVE_PROOF.md` from actual finalized receipts.
