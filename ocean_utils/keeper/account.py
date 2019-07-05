"""Accounts module."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os

logger = logging.getLogger('account')


class Account:
    """Class representing an account."""

    def __init__(self, address, password=None, key_file=None):
        """
        Hold account address, password and path to keyfile.

        :param address: The address of this account
        :param password: account's password. This is necessary for decrypting the private key
            to be able to sign transactions locally
        :param key_file: str path to the encrypted private key file
        """
        self.address = address
        self.password = password
        self._key_file = key_file

    @property
    def key_file(self):
        return os.path.expandvars(os.path.expanduser(self._key_file))
