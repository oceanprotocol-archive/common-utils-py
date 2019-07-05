"""
    Public key HEX

"""


#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from .public_key_base import PUBLIC_KEY_STORE_TYPE_HEX, PublicKeyBase

AUTHENTICATION_TYPE_HEX = 'HexVerificationKey'
PUBLIC_KEY_TYPE_HEX = 'PublicKeyHex'


class PublicKeyHex(PublicKeyBase):
    """Encode key value using Hex."""

    def __init__(self, key_id, **kwargs):
        PublicKeyBase.__init__(self, key_id, **kwargs)
        self._type = PUBLIC_KEY_TYPE_HEX
        self._store_type = PUBLIC_KEY_STORE_TYPE_HEX

    def get_authentication_type(self):
        """Return the type of authentication supported by this class."""
        return AUTHENTICATION_TYPE_HEX
