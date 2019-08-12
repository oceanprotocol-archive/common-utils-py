#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.agreements.service_agreement import ServiceAgreement
from ocean_utils.agreements.service_agreement_template import ServiceAgreementTemplate
from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.agreements.utils import get_sla_template
from ocean_utils.ddo.service import Service
from ocean_utils.did import did_to_id


class ServiceDescriptor(object):
    """Tuples of length 2. The first item must be one of ServiceTypes and the second
    item is a dict of parameters and values required by the service"""

    @staticmethod
    def metadata_service_descriptor(metadata, service_endpoint):
        """
        Metadata service descriptor.

        :param metadata: conforming to the Metadata accepted by Ocean Protocol, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service descriptor.
        """
        return (ServiceTypes.METADATA,
                {'metadata': metadata, 'serviceEndpoint': service_endpoint})

    @staticmethod
    def authorization_service_descriptor(service_endpoint):
        """
        Authorization service descriptor.

        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service descriptor.
        """
        return (ServiceTypes.AUTHORIZATION,
                {'serviceEndpoint': service_endpoint})

    @staticmethod
    def access_service_descriptor(price, purchase_endpoint, service_endpoint, timeout,
                                  template_id, reward_contract_address):
        """
        Access service descriptor.

        :param price: Asset price, int
        :param purchase_endpoint: url of the service provider, str
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :param timeout: amount of time in seconds before the agreement expires, int
        :param template_id: id of the template use to create the service, str
        :param reward_contract_address: hex str ethereum address of deployed reward condition
            smart contract
        :return: Service descriptor.
        """
        return (
            ServiceTypes.ASSET_ACCESS,
            {
                'price': price,
                'purchaseEndpoint': purchase_endpoint,
                'serviceEndpoint': service_endpoint,
                'timeout': timeout,
                'templateId': template_id,
                'rewardContractAddress': reward_contract_address}
        )

    @staticmethod
    def compute_service_descriptor(price, purchase_endpoint, service_endpoint,
                                   timeout, reward_contract_address):
        """
        Compute service descriptor.

        :param price: Asset price, int
        :param purchase_endpoint: url of the service provider, str
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :param timeout: amount of time in seconds before the agreement expires, int
        :param reward_contract_address: hex str ethereum address of deployed reward condition
            smart contract
        :return: Service descriptor.
        """
        return (ServiceTypes.CLOUD_COMPUTE,
                {'price': price,
                 'purchaseEndpoint': purchase_endpoint,
                 'serviceEndpoint': service_endpoint,
                 'timeout': timeout,
                 'rewardContractAddress': reward_contract_address})


class ServiceFactory(object):
    """Factory class to create Services."""

    @staticmethod
    def build_services(did, service_descriptors):
        """
        Build a list of services.

        :param did: DID, str
        :param service_descriptors: List of tuples of length 2. The first item must be one of
        ServiceTypes
        and the second item is a dict of parameters and values required by the service
        :return: List of Services
        """
        services = []
        sa_def_key = ServiceAgreement.SERVICE_DEFINITION_ID
        for i, service_desc in enumerate(service_descriptors):
            service = ServiceFactory.build_service(service_desc, did)
            # set serviceDefinitionId for each service
            service.update_value(sa_def_key, str(i))
            services.append(service)

        return services

    @staticmethod
    def build_service(service_descriptor, did):
        """
        Build a service.

        :param service_descriptor: Tuples of length 2. The first item must be one of ServiceTypes
        and the second item is a dict of parameters and values required by the service
        :param did: DID, str
        :return: Service
        """
        assert isinstance(service_descriptor, tuple) and len(
            service_descriptor) == 2, 'Unknown service descriptor format.'
        service_type, kwargs = service_descriptor
        if service_type == ServiceTypes.METADATA:
            return ServiceFactory.build_metadata_service(
                did,
                kwargs['metadata'],
                kwargs['serviceEndpoint']
            )

        elif service_type == ServiceTypes.AUTHORIZATION:
            return ServiceFactory.build_authorization_service(
                kwargs['serviceEndpoint']
            )

        elif service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceFactory.build_access_service(
                did, kwargs['price'],
                kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'],
                kwargs['timeout'], kwargs['templateId'], kwargs['rewardContractAddress']
            )

        elif service_type == ServiceTypes.CLOUD_COMPUTE:
            return ServiceFactory.build_compute_service(
                did, kwargs['price'],
                kwargs['purchaseEndpoint'], kwargs['serviceEndpoint'],
                kwargs['timeout'], kwargs['rewardContractAddress']
            )

        raise ValueError(f'Unknown service type {service_type}')

    @staticmethod
    def build_metadata_service(did, metadata, service_endpoint):
        """
        Build a metadata service.

        :param did: DID, str
        :param metadata: conforming to the Metadata accepted by Ocean Protocol, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service
        """
        return Service(service_endpoint,
                       ServiceTypes.METADATA,
                       values={'metadata': metadata},
                       did=did)

    @staticmethod
    def build_authorization_service(service_endpoint):
        """
        Build an authorization service.

        :param service_endpoint:
        :return: Service
        """
        return Service(service_endpoint, ServiceTypes.AUTHORIZATION,
                       values={'service': 'SecretStore'})

    @staticmethod
    def build_access_service(did, price, purchase_endpoint, service_endpoint,
                             timeout, template_id, reward_contract_address):
        """
        Build the access service.

        :param did: DID, str
        :param price: Asset price, int
        :param purchase_endpoint: url of the service provider, str
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :param timeout: amount of time in seconds before the agreement expires, int
        :param template_id: id of the template use to create the service, str
        :param reward_contract_address: hex str ethereum address of deployed reward condition
            smart contract
        :return: ServiceAgreement
        """
        # TODO fill all the possible mappings
        param_map = {
            '_documentId': did_to_id(did),
            '_amount': price,
            '_rewardAddress': reward_contract_address
        }
        sla_template_dict = get_sla_template()
        sla_template = ServiceAgreementTemplate(template_json=sla_template_dict)
        sla_template.template_id = template_id
        conditions = sla_template.conditions[:]
        for cond in conditions:
            for param in cond.parameters:
                param.value = param_map.get(param.name, '')

            if cond.timeout > 0:
                cond.timeout = timeout

        sla_template.set_conditions(conditions)
        sa = ServiceAgreement(
            1,
            sla_template,
            service_endpoint,
            purchase_endpoint,
            ServiceTypes.ASSET_ACCESS
        )
        sa.set_did(did)
        return sa

    @staticmethod
    def build_compute_service(did, price, purchase_endpoint, service_endpoint,
                              timeout, reward_contract_address):
        # TODO: implement this once the compute flow is ready
        return
