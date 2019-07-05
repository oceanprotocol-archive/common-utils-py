#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.did import id_to_did
from ocean_utils.keeper.conditions.condition_base import ConditionBase
from ocean_utils.keeper.event_filter import EventFilter


class AccessSecretStoreCondition(ConditionBase):
    """Class representing the AccessSecretStoreCondition contract."""
    CONTRACT_NAME = 'AccessSecretStoreCondition'

    def fulfill(self, agreement_id, document_id, grantee_address, account):
        """
        Fulfill the access secret store condition.

        :param agreement_id: id of the agreement, hex str
        :param document_id: refers to the DID in which secret store will issue the decryption
        keys, DID
        :param grantee_address: is the address of the granted user, str
        :param account: Account instance
        :return: true if the condition was successfully fulfilled, bool
        """
        return self._fulfill(
            agreement_id,
            document_id,
            grantee_address,
            transact={'from': account.address,
                      'passphrase': account.password,
                      'keyfile': account.key_file}
        )

    def hash_values(self, document_id, grantee_address):
        """
        Hast the values of the document_id with the grantee address.

        :param document_id: refers to the DID in which secret store will issue the decryption
        keys, DID
        :param grantee_address: is the address of the granted user, str
        :return: hex str
        """
        return self._hash_values(document_id, grantee_address)

    def check_permissions(self, document_id, grantee_address):
        """
        Check that the grantee_address has permissions to decrypt the document stored with this
        document_id.

        :param document_id: refers to the DID in which secret store will issue the decryption
        keys, DID
        :param grantee_address: is the address of the granted user, str
        :return: true if the access was granted, bool
        """
        return self.contract_concise.checkPermissions(grantee_address, document_id)

    def get_purchased_assets_by_address(self, address, from_block=0, to_block='latest'):
        """
        Get the list of the assets dids consumed for an address.

        :param address: is the address of the granted user, hex-str
        :param from_block: block to start to listen
        :param to_block: block to stop to listen
        :return: list of dids
        """
        block_filter = EventFilter(
            ConditionBase.FULFILLED_EVENT,
            getattr(self.events, ConditionBase.FULFILLED_EVENT),
            from_block=from_block,
            to_block=to_block,
            argument_filters={'_grantee': address}
        )
        log_items = block_filter.get_all_entries(max_tries=5)
        did_list = []
        for log_i in log_items:
            did_list.append(id_to_did(log_i.args['_documentId']))

        return did_list
