"""Agreements module."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import os

from ocean_utils.agreements.access_sla_template import ACCESS_SLA_TEMPLATE
from ocean_utils.agreements.service_types import ServiceTypes


def get_sla_template(service_type=ServiceTypes.ASSET_ACCESS):
    """
    Get the template for a ServiceType.

    :param service_type: ServiceTypes
    :return: template dict
    """
    if service_type == ServiceTypes.ASSET_ACCESS:
        return ACCESS_SLA_TEMPLATE.copy()
    else:
        raise ValueError(f'Invalid/unsupported service agreement type {service_type}')
