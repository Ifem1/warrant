# Warrant

**A reusable GenLayer authority primitive for safe semantic delegation.**

Warrant lets an authority holder delegate a bounded natural-language capability through multiple agents or contracts without allowing any child to silently acquire more power than its parent.

It is intentionally a **standalone Intelligent Contract, not a dApp**. There is no frontend. The reusable output is on-chain authority and permit state that other Intelligent Contracts can consume directly.

## The problem

Deterministic capability systems work well when every permission can be encoded as an exact method, address and number. Agentic workflows often contain a second layer that is harder to encode:

> "May purchase cloud compute required for Project Atlas, but may not spend for unrelated software or disclose customer data."

A root authority can be explicit, but safe sub-delegation requires judgement. A child description may narrow the authority, broaden it, weaken a condition, or be too ambiguous to trust.

Warrant separates these responsibilities:

- **Humans/contracts grant authority.** GenLayer never invents or grants root authority.
- **GenLayer consensus judges containment.** Validators independently decide whether a child scope is a true semantic subset of its parent.
- **GenLayer consensus judges requested use.** Validators independently decide whether a proposed action is inside every cumulative semantic scope in the active delegation lineage.
- **Deterministic code enforces hard safety rails.** Amount caps, cumulative exposure, target binding, expiry, delegation depth, revocation and replay protection do not depend on an LLM.

## Core lifecycle

```text
root owner
   │ explicit grant
   ▼
Authority #1
   │ semantic subset + deterministic narrowing
   ▼
Authority #2
   │ semantic subset + deterministic narrowing
   ▼
Authority #3
   │ request exact-action permit
   ▼
Permit #1 ──────────────► Protected consumer IC
                              │
                              ├─ synchronous permit validation
                              ├─ local replay guard
                              ├─ protected state transition
                              └─ finalized consumption message
                                      │
                                      ▼
                                  Warrant
```

Revoking any ancestor immediately makes every descendant authority and every still-active descendant permit ineffective through lineage validation. Historical records remain intact.

## Why this is not an "AI decides permission" wrapper

The LLM cannot create authority, increase a cap, select a target, extend expiry, waive a restriction, spend a budget, revoke a grant, or execute the downstream action.

Consensus is deliberately limited to two bounded semantic questions:

1. `VALID_SUBSET | EXPANDS_AUTHORITY | AMBIGUOUS`
2. `WITHIN_SCOPE | OUT_OF_SCOPE | AMBIGUOUS`

Everything with an objective representation is deterministic.

## Main state

### Authority

Each node commits to:

- root and parent IDs;
- root owner, grantor and delegate;
- immutable natural-language scope and `scope_hash`;
- optional exact target contract (`0x0` means unrestricted at that layer);
- `max_per_action`;
- lifetime `max_total` authorised exposure;
- cumulative `committed_total`;
- expiry;
- depth;
- status;
- immutable transitive `chain_hash`.

### Permit

Each permit binds:

- one authority node;
- one requester;
- one consumer contract;
- one action key;
- one payload hash;
- one amount;
- one explicit expiry;
- one immutable action hash;
- the authority chain hash that existed at issuance.

A consumer must validate all of those exact fields.

## Budget semantics

`max_total` is intentionally a **lifetime authorised-exposure ceiling**, not an account balance. Issuing a permit commits that amount on the leaf and every ancestor. Sibling delegates therefore share their ancestors' remaining capacity.

Warrant does **not** release committed capacity if a permit later expires unused. This is conservative by design: the primitive never needs to decide whether an external action really happened in order to remain safe. Applications that want replenishing budgets can create a new root authority or layer a settlement/accounting contract around Warrant.

## Consensus design

Warrant uses `gl.vm.run_nondet_unsafe` with independent validator derivation.

For delegation:

```text
leader:      compare parent scope vs child scope
validator:   independently compare the same immutable scopes
agreement:   verdict must match exactly
```

For permits:

```text
leader:      compare all lineage scopes vs requested action
validator:   independently compare the same immutable scope/action
agreement:   verdict must match exactly
```

Reason strings are explanatory only and are not used to manufacture consensus.

Ambiguity fails closed.

See [`docs/CONSENSUS.md`](docs/CONSENSUS.md).

## Cross-contract composition

[`examples/protected_treasury.py`](examples/protected_treasury.py) is a real consumer contract, not frontend code. It:

1. computes a payload commitment for its exact requested transition;
2. calls `Warrant.permit_valid_for(...)` synchronously;
3. rejects a wrong consumer, action key, payload, amount, expired/revoked lineage or consumed permit;
4. marks the permit locally used before changing state;
5. performs its protected ledger transition;
6. emits `record_consumption(...)` back to Warrant **on finalization**.

The consumption callback is idempotent so repeated finalized delivery is harmless.

See [`docs/COMPOSITION.md`](docs/COMPOSITION.md).

## Public methods

### Writes

- `create_root(...)`
- `delegate(...)`
- `revoke(...)`
- `request_permit(...)`
- `record_consumption(...)`

### Views

- `authority_effective(...)`
- `remaining_total(...)`
- `action_commitment(...)`
- `permit_valid_for(...)`
- `get_authority(...)`
- `get_permit(...)`
- `lineage(...)`

## Security invariants

The implementation is designed around these invariants:

1. **Authority originates explicitly.** Root creation does not call an LLM.
2. **Delegation can only narrow.** Semantic containment and deterministic bounds both have to pass.
3. **Hard limits are transitive.** Every permit must fit every ancestor's per-action and total ceilings.
4. **Sibling spend cannot bypass the root budget.** Permit issuance increments `committed_total` on the full lineage.
5. **Revocation is transitive without rewriting history.** Effective validity traverses the lineage at read/use time.
6. **Permits bind an exact consumer and exact payload.** A permit for one consumer/action cannot be replayed against another.
7. **Consumers own atomic replay prevention.** The consumer marks a permit used before its protected state transition.
8. **Consumption callbacks are idempotent.** Finalized internal-message duplication does not double-consume.
9. **No nondeterministic side effects.** Storage changes and contract calls occur outside nondeterministic blocks.
10. **Ambiguity never expands power.** `AMBIGUOUS` is a rejection outcome.

See [`docs/SECURITY.md`](docs/SECURITY.md).

## Tests

The Direct Mode suite covers root grants, semantic containment, validator disagreement, deterministic narrowing, target restrictions, ancestor budgets, sibling aggregation, revocation, exact permit binding, consumption and idempotence.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Before deployment:

```bash
genvm-lint check contracts/warrant.py
genvm-lint typecheck contracts/warrant.py
genvm-lint schema contracts/warrant.py --output proof/warrant-schema.json

genvm-lint check examples/protected_treasury.py
genvm-lint typecheck examples/protected_treasury.py

python scripts/preflight.py
```

The repository includes CI that runs the same static/preflight and Direct Mode checks.

## StudioNet proof target

The submission is not complete until the live proof demonstrates **both contracts**:

1. deploy Warrant;
2. deploy `ProtectedTreasury` with the Warrant address;
3. create a broad-but-bounded root grant;
4. create a narrower child delegation;
5. prove an attempted expanded child is rejected;
6. issue a valid exact-action permit;
7. have `ProtectedTreasury` consume it in a finalized transaction;
8. show the Warrant permit eventually becomes `CONSUMED` through the finalized callback;
9. prove replay fails;
10. revoke the ancestor and prove a second descendant permit becomes invalid.

Record the finalized addresses and transaction hashes in [`proof/LIVE_PROOF.md`](proof/LIVE_PROOF.md).

## Repository boundary

This repo deliberately contains **no frontend, wallet flow, product dashboard or application UI**. The deliverable is the reusable authority primitive, its tests, its consumer contract and reproducible deployment evidence.

## Licence

MIT
