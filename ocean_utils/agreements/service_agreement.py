#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from ocean_utils.agreements.service_agreement_template import ServiceAgreementTemplate
from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.ddo.service import Service
from ocean_utils.utils.utilities import generate_prefixed_id

Agreement = namedtuple('Agreement', ('template', 'conditions'))


class ServiceAgreement(Service):
    """Class representing a Service Agreement."""
    SERVICE_DEFINITION_ID = 'serviceDefinitionId'
    AGREEMENT_TEMPLATE = 'serviceAgreementTemplate'
    SERVICE_CONDITIONS = 'conditions'
    PURCHASE_ENDPOINT = 'purchaseEndpoint'
    SERVICE_ENDPOINT = 'serviceEndpoint'

    def __init__(self, sa_definition_id, service_agreement_template, service_endpoint=None,
                 purchase_endpoint=None, service_type=None):
        """

        :param sa_definition_id:
        :param service_agreement_template: ServiceAgreementTemplate instance
        :param service_endpoint: str URL to use for requesting service defined in this agreement
        :param purchase_endpoint: str URL to use for consuming the service after access is given
        :param service_type: str like ServiceTypes.ASSET_ACCESS
        """
        self.sa_definition_id = sa_definition_id
        self.service_agreement_template = service_agreement_template

        values_dict = {
            ServiceAgreement.SERVICE_DEFINITION_ID: self.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: self.template_id,

        }
        values_dict.update(self.service_agreement_template.as_dictionary())

        Service.__init__(self, service_endpoint,
                         service_type or ServiceTypes.ASSET_ACCESS,
                         values_dict, purchase_endpoint)

    def get_price(self):
        """
        Return the price from the conditions parameters.

        :return: Int
        """
        for cond in self.conditions:
            for p in cond.parameters:
                if p.name == '_amount':
                    return int(p.value)

    @property
    def service_endpoint(self):
        """

        :return:
        """
        return self._service_endpoint

    @property
    def purchase_endpoint(self):
        """

        :return:
        """
        return self._purchase_endpoint

    @property
    def agreement(self):
        """

        :return:
        """
        return Agreement(self.template_id, self.conditions[:])

    @property
    def template_id(self):
        """

        :return:
        """
        return self.service_agreement_template.template_id

    @property
    def conditions(self):
        """

        :return:
        """
        return self.service_agreement_template.conditions

    @property
    def condition_by_name(self):
        """

        :return:
        """
        return {cond.name: cond for cond in self.conditions}

    @property
    def conditions_params_value_hashes(self):
        """

        :return:
        """
        value_hashes = []
        for cond in self.conditions:
            value_hashes.append(cond.values_hash)

        return value_hashes

    @property
    def conditions_timeouts(self):
        """

        :return:
        """
        return [cond.timeout for cond in self.conditions]

    @property
    def conditions_timelocks(self):
        """

        :return:
        """
        return [cond.timelock for cond in self.conditions]

    @property
    def conditions_contracts(self):
        """

        :return:
        """
        return [cond.contract_name for cond in self.conditions]

    @classmethod
    def from_ddo(cls, service_definition_id, ddo):
        """

        :param service_definition_id: identifier of the service inside the asset DDO, str
        :param ddo:
        :return:
        """
        service_def = ddo.find_service_by_id(service_definition_id).as_dictionary()
        if not service_def:
            raise ValueError(
                f'Service with definition id {service_definition_id} is not found in this DDO.')

        return cls.from_service_dict(service_def)

    @classmethod
    def from_service_dict(cls, service_dict):
        """

        :param service_dict:
        :return:
        """
        return cls(
            service_dict[cls.SERVICE_DEFINITION_ID],
            ServiceAgreementTemplate(service_dict),
            service_dict.get(cls.SERVICE_ENDPOINT),
            service_dict.get(cls.PURCHASE_ENDPOINT),
            service_dict.get('type')
        )

    @staticmethod
    def generate_service_agreement_hash(template_id, values_hash_list, timelocks, timeouts,
                                        agreement_id, hash_function):
        """

        :param template_id:
        :param values_hash_list:
        :param timelocks:
        :param timeouts:
        :param agreement_id: id of the agreement, hex str
        :param hash_function: reference to function that will be used to compute the hash (sha3 or similar)
        :return:
        """
        return hash_function(
            ['address', 'bytes32[]', 'uint256[]', 'uint256[]', 'bytes32'],
            [template_id, values_hash_list, timelocks, timeouts, agreement_id]
        )

    @staticmethod
    def create_new_agreement_id():
        """

        :return:
        """
        return generate_prefixed_id()

    def generate_agreement_condition_ids(self, agreement_id, asset_id, consumer_address,
                                         publisher_address, keeper):
        """

        :param agreement_id: id of the agreement, hex str
        :param asset_id:
        :param consumer_address: ethereum account address of consumer, hex str
        :param publisher_address: ethereum account address of publisher, hex str
        :param keeper:
        :return:
        """
        lock_cond_id = keeper.lock_reward_condition.generate_id(
            agreement_id,
            self.condition_by_name['lockReward'].param_types,
            [keeper.escrow_reward_condition.address, self.get_price()]).hex()

        access_cond_id = keeper.access_secret_store_condition.generate_id(
            agreement_id,
            self.condition_by_name['accessSecretStore'].param_types,
            [asset_id, consumer_address]).hex()

        escrow_cond_id = keeper.escrow_reward_condition.generate_id(
            agreement_id,
            self.condition_by_name['escrowReward'].param_types,
            [self.get_price(), publisher_address, consumer_address,
             lock_cond_id, access_cond_id]).hex()

        return access_cond_id, lock_cond_id, escrow_cond_id

    def get_service_agreement_hash(
            self, agreement_id, asset_id, consumer_address, publisher_address, keeper):
        """Return the hash of the service agreement values to be signed by a consumer.

        :param agreement_id:id of the agreement, hex str
        :param asset_id:
        :param consumer_address: ethereum account address of consumer, hex str
        :param publisher_address: ethereum account address of publisher, hex str
        :param keeper:
        :return:
        """
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            self.template_id,
            self.generate_agreement_condition_ids(
                agreement_id, asset_id, consumer_address, publisher_address, keeper),
            self.conditions_timelocks,
            self.conditions_timeouts,
            agreement_id,
            keeper.generate_multi_value_hash
        )
        return agreement_hash
