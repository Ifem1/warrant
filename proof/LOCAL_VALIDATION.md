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
- Contract source SHA-256: `15B17B42BAA08CF9E03FC45514A8D533BB7889EFE79D1400DFD3354C074DC88C`
- Consumer source SHA-256: `D3BF746D022AFF096B6532A4C2C7AA0CA219CFFB0E6A03B6AD2087D678496322`

## Not completed in this environment

The execution environment could not reach package registries / GenLayer network services, so these checks are deliberately **not** claimed as passing:

- `genvm-lint check`
- `genvm-lint typecheck`
- `genvm-lint schema`
- `pytest` through the real `genlayer-test` Direct Mode runtime
- StudioNet deployment or finalized lifecycle proof

The finishing agent must run those checks with current GenLayer tooling, fix real compatibility errors without weakening the security invariants, add regression tests for fixes, then deploy both Warrant and `ProtectedTreasury` and fill `proof/LIVE_PROOF.md` from actual finalized receipts.
