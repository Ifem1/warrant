# Consensus Design

Warrant uses GenLayer consensus for semantic containment, not for objective protocol mechanics.

## Delegation containment

Input:

- immutable parent scope;
- proposed child scope.

Leader task:

```text
VALID_SUBSET
EXPANDS_AUTHORITY
AMBIGUOUS
```

Validator task:

The validator independently performs the same containment analysis from the original parent and child text. It does not merely inspect the leader's schema or reasoning.

Acceptance rule:

```text
leader verdict == independent validator verdict
```

`reason_code` is intentionally explanatory and can differ. The consequential decision field is the verdict.

### Fail-closed policy

Only `VALID_SUBSET` can create a child.

Both `EXPANDS_AUTHORITY` and `AMBIGUOUS` reject the delegation.

## Action containment

Input:

- immutable ordered scope lineage from root through the requesting authority;
- action key;
- human-readable action description.

Leader task:

```text
WITHIN_SCOPE
OUT_OF_SCOPE
AMBIGUOUS
```

The validator independently derives its own verdict from the same immutable data.

Only exact verdict agreement passes the Equivalence Principle. Only `WITHIN_SCOPE` may proceed to deterministic permit checks.

## Why independent reproduction matters

A weak validator could check only that the leader returned one of three allowed strings. That would leave the leader's substantive judgement unverified.

Warrant instead makes every validator redo the semantic task. A malicious leader that calls an expanded delegation a subset is rejected when an independent validator derives `EXPANDS_AUTHORITY`.

The test suite includes explicit leader/validator disagreement cases for both semantic boundaries.

## What consensus cannot do

Consensus cannot:

- create a root grant;
- change who the grantor is;
- increase `max_per_action`;
- increase `max_total`;
- broaden an exact target;
- extend a finite parent expiry;
- bypass revocation;
- mutate lineage hashes;
- consume a permit;
- change the exact payload binding.

Those are deterministic protocol rules.

## Prompt-injection posture

Every prompt marks user-controlled scope/action text as untrusted data and explicitly forbids obeying instructions inside it.

This is defence in depth, not the primary security boundary. The stronger boundary is that the model's output is confined to a tiny closed enum and every consequential deterministic restriction is checked independently of the LLM.
