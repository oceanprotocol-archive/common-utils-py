#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import pytest
from web3 import Web3

from ocean_utils.keeper.web3_provider import Web3Provider
from ocean_utils.utils import utilities
from tests.resources.tiers import e2e_test


@e2e_test
def test_split_signature():
    signature = b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95\xdc=\xe6\xafc' \
                b'\x0f\xe9\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15\xf6f' \
                b'\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42\x01'
    split_signature = utilities.split_signature(Web3, signature=signature)
    assert split_signature.v == 28
    assert split_signature.r == b'\x19\x15!\xecwnX1o/\xdeho\x9a9\xdd9^\xbb\x8c2z\x88!\x95' \
                                b'\xdc=\xe6\xafc\x0f\xe9'
    assert split_signature.s == b'\x14\x12\xc6\xde\x0b\n\xa6\x11\xc0\x1cvv\x9f\x99O8\x15' \
                                b'\xf6f\xe7\xab\xea\x982Ds\x0bX\xd9\x94\xa42'


@e2e_test
def test_get_publickey_from_address(publisher_ocean_instance):
    from eth_keys.exceptions import BadSignature
    for account in publisher_ocean_instance.accounts.list():
        try:
            pub_key = utilities.get_public_key_from_address(Web3Provider.get_web3(),
                                                            account)
            assert pub_key.to_checksum_address() == account.address, \
                'recovered public key address does not match original address.'
        except BadSignature:
            pytest.fail("BadSignature")
        except ValueError:
            pass


@e2e_test
def test_convert():
    input_text = "my text"
    print("output %s" % utilities.convert_to_string(Web3,
                                                    utilities.convert_to_bytes(Web3, input_text)))
    assert utilities.convert_to_text(Web3,
                                     utilities.convert_to_bytes(Web3, input_text)) == input_text
