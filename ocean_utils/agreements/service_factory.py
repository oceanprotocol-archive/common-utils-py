#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.agreements.service_agreement import ServiceAgreement
from ocean_utils.agreements.service_agreement_template import ServiceAgreementTemplate
from ocean_utils.agreements.service_types import ServiceTypes, ServiceTypesIndices
from ocean_utils.agreements.utils import get_sla_template
from ocean_utils.ddo.service import Service
from ocean_utils.did import did_to_id


class ServiceDescriptor(object):
    """Tuples of length 2. The first item must be one of ServiceTypes and the second
    item is a dict of parameters and values required by the service"""

    @staticmethod
    def metadata_service_descriptor(attributes, service_endpoint):
        """
        Metadata service descriptor.

        :param attributes: conforming to the Metadata accepted by Ocean Protocol, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service descriptor.
        """
        return (ServiceTypes.METADATA,
                {'attributes': attributes, 'serviceEndpoint': service_endpoint})

    @staticmethod
    def authorization_service_descriptor(service_endpoint):
        """
        Authorization service descriptor.

        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service descriptor.
        """
        return (ServiceTypes.AUTHORIZATION,
                {'attributes': {'main': {}}, 'serviceEndpoint': service_endpoint})

    @staticmethod
    def access_service_descriptor(attributes, service_endpoint):
        """
        Access service descriptor.

        :param attributes: attributes of the access service, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service descriptor.
        """
        return (
            ServiceTypes.ASSET_ACCESS,
            {'attributes': attributes, 'serviceEndpoint': service_endpoint}
        )

    @staticmethod
    def compute_service_descriptor(attributes, service_endpoint):
        """
        Compute service descriptor.

        :param attributes: attributes of the compute service, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service descriptor.
        """
        return (
            ServiceTypes.CLOUD_COMPUTE,
            {'attributes': attributes, 'serviceEndpoint': service_endpoint}
        )


class ServiceFactory(object):
    """Factory class to create Services."""

    @staticmethod
    def build_services(service_descriptors):
        """
        Build a list of services.

        :param service_descriptors: List of tuples of length 2. The first item must be one of
        ServiceTypes
        and the second item is a dict of parameters and values required by the service
        :return: List of Services
        """
        services = []
        sa_def_key = ServiceAgreement.SERVICE_INDEX
        for i, service_desc in enumerate(service_descriptors):
            service = ServiceFactory.build_service(service_desc)
            # set index for each service
            service.update_value(sa_def_key, str(i))
            services.append(service)

        return services

    @staticmethod
    def build_service(service_descriptor):
        """
        Build a service.

        :param service_descriptor: Tuples of length 2. The first item must be one of ServiceTypes
        and the second item is a dict of parameters and values required by the service
        :return: Service
        """
        assert isinstance(service_descriptor, tuple) and len(
            service_descriptor) == 2, 'Unknown service descriptor format.'
        service_type, kwargs = service_descriptor
        if service_type == ServiceTypes.METADATA:
            return ServiceFactory.build_metadata_service(
                kwargs['attributes'],
                kwargs['serviceEndpoint']
            )

        elif service_type == ServiceTypes.AUTHORIZATION:
            return ServiceFactory.build_authorization_service(
                kwargs['attributes'],
                kwargs['serviceEndpoint']
            )

        elif service_type == ServiceTypes.ASSET_ACCESS:
            return ServiceFactory.build_access_service(
                kwargs['attributes'],
                kwargs['serviceEndpoint']
            )
        elif service_type == ServiceTypes.CLOUD_COMPUTE:
            return ServiceFactory.build_compute_service(
                kwargs['attributes'],
                kwargs['serviceEndpoint']
            )
        raise ValueError(f'Unknown service type {service_type}')

    @staticmethod
    def build_metadata_service(metadata, service_endpoint):
        """
        Build a metadata service.

        :param metadata: conforming to the Metadata accepted by Ocean Protocol, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service
        """
        return Service(service_endpoint,
                       ServiceTypes.METADATA,
                       values={'attributes': metadata},
                       index=ServiceTypesIndices.DEFAULT_METADATA_INDEX
                       )

    @staticmethod
    def build_authorization_service(attributes, service_endpoint):
        """
        Build an authorization service.

        :param attributes: attributes of authorization service, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service
        """
        return Service(service_endpoint, ServiceTypes.AUTHORIZATION,
                       values={'attributes': attributes},
                       index=ServiceTypesIndices.DEFAULT_AUTHORIZATION_INDEX)

    @staticmethod
    def build_access_service(attributes, service_endpoint):
        """
        Build an authorization service.

        :param attributes: attributes of access service, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service
        """
        return Service(service_endpoint, ServiceTypes.ASSET_ACCESS,
                       values={'attributes': attributes},
                       index=ServiceTypesIndices.DEFAULT_ACCESS_INDEX)

    @staticmethod
    def build_compute_service(attributes, service_endpoint):
        """
        Build an authorization service.

        :param attributes: attributes of compute service, dict
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :return: Service
        """
        return Service(service_endpoint, ServiceTypes.CLOUD_COMPUTE,
                       values={'attributes': attributes},
                       index=ServiceTypesIndices.DEFAULT_COMPUTING_INDEX)

    @staticmethod
    def complete_access_service(did, service_endpoint, attributes, template_id,
                                reward_contract_address):
        """
        Build the access service.

        :param did: DID, str
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :param template_id: id of the template use to create the service, str
        :param reward_contract_address: hex str ethereum address of deployed reward condition
            smart contract
        :return: ServiceAgreement
        """
        param_map = {
            '_documentId': did_to_id(did),
            '_amount': attributes['main']['price'],
            '_rewardAddress': reward_contract_address
        }
        sla_template_dict = get_sla_template()
        sla_template = ServiceAgreementTemplate(template_id, ServiceTypes.ASSET_ACCESS,
                                                attributes['main']['creator'], sla_template_dict)
        sla_template.template_id = template_id
        conditions = sla_template.conditions[:]
        for cond in conditions:
            for param in cond.parameters:
                param.value = param_map.get(param.name, '')

            if cond.timeout > 0:
                cond.timeout = attributes['main']['timeout']

        sla_template.set_conditions(conditions)
        sa = ServiceAgreement(
            attributes,
            sla_template,
            service_endpoint,
            ServiceTypes.ASSET_ACCESS
        )
        return sa

    @staticmethod
    def complete_compute_service(did, service_endpoint, attributes, template_id,
                                 reward_contract_address):
        """
        Build the access service.

        :param did: DID, str
        :param service_endpoint: identifier of the service inside the asset DDO, str
        :param template_id: id of the template use to create the service, str
        :param reward_contract_address: hex str ethereum address of deployed reward condition
            smart contract
        :return: ServiceAgreement
        """
        param_map = {
            '_documentId': did_to_id(did),
            '_amount': attributes['main']['price'],
            '_rewardAddress': reward_contract_address
        }
        sla_template_dict = get_sla_template(ServiceTypes.CLOUD_COMPUTE)
        sla_template = ServiceAgreementTemplate(template_id, ServiceTypes.CLOUD_COMPUTE,
                                                attributes['main']['creator'], sla_template_dict)
        sla_template.template_id = template_id
        conditions = sla_template.conditions[:]
        for cond in conditions:
            for param in cond.parameters:
                param.value = param_map.get(param.name, '')

            if cond.timeout > 0:
                cond.timeout = attributes['main']['timeout']

        sla_template.set_conditions(conditions)
        sa = ServiceAgreement(
            attributes,
            sla_template,
            service_endpoint,
            ServiceTypes.CLOUD_COMPUTE
        )
        return sa
