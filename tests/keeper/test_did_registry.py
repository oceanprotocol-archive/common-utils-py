"""Test DIDRegistry contract."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import secrets

import pytest
from eth_utils import add_0x_prefix

from ocean_utils import ConfigProvider
from ocean_utils.did import DID, did_to_id
from ocean_utils.keeper.didregistry import DIDRegistry
from ocean_utils.keeper.web3_provider import Web3Provider
from tests.resources.helper_functions import get_publisher_account, get_consumer_account
from tests.resources.tiers import e2e_test

did_registry = DIDRegistry.get_instance()


@e2e_test
def test_did_registry_contract():
    assert did_registry
    assert isinstance(did_registry, DIDRegistry)


@e2e_test
def test_did_registry_get_block_number_updated():
    test_id = secrets.token_hex(32)
    assert did_registry.get_block_number_updated(test_id) == 0


@e2e_test
def test_register():
    config = ConfigProvider.get_config()
    w3 = Web3Provider.get_web3()
    did_test = DID.did()
    register_account = get_publisher_account(config)
    checksum_test = w3.sha3(text='checksum')
    value_test = 'http://localhost:5000'
    # register DID-> URL
    assert did_registry.register(
        did_test, checksum_test, url=value_test, account=register_account
    ) is True

    with pytest.raises(Exception):
        did_registry.get_did_owner(did_test)

    assert did_registry.get_did_owner(
        add_0x_prefix(did_to_id(did_test))
    ) == register_account.address


@e2e_test
def test_register_with_invalid_params():
    w3 = Web3Provider.get_web3()
    did_test = DID.did()
    checksum_test = w3.sha3(text='checksum')
    value_test = 'http://localhost:5000'
    # No checksum provided
    with pytest.raises(ValueError):
        did_registry.register(did_test, '', url=value_test, account=None)
    # Invalid checksum  provided
    with pytest.raises(ValueError):
        did_registry.register(did_test, did_test, url=value_test, account=None)

    # No account provided
    with pytest.raises(ValueError):
        did_registry.register(did_test, checksum_test, url=value_test, account=None)


@e2e_test
def test_providers():
    config = ConfigProvider.get_config()
    w3 = Web3Provider.get_web3()
    did_test = DID.did()
    asset_id = add_0x_prefix(did_to_id(did_test))
    register_account = get_publisher_account(config)
    consumer_account = get_consumer_account(config)
    checksum_test = w3.sha3(text='checksum')
    value_test = 'http://localhost:5000'
    # register DID-> URL
    with pytest.raises(AssertionError):
        did_registry.register(
            did_test, checksum_test, url=value_test, account=register_account, providers=consumer_account.address
        )
    did_registry.register(
        did_test, checksum_test, url=value_test, account=register_account, providers=[consumer_account.address]
    )
    unknown_asset_id = add_0x_prefix(did_to_id(DID.did()))
    providers = did_registry.get_did_providers(unknown_asset_id)
    assert providers is None

    assert did_registry.is_did_provider(asset_id, register_account.address) is False

    providers = did_registry.get_did_providers(asset_id)
    assert len(providers) == 1 and providers[0] == consumer_account.address
    assert did_registry.is_did_provider(asset_id, consumer_account.address) is True

    removed = did_registry.remove_provider(asset_id, consumer_account.address, register_account)
    assert removed
    providers = did_registry.get_did_providers(asset_id)
    assert len(providers) == 0
    assert did_registry.is_did_provider(asset_id, consumer_account.address) is False

    did_registry.add_provider(asset_id, consumer_account.address, register_account)
    providers = did_registry.get_did_providers(asset_id)
    assert len(providers) == 1 and providers[0] == consumer_account.address
    assert did_registry.is_did_provider(asset_id, consumer_account.address) is True
