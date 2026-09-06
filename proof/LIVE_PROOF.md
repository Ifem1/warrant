# Warrant StudioNet Live Proof

**Status: DEPLOYMENTS VERIFIED; LIFECYCLE INCOMPLETE.**

This file is intentionally blank of fabricated blockchain evidence. The finishing agent must replace the fields below only after successful finalized StudioNet execution.

## Source identity

- Repository: `https://github.com/Ifem1/warrant`
- Branch: `main`
- Source commit: `8757f1c`
- `contracts/warrant.py` SHA-256: `83870F93E24FBA37CADD5946BDFFF82E81006352BDF9B6C250C8060AF508973D`
- `examples/protected_treasury.py` SHA-256: `09C439BB688359823AAD7DBA6F060849AA19D15EE698328EFEBC864F3D6280EB`

## Validation

- GenVM lint Warrant: `PASSED in GitHub Actions run 33440491196`
- GenVM validate Warrant: `PASSED in GitHub Actions run 33454584299`
- GenVM typecheck Warrant: `PASSED in GitHub Actions run 33454584299`
- GenVM schema Warrant: `PASSED in GitHub Actions run 33454584299`
- GenVM lint consumer: `PASSED in GitHub Actions run 33454584299`
- Direct Mode tests: `35 passed, 1 skipped in GitHub Actions run 33454584299`
- Repository preflight: `25 passed, 0 failed in GitHub Actions run 33454584299`

## Deployments

### Warrant

- Address: `0xdF38185e0EA3bCb4779b3E56AB5eeeE7e63381De`
- Deployment transaction: `0xfbd0275f2720eed097f874523bb2426ba0ec757f030608467b90add207325620`
- Finalized status: `FINALIZED`

### ProtectedTreasury

- Address: `0x5a0c97395A95d6cDf766313de3D218FA19B10915`
- Deployment transaction: `0x453df80dfde0f9e78ace906ea186564f235304a251363cdeae13347fcd58bdf7`
- Finalized status: `FINALIZED`

## Lifecycle receipts

### Root authority created

- Transaction: `PENDING`
- Root authority ID: `PENDING`
- Finalized: `PENDING`

### Valid narrowed delegation

- Transaction: `PENDING`
- Child authority ID: `PENDING`
- Finalized: `PENDING`

### Expanded delegation rejected

- Transaction/evidence: `PENDING`
- Observed result: `PENDING`

### Valid exact-action permit

- Transaction: `PENDING`
- Permit ID: `PENDING`
- Finalized: `PENDING`

### Consumer executes through Warrant

- ProtectedTreasury transaction: `PENDING`
- Action ID: `PENDING`
- Consumer state after: `PENDING`
- Finalized: `PENDING`

### Finalized consumption callback

- Child/internal transaction or receipt evidence: `PENDING`
- Warrant permit status after: `PENDING`

### Replay rejected

- Transaction/evidence: `PENDING`
- Observed result: `PENDING`

### Ancestor revoked

- Transaction: `PENDING`
- Finalized: `PENDING`

### Descendant/permit invalid after revocation

- `authority_effective(child)`: `PENDING`
- `permit_valid_for(second permit, ...)`: `PENDING`
- Evidence: `PENDING`

## Explorer links

- Warrant: https://genlayer-explorer.vercel.app/address/0xdF38185e0EA3bCb4779b3E56AB5eeeE7e63381De
- ProtectedTreasury: https://genlayer-explorer.vercel.app/address/0x5a0c97395A95d6cDf766313de3D218FA19B10915
