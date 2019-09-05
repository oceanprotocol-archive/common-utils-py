#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import os

import pytest
from ocean_keeper.contract_handler import ContractHandler
from ocean_keeper.keeper import Keeper
from ocean_keeper.web3_provider import Web3Provider
from web3 import HTTPProvider, Web3

from ocean_utils.agreements.service_agreement import ServiceAgreement, ServiceTypes
from ocean_utils.aquarius import AquariusProvider
from ocean_utils.ddo.ddo import DDO
from ocean_utils.did import DID
from tests.resources.helper_functions import (
    get_consumer_account,
    get_ddo_sample,
    get_metadata,
    get_publisher_account
)


def get_aquarius_url():
    if os.getenv('AQUARIUS_URL'):
        return os.getenv('AQUARIUS_URL')
    return 'http://localhost:5000'


def get_keeper_url():
    if os.getenv('KEEPER_URL'):
        return os.getenv('KEEPER_URL')
    return 'http://localhost:8545'


@pytest.fixture(autouse=True)
def setup_all():
    Web3Provider.get_web3('http://localhost:8545')
    ContractHandler.artifacts_path = os.path.expanduser('~/.ocean/keeper-contracts/artifacts')
    Keeper.get_instance(artifacts_path=ContractHandler.artifacts_path)


@pytest.fixture
def publisher_account():
    return get_publisher_account()


@pytest.fixture
def consumer_account():
    return get_consumer_account()


@pytest.fixture
def aquarius():
    return AquariusProvider.get_aquarius(get_aquarius_url())


@pytest.fixture
def registered_ddo():
    return DDO()


@pytest.fixture
def web3_instance():
    return Web3(HTTPProvider(get_keeper_url()))


@pytest.fixture
def metadata():
    return get_metadata()


@pytest.fixture
def setup_agreements_enviroment():
    consumer_acc = get_consumer_account()
    publisher_acc = get_publisher_account()
    keeper = Keeper.get_instance()

    ddo = get_ddo_sample()
    ddo._did = DID.did({"0": "0x12341234"})
    # Remove '0x' from the start of ddo.metadata['base']['checksum']
    text_for_sha3 = ddo.metadata['main']['checksum'][2:]
    keeper.did_registry.register(
        ddo.asset_id,
        checksum=Web3.sha3(text=text_for_sha3),
        url='aquarius:5000',
        account=publisher_acc,
        providers=None
    )

    registered_ddo = ddo
    asset_id = registered_ddo.asset_id
    service_agreement = ServiceAgreement.from_ddo(ServiceTypes.ASSET_ACCESS, ddo)
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
