"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
from collections import namedtuple
from urllib.parse import urlparse

from ocean_utils.did import did_to_id_bytes, id_to_did
from ocean_utils.exceptions import OceanDIDNotFound
from ocean_utils.keeper.contract_base import ContractBase
from ocean_utils.keeper.event_filter import EventFilter
from ocean_utils.keeper.web3_provider import Web3Provider

logger = logging.getLogger(__name__)

DIDRegisterValues = namedtuple(
    'DIDRegisterValues',
    ('owner', 'last_checksum', 'last_updated_by', 'block_number_updated', 'providers')
)


class DIDRegistry(ContractBase):
    """Class to register and update Ocean DID's."""
    DID_REGISTRY_EVENT_NAME = 'DIDAttributeRegistered'

    CONTRACT_NAME = 'DIDRegistry'

    def register(self, did, checksum, url, account, providers=None):
        """
        Register or update a DID on the block chain using the DIDRegistry smart contract.

        :param did: DID to register/update, can be a 32 byte or hexstring
        :param checksum: hex str hash of TODO
        :param url: URL of the resolved DID
        :param account: instance of Account to use to register/update the DID
        :param providers: list of addresses of providers to be allowed to serve the asset and play
            a part in creating and fulfilling service agreements
        :return: Receipt
        """

        did_source_id = did_to_id_bytes(did)
        if not did_source_id:
            raise ValueError(f'{did} must be a valid DID to register')

        if not urlparse(url):
            raise ValueError(f'Invalid URL {url} to register for DID {did}')

        if checksum is None:
            checksum = Web3Provider.get_web3().toBytes(0)

        if not isinstance(checksum, bytes):
            raise ValueError(f'Invalid checksum value {checksum}, must be bytes or string')

        if account is None:
            raise ValueError('You must provide an account to use to register a DID')

        transaction = self._register_attribute(
            did_source_id, checksum, url, account, providers or []
        )
        receipt = self.get_tx_receipt(transaction)
        if receipt:
            return receipt.status == 1

        _filters = dict()
        _filters['_did'] = Web3Provider.get_web3().toBytes(hexstr=did)
        _filters['_owner'] = Web3Provider.get_web3().toBytes(hexstr=account.address)
        event = self.subscribe_to_event(self.DID_REGISTRY_EVENT_NAME, 15, _filters, wait=True)
        return event is not None

    def _register_attribute(self, did, checksum, value, account, providers):
        """Register an DID attribute as an event on the block chain.

        :param did: 32 byte string/hex of the DID
        :param checksum: checksum of the ddo, hex str
        :param value: url for resolve the did, str
        :param account: account owner of this DID registration record
        :param providers: list of providers addresses
        """
        assert isinstance(providers, list), ''
        return self.send_transaction(
            'registerAttribute',
            (did,
             checksum,
             providers,
             value),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'keyfile': account.key_file}
        )

    def get_block_number_updated(self, did):
        """Return the block number the last did was updated on the block chain."""
        return self.contract_concise.getBlockNumberUpdated(did)

    def get_did_owner(self, did):
        """
        Return the owner of the did.

        :param did: Asset did, did
        :return: ethereum address, hex str
        """
        return self.contract_concise.getDIDOwner(did)

    def add_provider(self, did, provider_address, account):
        """
        Add the provider of the did.

        :param did: the id of an asset on-chain, hex str
        :param provider_address: ethereum account address of the provider, hex str
        :param account: Account executing the action
        :return:
        """
        tx_hash = self.send_transaction(
            'addDIDProvider',
            (did,
             provider_address),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'keyfile': account.key_file}
        )
        return self.is_tx_successful(tx_hash)

    def remove_provider(self, did, provider_address, account):
        """
        Remove a provider

        :param did: the id of an asset on-chain, hex str
        :param provider_address: ethereum account address of the provider, hex str
        :param account: Account executing the action
        :return:
        """
        tx_hash = self.send_transaction(
            'removeDIDProvider',
            (did,
             provider_address),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'keyfile': account.key_file}
        )
        return self.is_tx_successful(tx_hash)

    def is_did_provider(self, did, address):
        """
        Return true if the address is the Provider of the did.

        :param did: the id of an asset on-chain, hex str
        :param address: ethereum account address, hex str
        :return: bool
        """
        return self.contract_concise.isDIDProvider(did, address)

    def get_did_providers(self, did):
        """
        Return the list providers registered on-chain for the given did.

        :param did: hex str the id of an asset on-chain
        :return:
            list of addresses
            None if asset has no registerd providers
        """
        register_values = self.contract_concise.getDIDRegister(did)
        if register_values and len(register_values) == 5 and register_values[0]:
            # sanitize providers list, because if providers were removed they will
            # be replaced with null/None
            valid_providers = [a for a in register_values[4] if a is not None]
            register_values[4] = valid_providers
            return DIDRegisterValues(*register_values).providers

        return None

    def get_owner_asset_ids(self, address):
        """
        Get the list of assets owned by an address owner.

        :param address: ethereum account address, hex str
        :return:
        """
        block_filter = self._get_event_filter(owner=address)
        log_items = block_filter.get_all_entries(max_tries=5)
        did_list = []
        for log_i in log_items:
            did_list.append(id_to_did(log_i.args['_did']))

        return did_list

    def get_registered_attribute(self, did_bytes):
        """

        Example of event logs from event_filter.get_all_entries():
        [AttributeDict(
            {'args': AttributeDict(
                {'did': b'\x02n\xfc\xfb\xfdNM\xe9\xb8\xe0\xba\xc2\xb2\xc7\xbeg\xc9/\x95\xc3\x16\
                           x98G^\xb9\xe1\xf0T\xce\x83\xcf\xab',
                 'owner': '0xAd12CFbff2Cb3E558303334e7e6f0d25D5791fc2',
                 'value': 'http://localhost:5000',
                 'checksum': '0x...',
                 'updatedAt': 1947}),
             'event': 'DIDAttributeRegistered',
             'logIndex': 0,
             'transactionIndex': 1,
             'transactionHash': HexBytes(
             '0xea9ca5748d54766fb43fe9660dd04b2e3bb29a0fbe18414457cca3dd488d359d'),
             'address': '0x86DF95937ec3761588e6DEbAB6E3508e271cC4dc',
             'blockHash': HexBytes(
             '0xbbbe1046b737f33b2076cb0bb5ba85a840c836cf1ffe88891afd71193d677ba2'),
             'blockNumber': 1947})]

        """
        result = None
        did = Web3Provider.get_web3().toHex(did_bytes)
        block_number = self.get_block_number_updated(did_bytes)
        logger.debug(f'got blockNumber {block_number} for did {did}')
        if block_number == 0:
            raise OceanDIDNotFound(
                f'DID "{did}" is not found on-chain in the current did registry. '
                f'Please ensure assets are registered in the correct keeper contracts. '
                f'The keeper-contracts DIDRegistry address is {self.address}.'
                f'Also ensure that sufficient time has passed after registering the asset '
                f'such that the transaction is confirmed by the network validators.')

        block_filter = self._get_event_filter(did=did, from_block=block_number,
                                              to_block=block_number)
        log_items = block_filter.get_all_entries(max_tries=5)
        if not log_items:
            block_filter = self._get_event_filter(did=did, from_block=block_number - 1,
                                                  to_block=block_number + 1)
            log_items = block_filter.get_all_entries(max_tries=3)

        if log_items:
            log_item = log_items[-1].args
            value = log_item['_value']
            block_number = log_item['_blockNumberUpdated']
            result = {
                'checksum': log_item['_checksum'],
                'value': value,
                'block_number': block_number,
                'did_bytes': log_item['_did'],
                'owner': Web3Provider.get_web3().toChecksumAddress(log_item['_owner']),
            }
        else:
            logger.warning(f'Could not find {DIDRegistry.DID_REGISTRY_EVENT_NAME} event logs for '
                           f'did {did} at blockNumber {block_number}')
        return result

    def _get_event_filter(self, did=None, owner=None, from_block=0, to_block='latest'):
        _filters = {}
        if did is not None:
            _filters['_did'] = Web3Provider.get_web3().toBytes(hexstr=did)
        if owner is not None:
            _filters['_owner'] = Web3Provider.get_web3().toBytes(hexstr=owner)

        block_filter = EventFilter(
            DIDRegistry.DID_REGISTRY_EVENT_NAME,
            getattr(self.events, DIDRegistry.DID_REGISTRY_EVENT_NAME),
            from_block=from_block,
            to_block=to_block,
            argument_filters=_filters
        )
        return block_filter
