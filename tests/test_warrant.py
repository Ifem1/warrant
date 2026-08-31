import importlib.util
import json

ZERO = "0x0000000000000000000000000000000000000000"
FUTURE = 4102444800  # 2100-01-01
FAR_FUTURE = 4133980800  # 2101-01-01
HASH_A = "a" * 64
HASH_B = "b" * 64

ROOT_SCOPE = (
    "The delegate may purchase cloud compute required for Project Atlas. "
    "The delegate may not purchase unrelated software, transfer customer data, "
    "or spend for any purpose outside Project Atlas infrastructure."
)
GPU_SCOPE = "The delegate may purchase GPU compute required for Project Atlas model training."
STORAGE_SCOPE = "The delegate may purchase object storage required for Project Atlas backups."
EXPANDED_SCOPE = "The delegate may purchase any software or infrastructure for any project."


def subset(verdict="VALID_SUBSET", reason="MATERIAL_SCOPE_CONTAINED"):
    return {"verdict": verdict, "reason_code": reason}


def action(verdict="WITHIN_SCOPE", reason="ACTION_MATCHES_GRANTED_PURPOSE"):
    return {"verdict": verdict, "reason_code": reason}


def address_text(value):
    return "0x" + bytes(value).hex()


def deploy_root(direct_deploy, direct_owner, target=ZERO, total=500, per_action=100, expiry=FUTURE):
    contract = direct_deploy("contracts/warrant.py", sdk_version="v0.2.12")
    root_id = contract.create_root(direct_owner, ROOT_SCOPE, target, per_action, total, expiry)
    return contract, root_id


def delegate_gpu(direct_vm, contract, root_id, delegate, target=ZERO, total=120, per_action=30, expiry=FUTURE):
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset())
    return contract.delegate(root_id, delegate, GPU_SCOPE, target, per_action, total, expiry)


def request_gpu_permit(direct_vm, contract, authority_id, consumer, amount=25, payload_hash=HASH_A, expiry=FUTURE):
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action())
    return contract.request_permit(
        authority_id,
        consumer,
        "TREASURY_TRANSFER",
        payload_hash,
        "Purchase GPU compute from the approved infrastructure provider for Project Atlas model training.",
        amount,
        expiry,
    )


def test_create_root_is_explicit_authority_not_ai_judgement(direct_deploy, direct_owner):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    root = contract.get_authority(root_id)
    assert root["parent_id"] == 0
    assert root["root_id"] == root_id
    assert root["delegate"].lower() == address_text(direct_owner)
    assert root["scope"] == ROOT_SCOPE
    assert root["status_name"] == "ACTIVE"
    assert root["committed_total"] == 0
    assert len(root["scope_hash"]) == 64
    assert len(root["chain_hash"]) == 64


def test_root_rejects_zero_delegate(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/warrant.py", sdk_version="v0.2.12")
    with direct_vm.expect_revert("delegate cannot be the zero address"):
        contract.create_root(ZERO, ROOT_SCOPE, ZERO, 100, 500, FUTURE)


def test_root_rejects_invalid_limits(direct_vm, direct_deploy, direct_owner):
    contract = direct_deploy("contracts/warrant.py", sdk_version="v0.2.12")
    with direct_vm.expect_revert("max_per_action cannot exceed max_total"):
        contract.create_root(direct_owner, ROOT_SCOPE, ZERO, 501, 500, FUTURE)


def test_valid_semantic_subset_creates_child(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    child = contract.get_authority(child_id)
    assert child["parent_id"] == root_id
    assert child["root_id"] == root_id
    assert child["depth"] == 1
    assert child["delegate"].lower() == address_text(direct_alice)
    assert child["max_per_action"] == 30
    assert child["max_total"] == 120
    assert len(contract.lineage(child_id)) == 2


def test_only_current_delegate_can_subdelegate(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("only the current delegate may sub-delegate"):
            contract.delegate(root_id, direct_bob, GPU_SCOPE, ZERO, 30, 120, FUTURE)


def test_expanding_semantic_scope_is_rejected(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset("EXPANDS_AUTHORITY", "PURPOSE_BROADENED"))
    with direct_vm.expect_revert("EXPANDS_AUTHORITY"):
        contract.delegate(root_id, direct_alice, EXPANDED_SCOPE, ZERO, 30, 120, FUTURE)


def test_ambiguous_delegation_fails_closed(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset("AMBIGUOUS", "UNCLEAR_PERMISSION_BOUNDARY"))
    with direct_vm.expect_revert("AMBIGUOUS"):
        contract.delegate(root_id, direct_alice, "Handle whatever infrastructure seems reasonable.", ZERO, 30, 120, FUTURE)


def test_child_cannot_widen_per_action_cap(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner, per_action=100)
    with direct_vm.expect_revert("child per-action cap expands parent authority"):
        contract.delegate(root_id, direct_alice, GPU_SCOPE, ZERO, 101, 120, FUTURE)


def test_child_cannot_widen_total_cap(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner, total=500)
    with direct_vm.expect_revert("child total cap expands parent authority"):
        contract.delegate(root_id, direct_alice, GPU_SCOPE, ZERO, 30, 501, FUTURE)


def test_child_cannot_outlive_parent(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner, expiry=FUTURE)
    with direct_vm.expect_revert("child expiry expands parent authority"):
        contract.delegate(root_id, direct_alice, GPU_SCOPE, ZERO, 30, 120, FAR_FUTURE)


def test_child_cannot_broaden_specific_target(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, direct_charlie):
    contract, root_id = deploy_root(direct_deploy, direct_owner, target=direct_bob)
    with direct_vm.expect_revert("child target expands parent authority"):
        contract.delegate(root_id, direct_alice, GPU_SCOPE, direct_charlie, 30, 120, FUTURE)


def test_wildcard_parent_can_be_narrowed_to_specific_target(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner, target=ZERO)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice, target=direct_bob)
    assert contract.get_authority(child_id)["target"].lower() == address_text(direct_bob)


def test_validator_rejects_malicious_subset_claim(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset("VALID_SUBSET"))
    contract.delegate(root_id, direct_alice, EXPANDED_SCOPE, ZERO, 30, 120, FUTURE)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / INDEPENDENTLY CLASSIFY DELEGATION SUBSET", subset("EXPANDS_AUTHORITY"))
    assert direct_vm.run_validator() is False


def test_validator_accepts_matching_subset_decision(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset("VALID_SUBSET"))
    contract.delegate(root_id, direct_alice, GPU_SCOPE, ZERO, 30, 120, FUTURE)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / INDEPENDENTLY CLASSIFY DELEGATION SUBSET", subset("VALID_SUBSET", "SAME_RESULT_DIFFERENT_REASON"))
    assert direct_vm.run_validator() is True


def test_delegate_can_request_in_scope_permit(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        permit_id = request_gpu_permit(direct_vm, contract, child_id, direct_bob, amount=25)
    permit = contract.get_permit(permit_id)
    assert permit["authority_id"] == child_id
    assert permit["consumer"].lower() == address_text(direct_bob)
    assert permit["amount"] == 25
    assert permit["status_name"] == "ACTIVE"
    assert len(permit["action_hash"]) == 64
    assert contract.remaining_total(child_id) == 95
    assert contract.remaining_total(root_id) == 475


def test_only_leaf_delegate_can_request_permit(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action())
    with direct_vm.expect_revert("only the current delegate may request a permit"):
        contract.request_permit(child_id, direct_bob, "TREASURY_TRANSFER", HASH_A, "Buy GPU compute for Atlas.", 25, FUTURE)


def test_out_of_scope_action_is_rejected(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action("OUT_OF_SCOPE", "UNRELATED_PURPOSE"))
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("OUT_OF_SCOPE"):
            contract.request_permit(child_id, direct_bob, "BUY_LAPTOPS", HASH_A, "Buy laptops for an unrelated marketing team.", 25, FUTURE)


def test_ambiguous_action_is_rejected(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action("AMBIGUOUS", "UNCLEAR_PURPOSE"))
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("AMBIGUOUS"):
            contract.request_permit(child_id, direct_bob, "PURCHASE", HASH_A, "Buy whatever compute seems useful.", 25, FUTURE)


def test_action_validator_rejects_false_within_scope(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action("WITHIN_SCOPE"))
    with direct_vm.prank(direct_alice):
        contract.request_permit(child_id, direct_bob, "BUY_LAPTOPS", HASH_A, "Buy laptops for an unrelated marketing team.", 25, FUTURE)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / INDEPENDENTLY CLASSIFY ACTION SCOPE", action("OUT_OF_SCOPE"))
    assert direct_vm.run_validator() is False


def test_per_action_cap_is_enforced_across_ancestors(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner, per_action=100)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice, per_action=30)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action())
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("ancestor per-action cap"):
            contract.request_permit(child_id, direct_bob, "TREASURY_TRANSFER", HASH_A, "Buy GPU compute for Atlas.", 31, FUTURE)


def test_sibling_delegates_share_root_budget(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner, total=50, per_action=50)
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset())
    first = contract.delegate(root_id, direct_alice, GPU_SCOPE, ZERO, 40, 50, FUTURE)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset())
    second = contract.delegate(root_id, direct_alice, STORAGE_SCOPE, ZERO, 40, 50, FUTURE)

    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        request_gpu_permit(direct_vm, contract, first, direct_bob, amount=30, payload_hash=HASH_A)
    assert contract.remaining_total(root_id) == 20

    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action())
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("remaining authority budget"):
            contract.request_permit(second, direct_bob, "STORAGE_PURCHASE", HASH_B, "Purchase Atlas backup object storage.", 25, FUTURE)


def test_payload_hash_binds_exact_action(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        permit_id = request_gpu_permit(direct_vm, contract, child_id, direct_bob)
    context_hash = contract.get_permit(permit_id)["action_context_hash"]
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_A, context_hash, 25) is True
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_B, context_hash, 25) is False


def test_consumer_target_binding_is_exact(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, direct_charlie):
    contract, root_id = deploy_root(direct_deploy, direct_owner, target=direct_bob)
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset())
    child_id = contract.delegate(root_id, direct_alice, GPU_SCOPE, direct_bob, 30, 120, FUTURE)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action())
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("consumer is outside"):
            contract.request_permit(child_id, direct_charlie, "TREASURY_TRANSFER", HASH_A, "Buy GPU compute for Atlas.", 25, FUTURE)


def test_root_revocation_invalidates_descendant_and_existing_permit(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        permit_id = request_gpu_permit(direct_vm, contract, child_id, direct_bob)
    assert contract.authority_effective(child_id) is True
    context_hash = contract.get_permit(permit_id)["action_context_hash"]
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_A, context_hash, 25) is True
    contract.revoke(root_id)
    assert contract.authority_effective(child_id) is False
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_A, contract.get_permit(permit_id)["action_context_hash"], 25) is False


def test_semantic_context_cannot_misrepresent_bound_payload(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        permit_id = request_gpu_permit(direct_vm, contract, child_id, direct_bob)
    context_hash = contract.get_permit(permit_id)["action_context_hash"]
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_A, context_hash, 25) is True
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_B, context_hash, 25) is False
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_A, "0" * 64, 25) is False
    assert contract.permit_valid_for_context(permit_id, direct_bob, "OTHER_ACTION", HASH_A, context_hash, 25) is False


def test_context_binding_changes_with_semantic_inputs(direct_deploy, direct_owner, direct_bob, direct_alice):
    contract, _ = deploy_root(direct_deploy, direct_owner)
    base = contract.action_commitment(direct_bob, "TREASURY_TRANSFER", HASH_A, HASH_A, 25)
    changed_consumer = contract.action_commitment(direct_alice, "TREASURY_TRANSFER", HASH_A, HASH_A, 25)
    assert base != changed_consumer


def test_cli_string_and_dict_contexts_have_same_canonical_hash(direct_deploy, direct_owner):
    contract, _ = deploy_root(direct_deploy, direct_owner)
    context_dict = {"purpose": " purchase GPU   compute for Project Atlas ", "recipient": "0xf8c03f1e5f6e6cee945a9b37807924d70e2a9c5f", "amount": 25, "action": "treasury_transfer"}
    context_string = '{"action":"TREASURY_TRANSFER","amount":25,"purpose":"purchase GPU compute for Project Atlas","recipient":"0xf8c03f1e5f6e6cee945a9b37807924d70e2a9c5f"}'
    assert contract.action_context_hash_for(context_dict) == contract.action_context_hash_for(context_string)


def test_intermediate_grantor_can_revoke_its_child(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"WARRANT / CLASSIFY DELEGATION SUBSET", subset())
    with direct_vm.prank(direct_alice):
        grandchild_id = contract.delegate(child_id, direct_bob, "Purchase NVIDIA GPU compute for Atlas training only.", ZERO, 20, 60, FUTURE)
        contract.revoke(grandchild_id)
    assert contract.get_authority(grandchild_id)["status_name"] == "REVOKED"


def test_unrelated_account_cannot_revoke(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("caller cannot revoke"):
            contract.revoke(child_id)


def test_only_bound_consumer_can_record_consumption(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob, direct_charlie):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        permit_id = request_gpu_permit(direct_vm, contract, child_id, direct_bob)
    with direct_vm.prank(direct_charlie):
        with direct_vm.expect_revert("only the bound consumer"):
            contract.record_consumption(permit_id, HASH_A)


def test_consumption_is_idempotent_and_disables_permit(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        permit_id = request_gpu_permit(direct_vm, contract, child_id, direct_bob)
    with direct_vm.prank(direct_bob):
        contract.record_consumption(permit_id, HASH_A)
        contract.record_consumption(permit_id, HASH_A)
    assert contract.get_permit(permit_id)["status_name"] == "CONSUMED"
    assert contract.permit_valid_for_context(permit_id, direct_bob, "TREASURY_TRANSFER", HASH_A, contract.get_permit(permit_id)["action_context_hash"], 25) is False


def test_consumption_rejects_wrong_payload_hash(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    direct_vm.clear_mocks()
    with direct_vm.prank(direct_alice):
        permit_id = request_gpu_permit(direct_vm, contract, child_id, direct_bob)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("payload hash does not match"):
            contract.record_consumption(permit_id, HASH_B)


def test_action_commitment_changes_when_any_bound_field_changes(direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, _ = deploy_root(direct_deploy, direct_owner)
    base = contract.action_commitment(direct_bob, "TREASURY_TRANSFER", HASH_A, HASH_A, 25)
    assert base != contract.action_commitment(direct_bob, "TREASURY_TRANSFER", HASH_B, HASH_A, 25)
    assert base != contract.action_commitment(direct_bob, "TREASURY_TRANSFER", HASH_A, HASH_B, 25)
    assert base != contract.action_commitment(direct_bob, "TREASURY_TRANSFER", HASH_A, HASH_A, 26)
    assert base != contract.action_commitment(direct_alice, "TREASURY_TRANSFER", HASH_A, HASH_A, 25)


def test_lineage_hashes_pin_every_definition(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    child_id = delegate_gpu(direct_vm, contract, root_id, direct_alice)
    lineage = contract.lineage(child_id)
    assert lineage[0]["authority_id"] == child_id
    assert lineage[1]["authority_id"] == root_id
    assert lineage[0]["chain_hash"] != lineage[1]["chain_hash"]
    assert len(lineage[0]["chain_hash"]) == 64


def test_pickling_safe_state(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm.check_pickling = True
    contract, root_id = deploy_root(direct_deploy, direct_owner)
    delegate_gpu(direct_vm, contract, root_id, direct_alice)
    assert contract.get_authority(root_id)["status_name"] == "ACTIVE"


def test_protected_treasury_uses_real_warrant_boundary(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    warrant, root_id = deploy_root(direct_deploy, direct_owner)
    import genlayer.gl.genvm_contracts as genvm_contracts
    from genlayer.py import calldata
    from genlayer.py.public_abi import ResultCode

    child_id = delegate_gpu(direct_vm, warrant, root_id, direct_alice)
    direct_vm.clear_mocks()
    # gltest's SDK registry is process-global and normally allows one contract
    # class; clear only that harness registry to model two deployed instances.
    genvm_contracts.__known_contract__ = None
    treasury = direct_deploy("examples/protected_treasury.py", warrant.address, sdk_version="v0.2.12")
    recipient = direct_owner
    amount = 25
    purpose = "Purchase GPU compute from the approved infrastructure provider for Project Atlas model training."
    action_context = json.dumps({
        "action": "TREASURY_TRANSFER",
        "recipient": str(recipient).lower(),
        "amount": amount,
        "purpose": " ".join(purpose.strip().split()),
    }, sort_keys=True, separators=(",", ":"))
    payload_hash = treasury.payload_hash_for(recipient, amount, purpose)
    assert warrant.action_context_hash_for(action_context) == treasury.action_context_hash_for(recipient, amount, purpose)
    direct_vm.mock_llm(r"WARRANT / CLASSIFY ACTION SCOPE", action("WITHIN_SCOPE"))
    with direct_vm.prank(direct_alice):
        permit_id = warrant.request_permit(child_id, treasury.address, "TREASURY_TRANSFER", payload_hash, action_context, amount, FUTURE)
    permit = warrant.get_permit(permit_id)
    assert permit["consumer"].lower() == str(treasury.address).lower()
    assert permit["payload_hash"] == payload_hash
    assert permit["action_context_hash"] == treasury.action_context_hash_for(recipient, amount, purpose)
    warrant_address = warrant.address.as_bytes

    def subvm_return(value):
        return bytes([int(ResultCode.RETURN)]) + calldata.encode(value)

    def resolve_call(vm, request):
        call = request.get("CallContract") or request.get("PostMessage")
        if call is None or call["address"].as_bytes != warrant_address:
            return None
        method = str(call["calldata"]["method"])
        args = call["calldata"].get("args", [])
        if method == "permit_valid_for_context":
            return subvm_return(warrant.permit_valid_for_context(*args))
        if method == "record_consumption":
            with vm.prank(treasury.address):
                warrant.record_consumption(*args)
            return subvm_return(None)
        raise AssertionError(f"unexpected Warrant method: {method}")

    direct_vm._gl_call_hook = resolve_call
    with direct_vm.prank(direct_bob):
        action_id = treasury.execute(permit_id, recipient, amount, purpose)
    assert treasury.get_action(action_id)["permit_id"] == permit_id
    assert treasury.total_executed() == amount
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("permit already used by this consumer"):
            treasury.execute(permit_id, recipient, amount, purpose)
    assert warrant.get_permit(permit_id)["status_name"] == "CONSUMED"
