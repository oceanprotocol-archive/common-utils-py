"""
    Service Class
    To handle service items in a DDO record
"""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import logging

# from ocean_commons.agreements.service_agreement import ServiceAgreement
# from ocean_commons.agreements.service_types import ServiceTypes

logger = logging.getLogger(__name__)


class Service:
    """Service class to create validate service in a DDO."""
    SERVICE_ENDPOINT = 'serviceEndpoint'

    def __init__(self, service_endpoint, service_type, values, index=None):
        """Initialize Service instance."""
        self._service_endpoint = service_endpoint
        self._type = service_type
        self._index = index

        # assign the _values property to empty until they are used
        self._values = dict()
        reserved_names = {self.SERVICE_ENDPOINT, 'type'}
        if values:
            for name, value in values.items():
                if name not in reserved_names:
                    self._values[name] = value

    @property
    def type(self):
        """
        Type of the service.

        :return: str
        """
        return self._type

    @property
    def index(self):
        """
        Identifier of the service inside the asset DDO

        :return: str
        """
        return self._index

    @property
    def service_endpoint(self):
        """
        Service endpoint.

        :return: String
        """
        return self._service_endpoint

    def set_service_endpoint(self, service_endpoint):
        """
        Update service endpoint. Needed to update after create did.

        :param service_endpoint: Service endpoint, str
        """
        self._service_endpoint = service_endpoint

    def values(self):
        """

        :return: array of values
        """
        return self._values.copy()

    @property
    def attributes(self):
        return self._values['attributes']

    @property
    def main(self):
        return self._values['attributes']['main']

    def update_value(self, name, value):
        """
        Update value in the array of values.

        :param name: Key of the value, str
        :param value: New value, str
        :return: None
        """
        if name not in {'id', self.SERVICE_ENDPOINT, 'type'}:
            self._values[name] = value

    def as_text(self, is_pretty=False):
        """Return the service as a JSON string."""
        values = {
            'type': self._type,
            self.SERVICE_ENDPOINT: self._service_endpoint,
        }
        if self._values:
            # add extra service values to the dictionary
            for name, value in self._values.items():
                values[name] = value

        if is_pretty:
            return json.dumps(values, indent=4, separators=(',', ': '))

        return json.dumps(values)

    def as_dictionary(self):
        """Return the service as a python dictionary."""
        values = {
            'type': self._type,
            self.SERVICE_ENDPOINT: self._service_endpoint,
        }
        if self._values:
            # add extra service values to the dictionary
            for name, value in self._values.items():
                if isinstance(value, object) and hasattr(value, 'as_dictionary'):
                    value = value.as_dictionary()
                elif isinstance(value, list):
                    value = [v.as_dictionary() if hasattr(v, 'as_dictionary') else v for v in value]

                values[name] = value
        return values

    @classmethod
    def from_json(cls, service_dict):
        """Create a service object from a JSON string."""
        sd = service_dict.copy()
        service_endpoint = sd.get(cls.SERVICE_ENDPOINT)
        if not service_endpoint:
            logger.error(
                'Service definition in DDO document is missing the "serviceEndpoint" key/value.')
            raise IndexError

        _type = sd.get('type')
        _index = sd.get('index')
        if not _type:
            logger.error('Service definition in DDO document is missing the "type" key/value.')
            raise IndexError

        sd.pop(cls.SERVICE_ENDPOINT)
        sd.pop('type')
        return cls(
            service_endpoint,
            _type,
            sd,
            _index
        )
