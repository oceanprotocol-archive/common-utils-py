#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from ocean_utils.keeper import ContractBase

ConditionValues = namedtuple(
    'ConditionValues',
    ('type_ref', 'state', 'time_lock', 'time_out',
     'block_number', 'last_updated_by', 'block_number_updated')
)


class ConditionStoreManager(ContractBase):
    """Class representing the ConditionStoreManager contract."""
    CONTRACT_NAME = 'ConditionStoreManager'

    def get_condition(self, condition_id):
        """Retrieve the condition for a condition_id.

        :param condition_id: id of the condition, str
        :return:
        """
        condition = self.contract_concise.getCondition(condition_id)
        if condition and len(condition) == 7:
            return ConditionValues(*condition)

        return None

    def get_condition_state(self, condition_id):
        """Retrieve the condition state.

        :param condition_id: id of the condition, str
        :return: State of the condition
        """
        return self.contract_concise.getConditionState(condition_id)

    def get_num_condition(self):
        """
        Return the size of the Conditions list.

        :return: the length of the conditions list, int
        """
        return self.contract_concise.getConditionListSize()
