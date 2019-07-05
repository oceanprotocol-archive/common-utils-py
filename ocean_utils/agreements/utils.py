"""Agreements module."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import os
import time

from ocean_utils.agreements.service_types import ServiceTypes
from ocean_utils.keeper import Keeper
from ocean_utils.keeper.utils import process_tx_receipt


def process_fulfill_condition(args, condition_contract, condition_id, logger, num_tries=10):
    keeper = Keeper.get_instance()
    contract_name = condition_contract.CONTRACT_NAME
    agreement_id = args[0]
    for i in range(num_tries):
        try:
            tx_hash = condition_contract.fulfill(
                *args
            )
            success = process_tx_receipt(
                tx_hash,
                getattr(condition_contract.contract.events, condition_contract.FULFILLED_EVENT)(),
                f'{contract_name}.Fulfilled'
            )
            if success or keeper.condition_manager.get_condition_state(condition_id) == 2:
                logger.info(f'Done {contract_name}.fulfill for agreement {agreement_id}')
                break

            logger.debug(f'done trial {i} {contract_name}.fulfill for agreement {agreement_id}, success?: {bool(success)}')
            time.sleep(2)

        except Exception as e:
            if keeper.condition_manager.get_condition_state(condition_id) == 2:
                logger.info(f'Done {contract_name}.fulfill for agreement {agreement_id}')
                break

            logger.debug(f'{contract_name}.fulfill error {agreement_id}: {e}', exc_info=1)
            if i == (num_tries-1):
                logger.debug(f'{contract_name}.fulfill for agreement {agreement_id} FAILED with error: {e}')
            else:
                logger.debug(f'Error when doing {contract_name}.fulfill for agreement {agreement_id}: retrying trial # {i}')
                time.sleep(2)


def get_sla_template_path(service_type=ServiceTypes.ASSET_ACCESS):
    """
    Get the template for a ServiceType.

    :param service_type: ServiceTypes
    :return: Path of the template, str
    """
    if service_type == ServiceTypes.ASSET_ACCESS:
        name = 'access_sla_template.json'
    elif service_type == ServiceTypes.CLOUD_COMPUTE:
        name = 'compute_sla_template.json'
    elif service_type == ServiceTypes.FITCHAIN_COMPUTE:
        name = 'fitchain_sla_template.json'
    else:
        raise ValueError(f'Invalid/unsupported service agreement type {service_type}')

    return os.path.join(os.path.sep, *os.path.realpath(__file__).split(os.path.sep)[1:-1], name)
