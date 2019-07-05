#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from ocean_utils.keeper import ContractBase, utils
from ocean_utils.keeper.event_filter import EventFilter
from ocean_utils.keeper.web3_provider import Web3Provider

logger = logging.getLogger('escrowAccessSecretStoreTemplate')


class ConditionBase(ContractBase):
    """Base class for all the Condition contract objects."""
    FULFILLED_EVENT = 'Fulfilled'

    def generate_id(self, agreement_id, types, values):
        """
        Generate id for the condition.

        :param agreement_id: id of the agreement, hex str
        :param types: list of types
        :param values: list of values
        :return: id, str
        """
        values_hash = utils.generate_multi_value_hash(types, values)
        return utils.generate_multi_value_hash(
            ['bytes32', 'address', 'bytes32'],
            [agreement_id, self.address, values_hash]
        )

    def _fulfill(self, *args, **kwargs):
        """
        Fulfill the condition.

        :param args:
        :param kwargs:
        :return: true if the condition was successfully fulfilled, bool
        """
        tx_hash = self.send_transaction('fulfill', args, **kwargs)
        return tx_hash

    def abort_by_timeout(self, condition_id):
        """

        :param condition_id: id of the condition, str
        :return:
        """
        tx_hash = self.contract_concise.abortByTimeOut(condition_id)
        return self.is_tx_successful(tx_hash)

    def _hash_values(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        return self.contract_concise.hashValues(*args, **kwargs)

    def subscribe_condition_fulfilled(self, agreement_id, timeout, callback, args,
                                      timeout_callback=None, wait=False,
                                      from_block=None, to_block=None):
        """
        Subscribe to the condition fullfilled event.

        :param agreement_id: id of the agreement, hex str
        :param timeout:
        :param callback:
        :param args:
        :param timeout_callback:
        :param wait: if true block the listener until get the event, bool
        :param from_block: int or None
        :param to_block: int or None
        :return:
        """
        logger.debug(
            f'Subscribing {self.FULFILLED_EVENT} event with agreement id {agreement_id}.')
        return self.subscribe_to_event(
            self.FULFILLED_EVENT,
            timeout,
            {'_agreementId': Web3Provider.get_web3().toBytes(hexstr=agreement_id)},
            callback=callback,
            timeout_callback=timeout_callback,
            args=args,
            wait=wait,
            from_block=from_block,
            to_block=to_block
        )

    def get_event_filter_for_fulfilled(self, agreement_id=None, from_block='latest', to_block='latest'):
        _filter = {}
        if agreement_id:
            assert isinstance(agreement_id, str) or isinstance(agreement_id, bytes)
            if isinstance(agreement_id, str) and agreement_id.startswith('0x'):
                agreement_id = Web3Provider.get_web3().toBytes(hexstr=agreement_id)
            _filter['_agreementId'] = agreement_id

        event_filter = EventFilter(
            self.FULFILLED_EVENT,
            getattr(self.events, self.FULFILLED_EVENT),
            _filter,
            from_block=from_block,
            to_block=to_block
        )
        event_filter.set_poll_interval(0.5)
        return event_filter
