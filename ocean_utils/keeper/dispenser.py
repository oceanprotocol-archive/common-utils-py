"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from web3.utils.threads import Timeout

from ocean_utils.exceptions import OceanInvalidTransaction
from ocean_utils.keeper.contract_base import ContractBase
from ocean_utils.keeper.event_filter import EventFilter
from ocean_utils.keeper.web3_provider import Web3Provider


class Dispenser(ContractBase):
    """Class representing the Dispenser contract."""

    CONTRACT_NAME = 'Dispenser'

    @staticmethod
    def get_scale():
        return 10 ** 18

    def request_vodkas(self, amount, account):
        self.request_tokens(max(1, int(amount/self.get_scale())), account)

    def request_tokens(self, amount, account):
        """
        Request an amount of tokens for a particular address.
        This transaction has gas cost

        :param amount: Amount of tokens, int
        :param account: Account instance
        :raise OceanInvalidTransaction: Transaction failed
        :return: bool
        """
        address = account.address
        try:
            tx_hash = self.send_transaction(
                'requestTokens',
                (amount,),
                transact={'from': address,
                          'passphrase': account.password,
                          'keyfile': account.key_file}
            )
            logging.debug(f'{address} requests {amount} tokens, returning receipt')
            try:
                receipt = Web3Provider.get_web3().eth.waitForTransactionReceipt(
                    tx_hash, timeout=10)
                logging.debug(f'requestTokens receipt: {receipt}')
            except Timeout:
                receipt = None

            if not receipt:
                return False

            if receipt.status == 0:
                logging.warning(f'request tokens failed: Tx-receipt={receipt}')
                logging.warning(f'request tokens failed: account {address}')
                return False

            # check for emitted events:
            rfe = EventFilter(
                'RequestFrequencyExceeded',
                self.events.RequestFrequencyExceeded,
                argument_filters={'requester': Web3Provider.get_web3().toBytes(hexstr=address)},
                from_block='latest',
                to_block='latest',
            )
            logs = rfe.get_all_entries(max_tries=5)
            if logs:
                logging.warning(f'request tokens failed RequestFrequencyExceeded')
                logging.info(f'RequestFrequencyExceeded event logs: {logs}')
                return False

            rle = EventFilter(
                'RequestLimitExceeded',
                self.events.RequestLimitExceeded,
                argument_filters={'requester': Web3Provider.get_web3().toBytes(hexstr=address)},
                from_block='latest',
                to_block='latest',
            )
            logs = rle.get_all_entries(max_tries=5)
            if logs:
                logging.warning(f'request tokens failed RequestLimitExceeded')
                logging.info(f'RequestLimitExceeded event logs: {logs}')
                return False

            return True

        except ValueError as err:
            raise OceanInvalidTransaction(
                f'Requesting {amount} tokens'
                f' to {address} failed with error: {err}'
            )
