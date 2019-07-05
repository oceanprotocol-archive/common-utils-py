"""Test Token Contract."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import pytest

from ocean_utils.config_provider import ConfigProvider
from ocean_utils.keeper.conditions import LockRewardCondition
from ocean_utils.keeper.token import Token
from tests.resources.helper_functions import get_consumer_account, get_publisher_account
from tests.resources.tiers import e2e_test

token = Token.get_instance()
consumer_account = get_consumer_account(ConfigProvider.get_config())
publisher_account = get_publisher_account(ConfigProvider.get_config())


@e2e_test
def test_token_contract():
    assert token
    assert isinstance(token, Token)


@e2e_test
def test_get_balance():
    assert isinstance(token.get_token_balance(consumer_account.address), int)


@e2e_test
def test_get_balance_invalid_address():
    with pytest.raises(Exception):
        token.get_token_balance('not valid')


@e2e_test
def test_token_approve():
    assert token.token_approve(consumer_account.address, 100, publisher_account)


@e2e_test
def test_token_approve_invalid_address():
    with pytest.raises(Exception):
        token.token_approve('10923019', 100, publisher_account)


@e2e_test
def test_token_approve_invalid_tokens():
    with pytest.raises(Exception):
        token.token_approve(consumer_account.address, -100, publisher_account)


@e2e_test
def test_token_allowance():
    lock_reward_condition = LockRewardCondition(LockRewardCondition.CONTRACT_NAME)
    allowance = token.get_allowance(consumer_account.address, lock_reward_condition.address)
    if allowance > 0:
        token.decrease_allowance(lock_reward_condition.address, allowance, consumer_account)
        allowance = token.get_allowance(consumer_account.address, lock_reward_condition.address)
    assert allowance == 0

    assert token.token_approve(lock_reward_condition.address, 77, consumer_account) is True
    allowance = token.get_allowance(consumer_account.address, lock_reward_condition.address)
    assert allowance == 77

    assert token.token_approve(lock_reward_condition.address, 49, consumer_account) is True
    allowance = token.get_allowance(consumer_account.address, lock_reward_condition.address)
    assert allowance == 49

    token.decrease_allowance(lock_reward_condition.address, 5, consumer_account)
    allowance = token.get_allowance(consumer_account.address, lock_reward_condition.address)
    assert allowance == 44

    token.increase_allowance(lock_reward_condition.address, 10, consumer_account)
    allowance = token.get_allowance(consumer_account.address, lock_reward_condition.address)
    assert allowance == 54


@e2e_test
def test_token_transfer():
    balance = token.get_token_balance(publisher_account.address)
    token.transfer(publisher_account.address, 3, consumer_account)
    new_balance = token.get_token_balance(publisher_account.address)
    assert new_balance == (balance + 3)
