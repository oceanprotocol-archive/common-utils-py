#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import pytest
from web3 import HTTPProvider, Web3

from examples import ExampleConfig
from ocean_utils.agreements.service_agreement import ServiceAgreement
from ocean_utils.config_provider import ConfigProvider
from ocean_utils.did import DID
from ocean_utils.keeper import Keeper
from ocean_utils.keeper.web3_provider import Web3Provider
from tests.resources.helper_functions import (get_consumer_account, get_consumer_ocean_instance,
                                              get_ddo_sample, get_metadata, get_publisher_account,
                                              get_publisher_ocean_instance, get_registered_ddo)
from tests.resources.mocks.secret_store_mock import SecretStoreMock
from tests.resources.tiers import should_run_test

if should_run_test('e2e'):
    ConfigProvider.set_config(ExampleConfig.get_config())


@pytest.fixture
def secret_store():
    return SecretStoreMock


@pytest.fixture
def publisher_ocean_instance():
    return get_publisher_ocean_instance()


@pytest.fixture
def consumer_ocean_instance():
    return get_consumer_ocean_instance()


@pytest.fixture
def publisher_ocean_instance_brizo():
    return get_publisher_ocean_instance(use_brizo_mock=False)


@pytest.fixture
def consumer_ocean_instance_brizo():
    return get_consumer_ocean_instance(use_brizo_mock=False)


@pytest.fixture
def registered_ddo():
    config = ExampleConfig.get_config()
    return get_registered_ddo(get_publisher_ocean_instance(), get_publisher_account(config))


@pytest.fixture
def web3_instance():
    config = ExampleConfig.get_config()
    return Web3(HTTPProvider(config.keeper_url))


@pytest.fixture
def metadata():
    return get_metadata()


@pytest.fixture
def setup_agreements_enviroment():
    config = ConfigProvider.get_config()
    consumer_acc = get_consumer_account(config)
    publisher_acc = get_publisher_account(config)
    keeper = Keeper.get_instance()

    service_definition_id = 'Access'

    ddo = get_ddo_sample()
    ddo._did = DID.did()
    # Remove '0x' from the start of ddo.metadata['base']['checksum']
    text_for_sha3 = ddo.metadata['base']['checksum'][2:]
    keeper.did_registry.register(
        ddo.did,
        checksum=Web3Provider.get_web3().sha3(text=text_for_sha3),
        url='aquarius:5000',
        account=publisher_acc,
        providers=None
    )

    registered_ddo = ddo
    asset_id = registered_ddo.asset_id
    service_agreement = ServiceAgreement.from_ddo(service_definition_id, ddo)
    agreement_id = ServiceAgreement.create_new_agreement_id()
    price = service_agreement.get_price()
    access_cond_id, lock_cond_id, escrow_cond_id = \
        service_agreement.generate_agreement_condition_ids(
            agreement_id, asset_id, consumer_acc.address, publisher_acc.address, keeper
        )

    return (
        keeper,
        publisher_acc,
        consumer_acc,
        agreement_id,
        asset_id,
        price,
        service_agreement,
        (lock_cond_id, access_cond_id, escrow_cond_id),
    )
