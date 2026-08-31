# State Machines

## Authority

```text
             create_root / delegate
                     │
                     ▼
                  ACTIVE
                     │
               revoke by grantor
               or root owner
                     │
                     ▼
                  REVOKED
```

Expiry does not rewrite status. It changes **effective validity** dynamically.

An authority is effective only when every node in its lineage is:

```text
status == ACTIVE
and
expires_at == 0 or now < expires_at
```

## Permit

```text
request_permit
      │
      ▼
   ACTIVE
      │
record_consumption
(bound consumer only)
      │
      ▼
  CONSUMED
```

A permit can also become unusable without changing its stored status when:

- its explicit expiry passes;
- an ancestor authority expires;
- an ancestor authority is revoked.

This preserves historical state while preventing use.

## Delegation decision

```text
proposed child
      │
      ├─ deterministic bound widening ───────► REJECT
      │
      ▼
GenLayer semantic containment
      │
      ├─ EXPANDS_AUTHORITY ─────────────────► REJECT
      ├─ AMBIGUOUS ─────────────────────────► REJECT
      └─ VALID_SUBSET
              │
              ▼
         create child
```

## Permit decision

```text
requested action
      │
      ├─ wrong caller / target / expiry ─────► REJECT
      │
      ▼
GenLayer action containment
      │
      ├─ OUT_OF_SCOPE ───────────────────────► REJECT
      ├─ AMBIGUOUS ─────────────────────────► REJECT
      └─ WITHIN_SCOPE
              │
              ▼
validate every ancestor cap
              │
              ├─ any cap exceeded ──────────► REJECT
              ▼
commit exposure on lineage
              │
              ▼
          issue permit
```
