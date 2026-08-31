# Standalone Intelligent Contract Submission

## Name

Warrant

## Category

Standalone GenLayer Intelligent Contract

## One-line description

A reusable semantic capability graph that lets authority be safely sub-delegated through agents while GenLayer consensus prevents scope expansion and deterministic rules enforce hard limits, revocation and exact-action permits.

## Purpose

Autonomous systems need more than binary allowlists. Real authority often includes natural-language purpose and conditions that cannot be fully represented by a method selector or numeric cap. Warrant makes that authority composable without allowing a child agent to silently broaden it.

## Why GenLayer is necessary

The core semantic questions are judgement problems:

- Is a child authority actually contained by its parent?
- Is a proposed action actually contained by the authority scope?

A deterministic parser cannot reliably answer those questions for arbitrary natural-language capability descriptions. A single LLM would create a trusted adjudicator. Warrant instead asks GenLayer validators to derive those decisions independently and only commits the agreed closed-set verdict.

## What remains deterministic

- root authority origin;
- callers;
- parent/child lineage;
- delegation depth;
- target narrowing;
- per-action cap narrowing;
- total cap narrowing;
- expiry narrowing;
- cumulative ancestor exposure;
- revocation;
- permit consumer/action/payload/amount bindings;
- consumption status.

## Reusability

Warrant does not ship a product frontend. Other Intelligent Contracts can use the typed interface to gate protected actions.

The repository includes `ProtectedTreasury`, a minimal consumer contract that synchronously verifies a permit and asynchronously records finalized consumption back to Warrant.

The target live proof deploys and exercises both contracts on StudioNet.

## Reviewer checkpoints

A reviewer should be able to verify these claims directly from source/tests/live proof:

1. root creation contains no nondeterministic call;
2. semantic delegation uses independent validator derivation;
3. ambiguous or expanded delegation cannot create authority;
4. numeric/target/expiry widening fails deterministically;
5. sibling permits share ancestor budget;
6. ancestor revocation invalidates descendants without rewriting them;
7. permits bind an exact consumer and payload;
8. the consumer uses local replay protection before its state transition;
9. consumption messages use `on="finalized"` and Warrant handles duplicates idempotently;
10. live cross-contract composition is demonstrated with finalized evidence.

## Deployment status

See `proof/LIVE_PROOF.md`. No address or transaction hash should be claimed before an actual finalized StudioNet deployment.
