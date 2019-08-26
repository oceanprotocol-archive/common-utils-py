"""
    Test did_lib
"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json

import pytest
from ocean_keeper import Keeper
from web3 import Web3

from ocean_utils.ddo.ddo import DDO
from ocean_utils.ddo.public_key_base import (
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_PEM,
    PublicKeyBase)
from ocean_utils.ddo.public_key_rsa import PUBLIC_KEY_TYPE_ETHEREUM_ECDSA, PUBLIC_KEY_TYPE_RSA
from ocean_utils.did import DID
from tests.resources.helper_functions import get_publisher_account, get_resource_path
from tests.resources.tiers import e2e_test, unit_test

public_key_store_types = [
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
]

TEST_SERVICE_TYPE = 'ocean-meta-storage'
TEST_SERVICE_URL = 'http://localhost:8005'

TEST_METADATA = """
{
   "main": {
     "name": "UK Weather information 2011",
     "type": "dataset",
     "dateCreated": "2012-10-10T17:00:000Z",
     "author": "Met Office",
     "license": "CC-BY",
     "files": [
       {
         "url": "https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf",
         "checksum": "efb2c764274b745f5fc37f97c6b0e761",
         "contentLength": "4535431",
         "resourceId": "access-log2018-02-13-15-17-29-18386C502CAEA932"
       }
     ],
     "price": 10
   },
   "curation": {
     "rating": 0.93,
     "numVotes": 123,
     "schema": "Binary Voting"
   },
   "additionalInformation": {
     "updateFrequency": "yearly",
     "structuredMarkup": [
       {
         "uri": "http://skos.um.es/unescothes/C01194/jsonld",
         "mediaType": "application/ld+json"
       },
       {
         "uri": "http://skos.um.es/unescothes/C01194/turtle",
         "mediaType": "text/turtle"
       }
     ]
   }
}
"""

TEST_SERVICES = [
    {
        "type": "Access",
        "purchaseEndpoint": "service",
        "serviceEndpoint": "consume",
        "index": "3",
        "templateId": "0x00000",
    }
]


def generate_sample_ddo():
    did = DID.did({"0":"0x1234"})
    assert did
    ddo = DDO(did)
    assert ddo
    pub_acc = get_publisher_account()

    # add a proof signed with the private key
    signature = Keeper.sign_hash(Web3.sha3(text='checksum'), pub_acc)
    ddo.add_proof('checksum', pub_acc)

    metadata = json.loads(TEST_METADATA)
    ddo.add_service("metadata", f"http://myaquarius.org/api/v1/provider/assets/metadata/{did}",
                    values={'metadata': metadata}, index=0)
    for test_service in TEST_SERVICES:
        if 'values' in test_service:
            values = test_service['values']
        else:
            values = test_service.copy()
            values.pop('type')
            values.pop('serviceEndpoint')

        ddo.add_service(test_service['type'], test_service['serviceEndpoint'], values=values)

    return ddo


@e2e_test
def test_creating_ddo():
    did = DID.did({"0":"0x123908123091283"})
    ddo = DDO(did)
    assert ddo.did == did

    pub_acc = get_publisher_account()

    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)
    assert len(ddo.services) == 1

    ddo_text_no_proof = ddo.as_text()
    assert ddo_text_no_proof

    signature = Keeper.sign_hash(Web3.sha3(text='checksum'), pub_acc)
    ddo.add_proof('checksum', pub_acc, signature)
    ddo_text_proof = ddo.as_text()

    ddo = DDO(json_text=ddo_text_proof)
    assert ddo.is_proof_defined()

    ddo = DDO(json_text=ddo_text_no_proof)
    assert not ddo.is_proof_defined()


@unit_test
def test_creating_ddo_from_scratch():
    # create an empty ddo
    ddo = DDO()
    assert ddo.did == ''
    assert ddo.asset_id is None
    assert ddo.created is not None

    did = DID.did({"0":"0x99999999999999999"})
    ddo.assign_did(did)
    assert ddo.did == did

    pub_acc = get_publisher_account()

    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)

    # add a proof to the first public_key/authentication
    signature = Keeper.sign_hash(Web3.sha3(text='checksum'), pub_acc)
    ddo.add_proof('checksum', pub_acc, signature)
    ddo_text_proof = ddo.as_text()
    assert ddo_text_proof

    pub_acc = get_publisher_account()
    assert not ddo.public_keys
    ddo.add_public_key(did, pub_acc.address)
    assert len(ddo.public_keys) == 1
    assert ddo.get_public_key(0) == ddo.public_keys[0]
    with pytest.raises(IndexError):
        ddo.get_public_key(1)

    assert ddo.get_public_key(did) == ddo.public_keys[0]
    assert ddo.get_public_key('0x32233') is None

    assert not ddo.authentications
    ddo.add_authentication(did, '')
    assert len(ddo.authentications) == 1


@unit_test
def test_create_auth_from_json():
    auth = {'publicKey': '0x00000', 'type': 'auth-type', 'nothing': ''}
    assert DDO.create_authentication_from_json(auth) == \
           {'publicKey': '0x00000', 'type': 'auth-type'}
    with pytest.raises(ValueError):
        DDO.create_authentication_from_json({'type': 'auth-type'})


@unit_test
def test_create_public_key_from_json():
    pkey = {'id': 'pkeyid', 'type': 'keytype', 'owner': '0x00009'}
    pub_key_inst = DDO.create_public_key_from_json(pkey)
    assert isinstance(pub_key_inst, PublicKeyBase)
    assert pub_key_inst.get_id() == pkey['id']
    assert pub_key_inst.get_type() == PUBLIC_KEY_TYPE_ETHEREUM_ECDSA
    assert pub_key_inst.get_owner() == pkey['owner']

    pub_key_inst = DDO.create_public_key_from_json(
        {'type': PUBLIC_KEY_TYPE_RSA}
    )
    assert pub_key_inst.get_id() == ''
    assert pub_key_inst.get_type() == PUBLIC_KEY_TYPE_RSA
    assert pub_key_inst.get_owner() is None


@unit_test
def test_load_ddo_json():
    # TODO: Fix
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), f'{sample_ddo_path} does not exist!'
    with open(sample_ddo_path) as f:
        sample_ddo_json_dict = json.load(f)

    sample_ddo_json_string = json.dumps(sample_ddo_json_dict)

    this_ddo = DDO(json_text=sample_ddo_json_string)
    service = this_ddo.get_service('metadata')
    assert service
    assert service.type == 'metadata'
    assert service.values['attributes']


@unit_test
def test_ddo_dict():
    sample_ddo_path = get_resource_path('ddo', 'ddo_sample1.json')
    assert sample_ddo_path.exists(), f'{sample_ddo_path} does not exist!'

    ddo1 = DDO(json_filename=sample_ddo_path)
    assert len(ddo1.public_keys) == 1
    assert ddo1.did == 'did:op:0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e429'


@unit_test
def test_find_service():
    ddo = generate_sample_ddo()
    service = ddo.find_service_by_id(0)
    assert service and service.type == 'access', 'Failed to find service by integer id.'
    service = ddo.find_service_by_id('0')
    assert service and service.type == 'access', 'Failed to find service by str(int) id.'

    service = ddo.find_service_by_id(1)
    assert service and service.type == 'compute', 'Failed to find service by integer id.'
    service = ddo.find_service_by_id('1')
    assert service and service.type == 'compute', 'Failed to find service by str(int) id.'

    service = ddo.find_service_by_id('access')
    assert service and service.type == 'access', 'Failed to find service by id using service type.'
    assert service.index == '0', 'index not as expected.'

    service = ddo.find_service_by_id('compute')
    assert service and service.type == 'compute', 'Failed to find service by id using service type.'
    assert service.index == '1', 'index not as expected.'


def test_create_ddo(metadata):
    from ocean_utils.utils.utilities import checksum
    from ocean_utils.did import did_to_id_bytes
    pub_acc = get_publisher_account()
    ddo = DDO()
    ddo.add_service('metadata', values=metadata)
    checksums = dict()
    for service in ddo.services:
        checksums[str(service.index)] = checksum(service.main)
    ddo.add_proof(checksums, pub_acc)
    did = ddo.assign_did(DID.did(ddo.proof['checksum']))
    ddo.proof['signatureValue'] = Keeper.sign_hash(did_to_id_bytes(did), pub_acc)
    ddo.add_public_key(did, pub_acc.address)
    ddo.add_authentication(did, PUBLIC_KEY_TYPE_RSA)
