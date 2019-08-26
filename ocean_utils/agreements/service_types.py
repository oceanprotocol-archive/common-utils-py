"""Agreements module."""


#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

class ServiceTypes:
    """Types of Service allowed in ocean protocol DDO services."""
    AUTHORIZATION = 'authorization'
    METADATA = 'metadata'
    ASSET_ACCESS = 'access'
    CLOUD_COMPUTE = 'compute'


class ServiceTypesIndexes:
    DEFAULT_METADATA_INDEX = 0
    DEFAULT_PROVENANCE_INDEX = 1
    DEFAULT_AUTHORIZATION_INDEX = 2
    DEFAULT_ACCESS_INDEX = 3
    DEFAULT_COMPUTING_INDEX = 4
