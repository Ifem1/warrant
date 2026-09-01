# Testing

## Direct Mode

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The suite contains 35 Direct Mode unit/adversarial tests plus one explicitly
skipped documentation test. Address-based cross-contract calls are not
supported by genlayer-test Direct Mode; cross-contract composition is proved
on StudioNet instead.

The suite is intended to cover:

- explicit root authority creation;
- access control;
- safe subset delegation;
- expanded/ambiguous delegation failure;
- deterministic limit/target/expiry narrowing;
- malicious leader disagreement for delegation;
- in-scope/out-of-scope/ambiguous action checks;
- malicious leader disagreement for action scope;
- transitive per-action ceilings;
- sibling sharing of root `max_total`;
- exact consumer/payload/amount binding;
- ancestor revocation invalidation;
- revocation access control;
- consumption caller binding;
- idempotent consumption;
- lineage hash integrity;
- pickling-safe storage.

## GenVM validation

Run all four checks on the primary contract:

```bash
genvm-lint lint contracts/warrant.py
genvm-lint validate contracts/warrant.py
genvm-lint typecheck contracts/warrant.py
genvm-lint schema contracts/warrant.py --output proof/warrant-schema.json
```

Then check the consumer:

```bash
genvm-lint lint examples/protected_treasury.py
genvm-lint validate examples/protected_treasury.py
genvm-lint typecheck examples/protected_treasury.py
```

## Repository preflight

```bash
python scripts/preflight.py
```

This is not a substitute for GenVM lint. It checks repository-level invariants that are easy to regress accidentally.

## Live StudioNet validation

Do not claim the submission is deployment-complete until `proof/LIVE_PROOF.md` contains finalized Warrant and consumer deployments plus the complete cross-contract lifecycle.
