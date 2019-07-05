#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.keeper.conditions.condition_base import ConditionBase


class EscrowRewardCondition(ConditionBase):
    """Class representing the EscrowReward contract."""
    CONTRACT_NAME = 'EscrowReward'

    def fulfill(self,
                agreement_id,
                amount,
                receiver_address,
                sender_address,
                lock_condition_id,
                release_condition_id,
                account):
        """
        Fulfill the escrow reward condition.

        :param agreement_id: id of the agreement, hex str
        :param amount: Amount of tokens, int
        :param receiver_address: ethereum address of the receiver, hex str
        :param sender_address: ethereum address of the sender, hex str
        :param lock_condition_id: id of the condition, str
        :param release_condition_id: id of the condition, str
        :param account: Account instance
        :return:
        """
        return self._fulfill(
            agreement_id,
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id,
            transact={'from': account.address,
                      'passphrase': account.password,
                      'keyfile': account.key_file}
        )

    def hash_values(self, amount, receiver_address, sender_address, lock_condition_id,
                    release_condition_id):
        """
        Hash the values of the escrow reward condition.

        :param amount: Amount of tokens, int
        :param receiver_address: ethereum address of the receiver, hex str
        :param sender_address: ethereum address of the sender, hex str
        :param lock_condition_id: id of the condition, str
        :param release_condition_id: id of the condition, str
        :return: hex str
        """
        return self._hash_values(
            amount,
            receiver_address,
            sender_address,
            lock_condition_id,
            release_condition_id
        )
