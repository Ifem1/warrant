# Security Model

## Assets protected

Warrant protects delegated authority from accidental or malicious expansion.

The critical assets are:

- root authority intent;
- semantic scope boundaries;
- deterministic spending/exposure limits;
- target restrictions;
- expiry restrictions;
- revocation power;
- permit consumer/payload binding;
- downstream replay resistance.

## Threats and mitigations

### Malicious leader claims broader scope is a subset

**Mitigation:** validators independently classify containment and must agree on the verdict.

### Prompt injection inside authority text

**Mitigation:** prompts treat scope/action blocks as untrusted data; outputs are closed enums; deterministic caps cannot be overridden by prompt text.

### Child narrows prose but widens numeric limits

**Mitigation:** child caps are checked deterministically before semantic consensus can create the node.

### Child changes a parent-bound consumer target

**Mitigation:** a specific parent target cannot become wildcard or change address in a child.

### Child outlives a finite parent

**Mitigation:** finite parent expiry is a deterministic upper bound on child expiry.

### Sibling delegates oversubscribe a root

**Mitigation:** every permit commits amount on every ancestor, so all branches share ancestor capacity.

### Revoked parent leaves live children

**Mitigation:** `authority_effective` and `permit_valid_for` traverse the complete bounded lineage. No descendant can be effective while any ancestor is revoked or expired.

### Permit is reused against another contract

**Mitigation:** permits bind an exact consumer address. `permit_valid_for` checks it.

### Permit is reused with changed parameters

**Mitigation:** permits bind action key, payload hash and amount. The consumer derives `payload_hash` from the exact state transition parameters.

### Same permit is replayed on the correct consumer before Warrant receives the async callback

**Mitigation:** the consumer must maintain an atomic local `used_permits` map and set it before changing protected state. The included consumer does this.

### Finalized callback is delivered twice

**Mitigation:** `record_consumption` is idempotent.

### Caller forges consumption

**Mitigation:** only the exact bound consumer contract address can mark the permit consumed, and it must provide the pinned payload hash.

### Unbounded graph traversal

**Mitigation:** delegation depth is capped at eight.

## Intentional conservative choices

### Lifetime authorised exposure

Warrant does not refund `committed_total` when a permit expires unused. This trades capital/authority efficiency for simple safety: no external fact is required to decide whether capacity can be restored.

### Immutable authority definitions

Scopes, targets, limits and expiry are immutable. Modification is represented as a new delegation/root, not an in-place edit. This keeps old permits and lineage hashes auditable.

### No model-controlled slashing or funds

Warrant does not hold user funds, settle payments or slash actors. It publishes authority state and exact permits for consumer contracts to enforce.

## Cross-contract caveat

A consumer that does not implement local permit replay protection can misuse Warrant even if Warrant itself is correct. The safe consumer pattern is part of the primitive's integration contract and is demonstrated in `examples/protected_treasury.py`.
