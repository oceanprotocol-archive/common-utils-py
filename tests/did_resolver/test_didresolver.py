#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import secrets

import pytest
from ocean_keeper import Keeper
from ocean_keeper.exceptions import (
    OceanDIDNotFound,
)
from web3 import Web3

from ocean_utils.ddo.ddo import DDO
from ocean_utils.did import DID, did_to_id
from ocean_utils.did_resolver.did_resolver import (
    DIDResolver,
)
from tests.resources.helper_functions import get_resource_path
from tests.resources.tiers import e2e_test

logger = logging.getLogger()


def keeper():
    return Keeper.get_instance()


@e2e_test
def test_did_resolver_library(publisher_account, aquarius):
    did_registry = keeper().did_registry
    checksum_test = Web3.sha3(text='checksum')
    value_test = aquarius.root_url

    did_resolver = DIDResolver(keeper().did_registry)

    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)
    asset1 = DDO(json_filename=sample_ddo_path)
    asset1._did = DID.did({"0": "0x1098098"})
    did_registry.register(asset1.asset_id, checksum_test, url=value_test, account=publisher_account)
    aquarius.publish_asset_ddo(asset1)

    did_resolved = did_resolver.resolve(asset1.did)
    assert did_resolved
    assert did_resolved.did == asset1.did

    with pytest.raises(ValueError):
        did_resolver.resolve(asset1.asset_id)

    aquarius.retire_asset_ddo(asset1.did)


@e2e_test
def test_did_not_found():
    did_resolver = DIDResolver(keeper().did_registry)
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    with pytest.raises(OceanDIDNotFound):
        did_resolver.resolve(did_id_bytes)


@e2e_test
def test_get_resolve_url(aquarius, publisher_account):
    register_account = publisher_account
    did_registry = keeper().did_registry
    did = DID.did({"0": "0x1"})
    asset_id = did_to_id(did)
    value_test = aquarius.root_url
    did_resolver = DIDResolver(keeper().did_registry)
    did_registry.register(asset_id, b'test', url=value_test, account=register_account)
    url = did_resolver.get_resolve_url(Web3.toBytes(hexstr=asset_id))
    assert url == value_test


@e2e_test
def test_get_resolve_multiple_urls(publisher_account):
    register_account = publisher_account
    did_registry = keeper().did_registry
    did = DID.did({"0": "0x1"})
    did2 = DID.did({"0": "0x2"})
    did3 = DID.did({"0": "0x3"})
    did4 = DID.did({"0": "0x4"})
    did5 = DID.did({"0": "0x5"})
    did6 = DID.did({"0": "0x6"})
    did7 = DID.did({"0": "0x7"})
    did8 = DID.did({"0": "0x8"})
    did9 = DID.did({"0": "0x9"})
    did10 = DID.did({"0": "0x10"})
    value_test = 'http://localhost:5000'
    value_test2 = 'http://localhost:5001'
    value_test3 = 'http://localhost:5002'
    value_test4 = 'http://localhost:5003'
    value_test5 = 'http://localhost:5004'
    value_test6 = 'http://localhost:5005'
    value_test7 = 'http://localhost:5006'
    value_test8 = 'http://localhost:5007'
    value_test9 = 'http://localhost:5008'
    value_test10 = 'http://localhost:5009'
    did_id = did_to_id(did)
    did_id2 = did_to_id(did2)
    did_id3 = did_to_id(did3)
    did_id4 = did_to_id(did4)
    did_id5 = did_to_id(did5)
    did_id6 = did_to_id(did6)
    did_id7 = did_to_id(did7)
    did_id8 = did_to_id(did8)
    did_id9 = did_to_id(did9)
    did_id10 = did_to_id(did10)
    did_resolver = DIDResolver(keeper().did_registry)
    did_registry.register(did_id, b'test', url=value_test, account=register_account)
    did_registry.register(did_id2, b'test', url=value_test2, account=register_account)
    did_registry.register(did_id3, b'test', url=value_test3, account=register_account)
    did_registry.register(did_id4, b'test', url=value_test4, account=register_account)
    did_registry.register(did_id5, b'test', url=value_test5, account=register_account)
    did_registry.register(did_id6, b'test', url=value_test6, account=register_account)
    did_registry.register(did_id7, b'test', url=value_test7, account=register_account)
    did_registry.register(did_id8, b'test', url=value_test8, account=register_account)
    did_registry.register(did_id9, b'test', url=value_test9, account=register_account)
    did_registry.register(did_id10, b'test', url=value_test10, account=register_account)
    url = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id))
    url2 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id2))
    url3 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id3))
    url4 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id4))
    url5 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id5))
    url6 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id6))
    url7 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id7))
    url8 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id8))
    url9 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id9))
    url10 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id10))
    assert url == value_test
    assert url2 == value_test2
    assert url3 == value_test3
    assert url4 == value_test4
    assert url5 == value_test5
    assert url6 == value_test6
    assert url7 == value_test7
    assert url8 == value_test8
    assert url9 == value_test9
    assert url10 == value_test10


@e2e_test
def test_get_did_not_valid():
    did_resolver = DIDResolver(keeper().did_registry)
    with pytest.raises(TypeError):
        did_resolver.get_resolve_url('not valid')
