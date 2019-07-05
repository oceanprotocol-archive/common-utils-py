import os

from eth_utils import add_0x_prefix
from web3 import Web3

from ocean_utils import ConfigProvider
from ocean_utils.keeper import Keeper
from ocean_utils.keeper.web3_provider import Web3Provider
from ocean_utils.utils.utilities import prepare_prefixed_hash
from tests.resources.helper_functions import get_publisher_account, get_resource_path
from tests.resources.tiers import e2e_test


@e2e_test
def test_keeper_instance():
    keeper = Keeper()
    assert keeper
    assert isinstance(keeper.get_instance(), Keeper)


def test_ec_recover():
    test_values = [
        ('0xe2DD09d719Da89e5a3D0F2549c7E24566e947260',
         'c80996119e884cb38599bcd96a22ad3eea3a4734bcfb47959a5d41ecdcbdfe67',
         '0xa50427a9d5beccdea3eeabecfc1014096b35cd05965e772e8ea32477d2f217'
         'c30d0ec5dbf6b14de1d6eeff45011d17490fe5126576b20d2cbada828cb068c9f801'),
        ('0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e',
         'd77c3a84cafe4cb8bc28bf41a99c63fd530c10da33a54acf94e8d1369d09fbb2',
         '0x9076b561e554cf657af333d9680ba118d556c5b697622636bce4b02f4d5632'
         '5a0ea6a474ca85291252c8c1b8637174ee32072bef357bb0c21b0db4c25b379e781b'),
        ('0xe2DD09d719Da89e5a3D0F2549c7E24566e947260',
         '8d5c1065a9c74da59fbb9e41d1f196e40517e92d81b14c3a8143d6887f3f4438',
         '0x662f6cffd96ada4b6ce5497d444c92126bd053ab131915332edf0dbba716ba'
         '82662275670c95eb2a4d65245cac70313c25e34f594d7c0fbca5232c3d5701a57e00')
    ]

    for expected_address, document_id, signed_document_id in test_values:
        rec_address = Keeper.get_instance().ec_recover(document_id, signed_document_id)
        assert expected_address.lower() == rec_address.lower()


def test_artifacts_path():
    config = ConfigProvider.get_config()
    artifacts_path = '/some/other/path'
    keeper = Keeper.get_instance(artifacts_path)
    assert keeper.artifacts_path == artifacts_path

    artifacts_path = config.keeper_path
    keeper = Keeper.get_instance()
    assert keeper.artifacts_path == artifacts_path


@e2e_test
def test_get_network_id():
    network_id = Keeper.get_network_id()
    assert isinstance(network_id, int)
    assert network_id in Keeper._network_name_map


@e2e_test
def test_get_network_name():
    name = Keeper.get_network_name(Keeper.get_network_id())
    assert name in Keeper._network_name_map.values()
    os.environ['KEEPER_NETWORK_NAME'] = 'yellow'
    assert 'KEEPER_NETWORK_NAME' in os.environ
    name = Keeper.get_network_name(Keeper.get_network_id())
    assert name == 'yellow'
    del os.environ['KEEPER_NETWORK_NAME']

    assert Keeper.get_network_name(1) == Keeper._network_name_map.get(1)
    assert Keeper.get_network_name(2) == Keeper._network_name_map.get(2)
    assert Keeper.get_network_name(3) == Keeper._network_name_map.get(3)
    assert Keeper.get_network_name(4) == Keeper._network_name_map.get(4)
    assert Keeper.get_network_name(42) == Keeper._network_name_map.get(42)
    assert Keeper.get_network_name(77) == Keeper._network_name_map.get(77)
    assert Keeper.get_network_name(99) == Keeper._network_name_map.get(99)
    assert Keeper.get_network_name(8995) == Keeper._network_name_map.get(8995)
    assert Keeper.get_network_name(8996) == Keeper._network_name_map.get(8996)
    assert Keeper.get_network_name(0) == 'development'


@e2e_test
def test_verify_signature(consumer_ocean_instance):
    """
    ocean_utils currently uses `web3.eth.sign()` to sign the service agreement hash. This signing
    method
    uses ethereum `eth_sign` on the ethereum client which automatically prepends the
    message with text defined in EIP-191 as version 'E': `b'\\x19Ethereum Signed Message:\\n'`
    concatenated with the number of bytes in the message.

    It is more convenient to sign a message using `web3.eth.sign()` because it only requires the
    account address
    whereas `web3.eth.account.signHash()` requires a private_key to sign the message.
    `web3.eth.account.signHash()` also does not prepend anything to the message before signing.
    Messages signed via Metamask in pleuston use the latter method and currently fail to verify in
    ocean_utils/brizo.
    The signature verification fails because recoverHash is being used on a prepended message but
    the signature
    created by `web3.eth.account.signHash()` does not add a prefix before signing.
    """
    w3 = Web3Provider.get_web3()

    # Signature created from Metamask (same as using `web3.eth.account.signHash()`)
    address = '0x8248039e67801Ac0B9d0e38201E963194abdb540'
    hex_agr_hash = '0xc8ea6bf6f4f4e2bf26a645dd4a1be20f5151c74964026c36efc2149bfae5f924'
    agreement_hash = Web3.toBytes(hexstr=hex_agr_hash)
    assert hex_agr_hash == '0x' + agreement_hash.hex()
    signature = (
        '0x200ce6aa55f0b4080c5f3a5dbe8385d2d196b0380cbdf388f79b6b004223c68a4f7972deb36417df8599155da2f903e43fe7e7eb40214db6bd6e55fd4c4fcf2a1c'
    )
    recovered_address = w3.eth.account.recoverHash(agreement_hash, signature=signature)
    assert address == recovered_address, f'Could not verify signature using address {address}'

    # Signature created using `web3.eth.sign()` (squid-py, squid-js with no metamask)
    address = "0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e"
    hex_agr_hash = "0xeeaae0098b39fdf8fab6733152dd0ef54729ac486f9846450780c5cc9d44f5e8"
    agreement_hash = Web3.toBytes(hexstr=hex_agr_hash)
    signature = (
        "0x44fa549d33f5993f73e96f91cad01d9b37830da78494e35bda32a280d1b864ac020a761e872633c8149a5b63b65a1143f9f5a3be35822a9e90e0187d4a1f9d101c"
    )
    assert hex_agr_hash == add_0x_prefix(agreement_hash.hex())
    prefixed_hash = prepare_prefixed_hash(agreement_hash)
    recovered_address = w3.eth.account.recoverHash(prefixed_hash, signature=signature)
    assert address == recovered_address, f'Could not verify signature using address {address}'


@e2e_test
def test_sign_and_recover():
    config = ConfigProvider.get_config()
    w3 = Web3Provider.get_web3(config)
    account = get_publisher_account(config)
    msg = 'testing-signature-and-recovery-of-signer-address'
    msg_hash = w3.sha3(text=msg)
    signature = Keeper.sign_hash(msg_hash, account)
    address = w3.toChecksumAddress(Keeper.ec_recover(msg_hash, signature))
    assert address == account.address

    # Signature created on msg with the ethereum prefix. `web3.eth.account.recoverHash` does NOT
    # add any prefixes to the message, so we have to add the prefix before the call.
    prefixed_hash = prepare_prefixed_hash(msg_hash)
    address = w3.eth.account.recoverHash(prefixed_hash, signature=signature)
    assert address == account.address

    # Now do the opposite, sign with eth.account.signHash() (using prefixed msg hash),
    # then recover address with Keeper.ec_recover() on the msg hash with no prefix.
    with open(get_resource_path('data', 'publisher_key_file.json')) as kf:
        key = kf.read()
    prvkey = w3.eth.account.decrypt(key, account.password)
    account_sig_prefixed = add_0x_prefix(w3.eth.account.signHash(prefixed_hash, prvkey)['signature'].hex())
    assert Keeper.ec_recover(msg_hash, account_sig_prefixed) == account.address.lower()


@e2e_test
def test_get_condition_name_by_address():
    keeper = Keeper.get_instance()
    name = keeper.get_condition_name_by_address(keeper.lock_reward_condition.address)
    assert name == 'lockReward'

    name = keeper.get_condition_name_by_address(keeper.access_secret_store_condition.address)
    assert name == 'accessSecretStore'

    name = keeper.get_condition_name_by_address(keeper.escrow_reward_condition.address)
    assert name == 'escrowReward'
