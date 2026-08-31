# Architecture

## Separation of authority, judgement and enforcement

Warrant deliberately splits the system into three layers.

### 1. Authority layer

A root grant is created by an explicit caller. This is the only place new authority originates.

A root grant includes semantic scope plus hard deterministic boundaries:

```text
scope
exact/wildcard consumer target
max per action
lifetime max total
expiry
```

The contract does not ask a model whether the root grant is sensible. The caller is the authority source.

### 2. Consensus layer

GenLayer consensus is used only where deterministic code cannot faithfully replace semantic judgement.

#### Delegation containment

A child can exist only after validators independently establish that the child scope is a semantic subset of the parent scope.

#### Action containment

A permit can exist only after validators independently establish that the requested action remains inside every semantic scope from the root through the requesting authority.

Both use a closed three-state result with `AMBIGUOUS` as a first-class fail-closed outcome.

### 3. Deterministic protocol layer

After consensus, ordinary deterministic logic controls:

- caller identity;
- delegation depth;
- target narrowing;
- per-action cap narrowing;
- total cap narrowing;
- expiry narrowing;
- lineage validity;
- cumulative exposure;
- permit bindings;
- revocation;
- consumption status.

## Authority graph

Each authority node points to exactly one parent, producing a forest of rooted delegation trees.

```text
Root A
├── A.1
│   ├── A.1.1
│   └── A.1.2
└── A.2

Root B
└── B.1
```

The contract bounds depth to `MAX_DEPTH = 8`, preventing unbounded lineage work.

## Chain hash

Every authority receives an immutable `chain_hash` derived from:

- its parent's chain hash;
- all addresses involved;
- scope hash;
- target;
- caps;
- expiry;
- depth.

This makes the leaf definition transitively commit to its ancestry without duplicating the full ancestor payload in a permit.

A permit stores the leaf chain hash at issuance. Authority definitions are immutable; revocation changes status, not the definition hash.

## Revocation model

Warrant does not rewrite descendants when an ancestor is revoked. Instead, effective validity is computed by traversing the lineage.

This gives three useful properties:

1. historical lineage remains auditable;
2. revoking a parent immediately invalidates every descendant;
3. revocation cost is bounded and independent of the number of descendants.

The root owner may revoke any node in its tree. A direct grantor may revoke the child authority it created.

## Exposure accounting

When a permit for amount `x` is issued, Warrant performs two deterministic passes over the lineage.

Pass 1 verifies every ancestor:

```text
x <= max_per_action
committed_total + x <= max_total
```

Only after every check passes does Pass 2 add `x` to every ancestor's `committed_total`.

This avoids partial mutation and prevents sibling authorities from collectively exceeding their root budget.

## Permit model

A permit is an immutable authorization record with mutable consumption status.

It binds:

```text
authority_id
requester
consumer
action_key
payload_hash
amount
explicit permit expiry
action_hash
authority chain hash
```

The semantic action description is retained for auditability but the consumer should bind the exact executable parameters through `payload_hash`.

## Consumer responsibility

GenLayer IC-to-IC writes are asynchronous. A consumer therefore cannot atomically make Warrant mark a permit consumed before its own state transition.

The safe composition pattern is:

```text
1. Warrant permit already exists and is finalized.
2. Consumer synchronously calls permit_valid_for().
3. Consumer checks its own used_permits map.
4. Consumer marks permit used locally.
5. Consumer performs protected state change.
6. Consumer emits record_consumption() on finalized.
```

This is why the consumer example includes local replay protection. Warrant's callback is audit/bookkeeping state, while the consumer's local guard is the atomic replay boundary for the protected action.
