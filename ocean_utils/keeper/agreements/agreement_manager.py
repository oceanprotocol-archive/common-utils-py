"""Keeper agreements sub-module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from eth_utils import add_0x_prefix

from ocean_utils.keeper import ContractBase

AgreementValues = namedtuple(
    'AgreementValues',
    ('did', 'owner', 'template_id', 'condition_ids', 'updated_by', 'block_number_updated')
)


class AgreementStoreManager(ContractBase):
    """Class representing the AgreementStoreManager contract."""
    CONTRACT_NAME = 'AgreementStoreManager'

    def create_agreement(self, agreement_id, did, condition_types, condition_ids, time_locks,
                         time_outs):
        """
        Create a new agreement.
        The agreement will create conditions of conditionType with conditionId.
        Only "approved" templates can access this function.
        :param agreement_id:id of the agreement, hex str
        :param did: DID of the asset. The DID must be registered beforehand, bytes32
        :param condition_types: is a list of addresses that point to Condition contracts,
                                list(address)
        :param condition_ids: is a list of bytes32 content-addressed Condition IDs, bytes32
        :param time_locks: is a list of uint time lock values associated to each Condition, int
        :param time_outs: is a list of uint time out values associated to each Condition, int
        :return: bool
        """

        tx_hash = self.contract_concise.createAgreement(
            agreement_id,
            did,
            condition_types,
            condition_ids,
            time_locks,
            time_outs,
        )
        return self.is_tx_successful(tx_hash)

    def get_agreement(self, agreement_id):
        """
        Retrieve the agreement for a agreement_id.

        :param agreement_id: id of the agreement, hex str
        :return: the agreement attributes.
        """
        agreement = self.contract_concise.getAgreement(agreement_id)
        if agreement and len(agreement) == 6:
            agreement = AgreementValues(*agreement)
            did = add_0x_prefix(agreement.did.hex())
            cond_ids = [add_0x_prefix(_id.hex()) for _id in agreement.condition_ids]

            return AgreementValues(
                did,
                agreement.owner,
                agreement.template_id,
                cond_ids,
                agreement.updated_by,
                agreement.block_number_updated
            )

        return None

    def get_agreement_did_owner(self, agreement_id):
        """Get the DID owner for this agreement with _id.

        :param agreement_id: id of the agreement, hex str
        :return: the DID owner associated with agreement.did from the DID registry.
        """
        return self.contract_concise.getAgreementDIDOwner(agreement_id)

    def get_num_agreements(self):
        """Return the size of the Agreements list.

        :return: the length of the agreement list, int
        """
        return self.contract_concise.getAgreementListSize()
