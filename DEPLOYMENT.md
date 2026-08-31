# Deployment and Live Proof

The source package is prepared for deployment but intentionally does not contain fabricated addresses or transaction hashes.

## Prerequisites

```bash
python -m pip install -r requirements-dev.txt
python -m pip install genvm-linter
npm install -g genlayer
```

Select StudioNet and verify configuration:

```bash
genlayer config get
genlayer network studionet
```

## Pre-deployment gate

```bash
python scripts/preflight.py
python -m pytest -q

genvm-lint check contracts/warrant.py
genvm-lint typecheck contracts/warrant.py
genvm-lint schema contracts/warrant.py --output proof/warrant-schema.json

genvm-lint check examples/protected_treasury.py
genvm-lint typecheck examples/protected_treasury.py
```

Fix all contract-source errors before deployment. Do not weaken a security invariant merely to satisfy a tool; update the implementation without changing the intended authority model.

## Deploy Warrant

Use the current GenLayer CLI syntax available in the installed version. After deployment, record:

- deployed address;
- deployment transaction hash;
- finalized receipt status;
- exact source commit;
- source SHA-256.

## Deploy the consumer

Deploy `examples/protected_treasury.py` with the finalized Warrant address as its constructor argument.

Record its finalized deployment address and transaction hash separately.

## Required live lifecycle

Use funded test accounts representing:

- root owner;
- Agent A;
- Agent B;
- recipient/other test actor.

Use a short but still valid future expiry window.

### A. Root authority

Create a root grant similar to:

```text
Agent A may authorize cloud-compute purchases required for Project Atlas.
It may not authorize unrelated software, unrelated projects or customer-data disclosure.
```

Bind the target to the deployed `ProtectedTreasury` if practical.

Hard bounds example:

```text
max_per_action = 100
max_total = 500
```

### B. Valid child

As Agent A, delegate to Agent B:

```text
Agent B may authorize GPU-compute purchases required for Project Atlas model training.
```

Use narrower hard bounds, e.g.:

```text
max_per_action = 30
max_total = 120
```

Finalize and record the child authority ID.

### C. Expanded child rejection

Attempt a second delegation like:

```text
Agent B may authorize any software or infrastructure for any project.
```

Record the failed/undetermined transaction evidence showing that Warrant does not create expanded authority.

### D. Exact permit

From Agent B, derive the payload hash for one exact `ProtectedTreasury.execute` action and request a permit for that amount.

Finalize the permit before consumer use.

### E. Real cross-contract use

Call `ProtectedTreasury.execute(...)` with the exact parameters bound by the permit.

Verify:

- consumer state changes;
- the same permit cannot be replayed on that consumer;
- after finalized internal-message processing, `Warrant.get_permit` reports `CONSUMED`.

### F. Revocation propagation

Issue another valid descendant permit but do not use it.

Revoke the root authority.

Verify:

```text
authority_effective(child) == false
permit_valid_for(second_permit, ...) == false
```

This is the live proof that revocation propagates without rewriting descendants.

## Evidence discipline

Do not fill `proof/LIVE_PROOF.md` from memory. Copy transaction hashes and addresses from finalized CLI/Explorer receipts.

If StudioNet is unavailable, leave the proof explicitly incomplete rather than inventing evidence.
