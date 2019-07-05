"""Asset module."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from ocean_utils.ddo.ddo import DDO


class Asset(DDO):
    """Class representing an asset base in a DDO object."""

    @property
    def encrypted_files(self):
        """Return encryptedFiles field in the base metadata."""
        files = self.metadata['base']['encryptedFiles']
        return files
