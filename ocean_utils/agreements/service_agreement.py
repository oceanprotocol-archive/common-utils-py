#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from ocean_utils.agreements.service_agreement_template import ServiceAgreementTemplate
from ocean_utils.agreements.service_types import ServiceTypes, ServiceTypesIndices
from ocean_utils.ddo.service import Service
from ocean_utils.utils.utilities import generate_prefixed_id

Agreement = namedtuple('Agreement', ('template', 'conditions'))


class ServiceAgreement(Service):
    """Class representing a Service Agreement."""
    SERVICE_INDEX = 'index'
    AGREEMENT_TEMPLATE = 'serviceAgreementTemplate'
    SERVICE_ATTRIBUTES = 'attributes'
    SERVICE_CONDITIONS = 'conditions'
    SERVICE_ENDPOINT = 'serviceEndpoint'

    def __init__(self, attributes, service_agreement_template, service_endpoint=None,
                 service_type=None):
        """

        :param attributes: attributes
        :param service_agreement_template: ServiceAgreementTemplate instance
        :param service_endpoint: str URL to use for requesting service defined in this agreement
        :param service_type: str like ServiceTypes.ASSET_ACCESS
        """
        self.service_agreement_template = service_agreement_template
        values = dict()
        values[ServiceAgreementTemplate.TEMPLATE_ID_KEY] = self.template_id
        values['attributes'] = dict()
        values['attributes'] = attributes
        values['attributes']['serviceAgreementTemplate'] = service_agreement_template.__dict__
        if service_type == ServiceTypes.ASSET_ACCESS:
            values['index'] = ServiceTypesIndices.DEFAULT_ACCESS_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.ASSET_ACCESS,
                             values, ServiceTypesIndices.DEFAULT_ACCESS_INDEX)
        elif service_type == ServiceTypes.CLOUD_COMPUTE:
            values['index'] = ServiceTypesIndices.DEFAULT_COMPUTING_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.CLOUD_COMPUTE,
                             values, ServiceTypesIndices.DEFAULT_COMPUTING_INDEX)
        else:
            raise ValueError(f'The service_type {service_type} is not currently supported.')

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
    def from_ddo(cls, service_type, ddo):
        """

        :param service_type: identifier of the service inside the asset DDO, str
        :param ddo:
        :return:
        """
        service_dict = ddo.get_service(service_type).as_dictionary()
        if not service_dict:
            raise ValueError(
                f'Service of type {service_type} is not found in this DDO.')

        return cls.from_service_dict(service_dict)

    @classmethod
    def from_service_dict(cls, service_dict):
        """

        :param service_dict:
        :return:
        """
        return cls(
            service_dict[cls.SERVICE_ATTRIBUTES],
            ServiceAgreementTemplate(service_dict['templateId'],
                                     service_dict[cls.SERVICE_ATTRIBUTES]['main']['name'],
                                     service_dict[cls.SERVICE_ATTRIBUTES]['main']['creator'],
                                     service_dict[cls.SERVICE_ATTRIBUTES]),
            service_dict.get(cls.SERVICE_ENDPOINT),
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
        :param hash_function: reference to function that will be used to compute the hash (sha3
        or similar)
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
        :param template_type: type of template, currently only access and compute are supported
        :return:
        """
        lock_cond_id = keeper.lock_reward_condition.generate_id(
            agreement_id,
            self.condition_by_name['lockReward'].param_types,
            [keeper.escrow_reward_condition.address, self.get_price()]).hex()

        if self.type == ServiceTypes.ASSET_ACCESS:
            access_or_compute_id = keeper.access_secret_store_condition.generate_id(
                agreement_id,
                self.condition_by_name['accessSecretStore'].param_types,
                [asset_id, consumer_address]).hex()
        elif self.type == ServiceTypes.CLOUD_COMPUTE:
            access_or_compute_id = keeper.compute_execution_condition.generate_id(
                agreement_id,
                self.condition_by_name['execCompute'].param_types,
                [asset_id, consumer_address]).hex()
        else:
            raise Exception(
                'Error generating the condition ids, the service_agreement type is not valid.')

        escrow_cond_id = keeper.escrow_reward_condition.generate_id(
            agreement_id,
            self.condition_by_name['escrowReward'].param_types,
            [self.get_price(), publisher_address, consumer_address,
             lock_cond_id, access_or_compute_id]).hex()

        return access_or_compute_id, lock_cond_id, escrow_cond_id

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
