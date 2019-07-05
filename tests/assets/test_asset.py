"""Test Assets"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from ocean_utils.assets.asset import Asset
from tests.resources.helper_functions import get_resource_path
from tests.resources.tiers import unit_test

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


@unit_test
def test_create_asset_ddo_file():
    # An asset can be created directly from a DDO .json file
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)
    asset1 = Asset(json_filename=sample_ddo_path)
    assert asset1.metadata
    assert asset1.encrypted_files == asset1.metadata['base']['encryptedFiles']
