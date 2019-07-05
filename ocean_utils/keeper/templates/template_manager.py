#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from ocean_utils.keeper import ContractBase

AgreementTemplate = namedtuple(
    'AgreementTemplate',
    ('state', 'owner', 'updated_by', 'block_number_updated')
)


class TemplateStoreManager(ContractBase):
    """Class representing the TemplateStoreManager contract."""
    CONTRACT_NAME = 'TemplateStoreManager'

    def get_template(self, template_id):
        """
        Get the template for a given template id.

        :param template_id: id of the template, str
        :return:
        """
        template = self.contract_concise.getTemplate(template_id)
        if template and len(template) == 4:
            return AgreementTemplate(*template)

        return None

    def propose_template(self, template_id, from_account):
        """Propose a template.

        :param template_id: id of the template, str
        :param from_account: Account
        :return: bool
        """
        tx_hash = self.send_transaction(
            'proposeTemplate',
            (template_id,),
            transact={'from': from_account.address,
                      'passphrase': from_account.password,
                      'keyfile': from_account.key_file}
        )
        return self.is_tx_successful(tx_hash)

    def approve_template(self, template_id, from_account):
        """
        Approve a template.

        :param template_id: id of the template, str
        :param from_account: Account
        :return:
        """
        tx_hash = self.send_transaction(
            'approveTemplate',
            (template_id,),
            transact={'from': from_account.address,
                      'passphrase': from_account.password,
                      'keyfile': from_account.key_file}
        )
        return self.is_tx_successful(tx_hash)

    def revoke_template(self, template_id, from_account):
        """
        Revoke a template.

        :param template_id: id of the template, str
        :param from_account: Account
        :return: bool
        """
        tx_hash = self.send_transaction(
            'revokeTemplate',
            (template_id,),
            transact={'from': from_account.address,
                      'passphrase': from_account.password,
                      'keyfile': from_account.key_file}
        )
        return self.is_tx_successful(tx_hash)

    def is_template_approved(self, template_id):
        """
        True if the template is approved.

        :param template_id: id of the template, str
        :return: bool
        """
        return self.contract_concise.isTemplateApproved(template_id)

    def get_num_templates(self):
        """
        Return the number of templates on-chain.

        :return: number of templates, int
        """
        return self.contract_concise.getTemplateListSize()
