# Agent Handoff Rules

The goal is to finish, validate, deploy and push **Warrant as a standalone GenLayer Intelligent Contract**.

## Non-negotiable product boundary

- Do not add a frontend.
- Do not turn this into a dApp/project submission.
- Do not add escrow, payments, reputation or unrelated product flows to the primary contract.
- Keep `contracts/warrant.py` as the canonical primitive.
- Keep `examples/protected_treasury.py` minimal and focused on proving composition.

## Security invariants that must survive fixes

1. Root authority is explicit and does not require AI approval.
2. A child must pass semantic subset consensus and deterministic narrowing.
3. `AMBIGUOUS` fails closed.
4. Child target/caps/expiry cannot widen the parent.
5. Every permit charges every ancestor's lifetime exposure ceiling.
6. Revoking any ancestor invalidates descendants dynamically.
7. Permits bind consumer + action key + payload hash + amount.
8. Consumers must have local replay protection before protected state change.
9. Cross-contract consumption notification uses finalized messaging and is idempotent.
10. Requested actions must pass semantic scope checks against every authority in the active lineage, not only the leaf.
11. Never fabricate live proof, addresses, scores, receipts or passing commands.

## Finish sequence

1. Read `README.md`, `docs/ARCHITECTURE.md`, `docs/CONSENSUS.md`, `docs/SECURITY.md` and `DEPLOYMENT.md`.
2. Install current tooling from `requirements-dev.txt` plus `genvm-linter` and current GenLayer CLI.
3. Run `python scripts/preflight.py`.
4. Run the full Direct Mode suite.
5. Run GenVM lint/validate/typecheck/schema on both contracts.
6. Fix every real error while preserving the invariants above.
7. Add regression tests for every fix.
8. Re-run all checks until clean.
9. Deploy Warrant to StudioNet and wait for finalization.
10. Deploy `ProtectedTreasury` with the finalized Warrant address.
11. Execute the complete live lifecycle in `DEPLOYMENT.md`, including the real consumer call and finalized callback.
12. Fill `proof/LIVE_PROOF.md` only from actual finalized evidence.
13. Update README deployment status if appropriate.
14. Ensure repository contains no secrets, private keys, `.env`, caches or generated junk.
15. Commit and push the completed repository to `https://github.com/Ifem1/warrant` on `main`.

If current GenLayer tooling has changed since this package was generated, use current official syntax while keeping the contract semantics and security model unchanged.
