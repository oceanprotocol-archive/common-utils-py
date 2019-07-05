"""Test AccessConditions contract."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.config_provider import ConfigProvider
from ocean_utils.did import DID, did_to_id
from ocean_utils.keeper.conditions.access import AccessSecretStoreCondition
from tests.resources.helper_functions import get_consumer_account
from tests.resources.tiers import e2e_test

access_secret_store_condition = AccessSecretStoreCondition('AccessSecretStoreCondition')


@e2e_test
def test_access_secret_store_condition_contract():
    assert access_secret_store_condition
    assert isinstance(access_secret_store_condition, AccessSecretStoreCondition), \
        f'{access_secret_store_condition} is not instance of AccessSecretStoreCondition'


@e2e_test
def test_check_permissions_not_registered_did():
    consumer_account = get_consumer_account(ConfigProvider.get_config())
    assert not access_secret_store_condition.check_permissions(did_to_id(DID.did()),
                                                               consumer_account.address)

# TODO Create test for check permission after access granted.
