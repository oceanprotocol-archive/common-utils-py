#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import os
import pathlib

from ocean_keeper.utils import get_account

from ocean_utils.ddo.ddo import DDO

PUBLISHER_INDEX = 1
CONSUMER_INDEX = 0


def get_resource_path(dir_name, file_name):
    base = os.path.realpath(__file__).split(os.path.sep)[1:-1]
    if dir_name:
        return pathlib.Path(os.path.join(os.path.sep, *base, dir_name, file_name))
    else:
        return pathlib.Path(os.path.join(os.path.sep, *base, file_name))


def get_publisher_account():
    return get_account(0)


def get_consumer_account():
    return get_account(1)


def get_ddo_sample():
    return DDO(json_filename=get_resource_path('ddo', 'ddo_sa_sample.json'))


def log_event(event_name):
    def _process_event(event):
        print(f'Received event {event_name}: {event}')

    return _process_event


def get_metadata():
    path = get_resource_path('ddo', 'valid_metadata.json')
    assert path.exists(), f"{path} does not exist!"
    with open(path, 'r') as file_handle:
        metadata = file_handle.read()
    return json.loads(metadata)
