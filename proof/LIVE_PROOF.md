# Warrant StudioNet Live Proof

**Status: COMPLETE LIVE LIFECYCLE VERIFIED.**

This file is intentionally blank of fabricated blockchain evidence. The finishing agent must replace the fields below only after successful finalized StudioNet execution.

## Source identity

- Repository: `https://github.com/Ifem1/warrant`
- Branch: `main`
- Source commit: `8757f1c`
- `contracts/warrant.py` SHA-256: `83870F93E24FBA37CADD5946BDFFF82E81006352BDF9B6C250C8060AF508973D`
- `examples/protected_treasury.py` SHA-256: `09C439BB688359823AAD7DBA6F060849AA19D15EE698328EFEBC864F3D6280EB`

## Validation

- GenVM lint Warrant: `PASSED in GitHub Actions run 33454584299`
- GenVM validate Warrant: `PASSED in GitHub Actions run 33454584299`
- GenVM typecheck Warrant: `PASSED in GitHub Actions run 33454584299`
- GenVM schema Warrant: `PASSED in GitHub Actions run 33454584299`
- GenVM lint consumer: `PASSED in GitHub Actions run 33454584299`
- Direct Mode tests: `35 passed, 1 skipped (unsupported address-based cross-contract Direct Mode) in GitHub Actions run 33454584299`
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

- Transaction: `0x03390c7b8844bad4ffe7e3cbbcf513fd87c31f27f82bff8225e1458826ab02a2`
- Root authority ID: `1`; root owner/delegate: `0x3926627eb9d353e29c7d6f8f914be96f38631bab`; target: zero; max_per_action: `100`; max_total: `500`; expiry: `4102444800`
- Finalized: `FINALIZED`

### Valid narrowed delegation

- Transaction: `0xe1843feb100b2be4428da13cf8449b7c2c36b20bd3132980e27aff28a5cb548d`
- Child authority ID: `3`; delegate: `0x1111111111111111111111111111111111111111`; parent/root: `1/1`; depth: `1`; caps: `30/120`; finalized: `FINALIZED`
- Additional active-account child: authority `4`, transaction `0xefdd75ed5709ba10f5f7c67a4a00109b2c6b92e5ae5b2fd5daa01c1116606d0f`; effective before revocation: `true`

### Expanded delegation rejected

- Transaction: `0xd16803a869bc86b82ff3ec9dfeb4ecf186e17281a8ad44a009e5aa18f5279cd3`
- Finalized fail-closed result: `EXPANDS_AUTHORITY:BROADER_PROJECT_AND_PURPOSE_SCOPE`; no expanded authority created

### Valid exact-action permit

- Transaction: `0xc9b9f5c88509ff34077b344153217e7cb965dca91581c4a18be29c3b6eb7e325`
- Permit IDs: `1` and `2`, finalized active; consumer: `0x5a0c97395a95d6cdf766313de3d218fa19b10915`; action: `TREASURY_TRANSFER`; amount: `25`; payload hash: `f488509e972eb90289eef53b6977c25fb748d76b5bc9032967fb3c93249553ab`; context hash: `3b384df1e00522bafc073f9cba746714ce481111367a58ce1a5ba95138c1ba2c`; action hash: `ec3b78fe04d7e4f4b7f6b8a2eef6164846f234fc2b2584bcb16b91785102c713`
- Canonical context equality: Warrant == ProtectedTreasury == stored permit: `3b384df1e00522bafc073f9cba746714ce481111367a58ce1a5ba95138c1ba2c`; finalized: `FINALIZED`

### Consumer executes through Warrant

- ProtectedTreasury transaction: `0x878e28373a5afa0d3ff86d927104a72d40dc5ef91ce2488128aba12c80e4e000`
- Action ID: `1`; permit ID: `1`; amount: `25`; payload hash: `f488509e972eb90289eef53b6977c25fb748d76b5bc9032967fb3c93249553ab`; total_executed: `25`; finalized: `FINALIZED`

### Finalized consumption callback

- Finalized receipt message: Warrant `record_consumption` callback; `get_permit(1)` shows `CONSUMED`, consumed_at `1788712616`

### Replay rejected

- Transaction: `0x9b3ea79e8d1bef8a11b4e9388d4234ecc31cb6e53be5f39f53d37a04aa061741`
- Finalized rejection: `permit already used by this consumer`

### Ancestor revoked

- Transaction: `0x9cbdf62fad2462679c2065d22a1ab78ea327f4f83e62b76d37798a9b58701534`
- Finalized: `FINALIZED`; `authority_effective(4) == false`

### Descendant/permit invalid after revocation

- `authority_effective(4)`: `false`; `permit_valid_for_context(2, ...)`: `false`
- ProtectedTreasury rejection: `0xab64b877edbfdaba46a2eac20bf6e89e366741dde05690122c9d25d752c81145`; finalized reason: `Warrant permit is not valid for this exact action`
- Revoked-branch permit rejection: `0x20dceb8b1aa924b39a56028ea8a175b7c73127e5a5f5e94a87bfe5ba286f332d`; finalized reason: `EXPECTED: authority is not effective`

## Explorer links

- Warrant: https://explorer-studio.genlayer.com/address/0xdF38185e0EA3bCb4779b3E56AB5eeeE7e63381De
- ProtectedTreasury: https://explorer-studio.genlayer.com/address/0x5a0c97395A95d6cDf766313de3D218FA19B10915
