"""Test the Account object."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.keeper.account import Account


def test_create_account():
    account = Account('0x213123123', 'pass')
    assert isinstance(account, Account)
    assert account.address == '0x213123123'
    assert account.password == 'pass'
