#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.keeper.conditions.condition_base import ConditionBase


class SignCondition(ConditionBase):
    """Class representing the SignCondition contract."""
    CONTRACT_NAME = 'SignCondition'

    def fulfill(self, agreement_id, message, account_address, signature, from_account):
        """
        Fulfill the sign conditon.

        :param agreement_id: id of the agreement, hex str
        :param message:
        :param account_address: ethereum account address, hex str
        :param signature: signed agreement hash, hex str
        :param from_account: Account doing the transaction
        :return:
        """
        return self._fulfill(
            agreement_id,
            message,
            account_address,
            signature,
            transact={'from': from_account.address,
                      'passphrase': from_account.password,
                      'keyfile': from_account.key_file}
        )

    def hash_values(self, message, account_address):
        """
        Hash the values of the sign condition.

        :param message:
        :param account_address:
        :return:
        """
        return self._hash_values(message, account_address)
