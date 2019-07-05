#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.keeper.templates.template_manager import TemplateStoreManager
from tests.resources.tiers import e2e_test

template_store_manager = TemplateStoreManager('TemplateStoreManager')


@e2e_test
def test_template():
    assert template_store_manager.get_num_templates() == 1
