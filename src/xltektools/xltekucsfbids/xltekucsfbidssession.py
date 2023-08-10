"""xltekcdfs.py

"""
# Package Header #
from ..header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #


# Third-Party Packages #
from ucsfbids.sessions import CDFSSession

# Local Packages #
from ..xltekcdfs import XLTEKCDFS


# Definitions #
# Classes #
class XLTEKUCSFBIDSSession(CDFSSession):
    """

    Class Attributes:

    Attributes:

    Args:

    """

    default_meta_info: dict = {
        "SessionType": "XLTEKCDFS"
    }
    cdfs_type: type[XLTEKCDFS] = XLTEKCDFS
