#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import os

import pytest
from ocean_keeper.web3.http_provider import CustomHTTPProvider
from ocean_keeper.web3_provider import Web3Provider
from web3 import HTTPProvider, Web3, WebsocketProvider

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
    return os.environ.get('ETH_NETWORK', 'http://localhost:8545')


@pytest.fixture(autouse=True)
def setup_all():
    network = get_keeper_url()
    provider = CustomHTTPProvider
    if network.startswith('wss'):
        provider = WebsocketProvider

    Web3Provider.init_web3(provider=provider(network))
    if 'rinkeby' in network:
        from web3.middleware import geth_poa_middleware
        Web3Provider.get_web3().middleware_stack.inject(geth_poa_middleware, layer=0)


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
