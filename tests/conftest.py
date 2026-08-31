"""Direct Mode test-runtime compatibility helpers."""

import os
import sys
import inspect
import pytest

from gltest.direct.loader import create_address
def _address(label, direct_vm):
    """Adapt current gltest byte fixtures to GenVM's Address storage type."""
    return type(direct_vm.sender)(create_address(label))


@pytest.fixture
def direct_owner(direct_vm):
    return _address("default_sender", direct_vm)


@pytest.fixture
def direct_alice(direct_vm):
    return _address("alice", direct_vm)


@pytest.fixture
def direct_bob(direct_vm):
    return _address("bob", direct_vm)


@pytest.fixture
def direct_charlie(direct_vm):
    return _address("charlie", direct_vm)


if sys.platform == "win32":
    _unlink = os.unlink

    def _unlink_open_tempfile(path, *args, **kwargs):
        try:
            return _unlink(path, *args, **kwargs)
        except PermissionError:
            caller_files = [frame.filename.replace("\\", "/") for frame in inspect.stack()]
            if any(file.endswith("/gltest/direct/loader.py") for file in caller_files):
                return None
            raise

    os.unlink = _unlink_open_tempfile
