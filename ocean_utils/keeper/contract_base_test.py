#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from unittest.mock import MagicMock, Mock

from tests.resources.dependencies import inject_dependencies
from tests.resources.tiers import unit_test
from .contract_base import ContractBase


@unit_test
def test_to_checksum_address():
    contract_handler = Mock()
    web3 = Mock()
    web3.toChecksumAddress = MagicMock(return_value='checksum address!')
    with inject_dependencies(ContractBase, 'TestContract',
                             dependencies={'ContractHandler': contract_handler,
                                           'web3': web3}) as contract_base:
        assert contract_base.to_checksum_address('bla') == 'checksum address!'
        web3.toChecksumAddress.assert_called_with('bla')
