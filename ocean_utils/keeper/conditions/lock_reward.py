#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.keeper.conditions.condition_base import ConditionBase


class LockRewardCondition(ConditionBase):
    """Class representing the LockRewardCondition contract."""
    CONTRACT_NAME = 'LockRewardCondition'

    def fulfill(self, agreement_id, reward_address, amount, account):
        """
        Fulfill the lock reward condition.

        :param agreement_id: id of the agreement, hex str
        :param reward_address: ethereum account address, hex str
        :param amount: Amount of tokens, int
        :param account: Account instance
        :return:
        """
        return self._fulfill(
            agreement_id,
            reward_address,
            amount,
            transact={'from': account.address,
                      'passphrase': account.password,
                      'keyfile': account.key_file}
        )

    def hash_values(self, reward_address, amount):
        """
        Hash of the values of the lock reward condition.

        :param reward_address: ethereum account address, hex str
        :param amount: Amount of tokens, int
        :return: hex str
        """
        return self._hash_values(reward_address, amount)
