#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.keeper.contract_handler import ContractHandler
from ocean_utils.ocean.ocean import Ocean


def init_ocean(web3, account=None):
    """
    Create an ocean instance with all the contracts deployed.

    :param web3: Web3 instance
    :param account: Account address, str
    :return: Ocean instance
    """
    ocn = Ocean()
    token_contract = deploy_contract(web3, account, 'OceanToken')
    ContractHandler.set('OceanToken', token_contract)
    ContractHandler.set('DIDRegistry', deploy_contract(web3, account, 'DIDRegistry'))
    ContractHandler.set('OceanMarket',
                        deploy_contract(web3, account, 'OceanMarket', token_contract.address))
    service_agreement_contract = deploy_contract(web3, account, 'ServiceExecutionAgreement')
    ContractHandler.set('ServiceExecutionAgreement', service_agreement_contract)
    ContractHandler.set('PaymentConditions', deploy_contract(web3, account, 'PaymentConditions',
                                                             service_agreement_contract.address,
                                                             token_contract.address))
    ContractHandler.set('AccessConditions', deploy_contract(web3, account, 'AccessConditions',
                                                            service_agreement_contract.address))
    return ocn


def deploy_contract(web3, account, contract_name, *args):
    """
    Deploy a json abi artifact on the chain that web3 is connected.

    :param web3: Web3 instance
    :param account: Account address, str
    :param contract_name: Contract name, str
    :param args: Args that the contract need to be deployed. Should be a list.
    :return: Contract instance
    """
    web3.eth.defaultAccount = account
    contract_instance = ContractHandler.get_contract_dict_by_name(contract_name)
    contract_initial = web3.eth.contract(abi=contract_instance['abi'],
                                         bytecode=contract_instance['bytecode'])
    # Using deploy because the new option constructor().transact() is not stable now.
    # https://github.com/ethereum/web3.py/issues/1193
    tx_hash = contract_initial.deploy(transaction={'from': account}, args=args)
    web3.eth.waitForTransactionReceipt(web3.toHex(tx_hash))
    tx_receipt = web3.eth.getTransactionReceipt(web3.toHex(tx_hash))
    contract = web3.eth.contract(
        abi=contract_instance['abi'],
        address=tx_receipt['contractAddress']
    )
    return contract
