# Composing With Warrant

## Typed interface

A consumer can define only the methods it needs:

```python
@gl.contract_interface
class IWarrant:
    class View:
        def permit_valid_for(
            self,
            permit_id: u256,
            consumer: Address,
            action_key: str,
            payload_hash: str,
            amount: u256,
        ) -> bool: ...

    class Write:
        def record_consumption(self, permit_id: u256, payload_hash: str) -> None: ...
```

## Safe execution pattern

A protected consumer should:

1. derive a deterministic payload hash from every material action parameter;
2. call `permit_valid_for` synchronously;
3. maintain its own `used_permits` map;
4. mark the permit used before the protected state transition;
5. perform the state transition;
6. emit `record_consumption` back to Warrant on `finalized`.

`examples/protected_treasury.py` implements exactly this pattern.

## Why the consumer needs a local replay map

A GenLayer write from one IC to another is an asynchronous internal message. The consumer cannot synchronously mutate Warrant and then continue in one atomic call.

The correct atomic boundary therefore lives in the consumer:

```text
validate Warrant permit (view)
        ↓
mark local permit used
        ↓
protected state transition
        ↓
finalized callback to Warrant
```

Warrant's `record_consumption` is idempotent and serves as shared bookkeeping/visibility after the consumer's finalized action.

## Payload binding

Do not use a vague action description as the only replay boundary.

For example, a treasury consumer should hash all executable parameters:

```text
recipient
amount
purpose / invoice / job ID
asset or method where relevant
```

Then the permit binds that digest.

## Target binding

If an authority is created with a non-zero `target`, neither descendants nor permits may escape that target.

Use target binding when a delegation should only ever authorize one known consumer IC.

Use zero target only when the semantic authority is deliberately portable across multiple consumer contracts.

## Read-only integrations

A contract can also use Warrant without consuming a permit, for example to display or gate state using:

- `authority_effective`;
- `remaining_total`;
- `get_authority`;
- `lineage`.

For consequential one-time actions, use permits plus consumer replay protection.
