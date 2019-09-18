#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.agreements.service_agreement_condition import Event, ServiceAgreementCondition


class ServiceAgreementTemplate(object):
    """Class representing a Service Agreement Template."""
    TEMPLATE_ID_KEY = 'templateId'

    def __init__(self, template_id=None, name=None, creator=None, template_json=None):
        self.template_id = template_id
        self.name = name
        self.creator = creator
        self.template = {}
        if template_json:
            self.parse_template_json(template_json)

    def parse_template_json(self, template_json):
        """
        Parse a template from a json.

        :param template_json: json dict
        """
        if 'template' in template_json['serviceAgreementTemplate']:
            self.template = template_json['serviceAgreementTemplate']['template']
        else:
            self.template = template_json['serviceAgreementTemplate']

    def set_template_id(self, template_id):
        """
        Assign the template id to the template.

        :param template_id: string
        """
        self.template_id = template_id

    @property
    def fulfillment_order(self):
        """
        List with the fulfillment order.

        :return: list
        """
        return self.template['fulfillmentOrder']

    @property
    def condition_dependency(self):
        """
        Dictionary with the dependencies of the conditions.

        :return: dict
        """
        return self.template['conditionDependency']

    @property
    def contract_name(self):
        """
        Contract name of the template.

        :return: string
        """
        return self.template['contractName']

    @property
    def agreement_events(self):
        """
        List of agreements events.

        :return: list
        """
        return [Event(e) for e in self.template['events']]

    @property
    def conditions(self):
        """
        List of conditions.

        :return: list
        """
        return [
            ServiceAgreementCondition(cond_json) for cond_json in self.template['conditions']
        ]

    def set_conditions(self, conditions):
        """
        Set the conditions of the template.

        :param conditions: list of conditions.
        """
        self.template['conditions'] = [cond.as_dictionary() for cond in conditions]

    def get_event_to_args_map(self, contract_by_name):
        """
        keys in returned dict have the format <contract_name>.<event_name>
        """
        cond_contract_tuples = [(cond, contract_by_name[cond.contract_name]) for cond in
                                self.conditions]
        event_to_args = {
            f'{cond.contract_name}.{cond.events[0].name}': (
                contract.get_event_argument_names(cond.events[0].name)
            )
            for cond, contract in cond_contract_tuples
        }
        agr_event_key = f'{self.contract_name}.{self.agreement_events[0].name}'
        event_to_args[agr_event_key] = contract_by_name[
            self.contract_name].get_event_argument_names(
            self.agreement_events[0].name
        )

        return event_to_args

    def as_dictionary(self):
        """
        Return the service agreement template as a dictionary.

        :return: dict
        """
        template = {
            'contractName': self.contract_name,
            'events': [e.as_dictionary() for e in self.agreement_events],
            'fulfillmentOrder': self.fulfillment_order,
            'conditionDependency': self.condition_dependency,
            'conditions': [cond.as_dictionary() for cond in self.conditions]
        }
        return {
            # 'type': self.DOCUMENT_TYPE,
            'name': self.name,
            'creator': self.creator,
            'serviceAgreementTemplate': template
        }
