# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""Minimal live-composition consumer for Warrant.

This example intentionally performs a consequential state transition rather than
being a frontend or mock wrapper.  It verifies a Warrant permit synchronously,
marks the permit as used locally to prevent replay, updates its protected ledger,
and emits a finalized consumption message back to Warrant.
"""

from genlayer import *

import json
from dataclasses import dataclass


ACTION_KEY = "TREASURY_TRANSFER"
MAX_PURPOSE_LEN = 320


@gl.contract_interface
class IWarrant:
    class View:
        def permit_valid_for_context(
            self,
            permit_id: u256,
            consumer: Address,
            action_key: str,
            payload_hash: str,
            action_context_hash: str,
            amount: u256,
        ) -> bool: ...

    class Write:
        def record_consumption(self, permit_id: u256, payload_hash: str) -> None: ...


@allow_storage
@dataclass
class ExecutedAction:
    action_id: u256
    permit_id: u256
    recipient: Address
    amount: u256
    purpose: str
    payload_hash: str


def hash_payload(recipient: Address, amount: u256, purpose: str) -> str:
    payload = {
        "recipient": str(recipient).lower(),
        "amount": int(amount),
        "purpose": " ".join(str(purpose).strip().split()),
    }
    return Keccak256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def canonical_action_context(recipient: Address, amount: u256, purpose: str) -> str:
    payload = {"action": ACTION_KEY, "recipient": str(recipient).lower(), "amount": int(amount), "purpose": " ".join(str(purpose).strip().split())}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def hash_action_context(recipient: Address, amount: u256, purpose: str) -> str:
    return Keccak256(canonical_action_context(recipient, amount, purpose).encode("utf-8")).hexdigest()


class ProtectedTreasury(gl.Contract):
    warrant_address: Address
    used_permits: TreeMap[u256, bool]
    actions: TreeMap[u256, ExecutedAction]
    next_action_id: u256
    executed_total: u256

    def __init__(self, warrant_address: Address):
        self.warrant_address = warrant_address
        self.next_action_id = u256(1)
        self.executed_total = u256(0)

    @gl.public.write
    def execute(self, permit_id: u256, recipient: Address, amount: u256, purpose: str) -> u256:
        purpose = " ".join(str(purpose).strip().split())
        if int(amount) <= 0:
            raise gl.vm.UserError("amount must be positive")
        if len(purpose) == 0 or len(purpose) > MAX_PURPOSE_LEN:
            raise gl.vm.UserError("invalid purpose")
        if self.used_permits.get(permit_id, False):
            raise gl.vm.UserError("permit already used by this consumer")

        payload_hash = hash_payload(recipient, amount, purpose)
        action_context_hash = hash_action_context(recipient, amount, purpose)
        warrant = IWarrant(self.warrant_address)
        if not warrant.view().permit_valid_for_context(
            permit_id,
            gl.message.contract_address,
            ACTION_KEY,
            payload_hash,
            action_context_hash,
            amount,
        ):
            raise gl.vm.UserError("Warrant permit is not valid for this exact action")

        # Replay protection is committed before any asynchronous message.
        self.used_permits[permit_id] = True
        action_id = self.next_action_id
        self.next_action_id = u256(int(self.next_action_id) + 1)
        action = self.actions.get_or_insert_default(action_id)
        action.action_id = action_id
        action.permit_id = permit_id
        action.recipient = recipient
        action.amount = amount
        action.purpose = purpose
        action.payload_hash = payload_hash
        self.executed_total = u256(int(self.executed_total) + int(amount))

        # Finalized messaging avoids accepted-state appeal/replay hazards.  Warrant's
        # record_consumption method is idempotent, so duplicate delivery is harmless.
        warrant.emit(on="finalized").record_consumption(permit_id, payload_hash)
        return action_id

    @gl.public.view
    def payload_hash_for(self, recipient: Address, amount: u256, purpose: str) -> str:
        return hash_payload(recipient, amount, purpose)

    @gl.public.view
    def action_context_hash_for(self, recipient: Address, amount: u256, purpose: str) -> str:
        return hash_action_context(recipient, amount, purpose)

    @gl.public.view
    def get_action(self, action_id: u256) -> dict:
        action = self.actions.get(action_id)
        if action is None:
            raise gl.vm.UserError("unknown action")
        return {
            "action_id": int(action.action_id),
            "permit_id": int(action.permit_id),
            "recipient": str(action.recipient).lower(),
            "amount": int(action.amount),
            "purpose": str(action.purpose),
            "payload_hash": str(action.payload_hash),
        }

    @gl.public.view
    def total_executed(self) -> u256:
        return self.executed_total
