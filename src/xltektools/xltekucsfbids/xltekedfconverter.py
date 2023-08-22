"""xltekedfconverter.py
A HDF5 file which contains data for XLTEK EEG data.
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
from typing import Any

# Third-Party Packages #
from baseobjects import BaseObject
from pyedflib import highlevel

# Local Packages #
from ..xltekcdfs import XLTEKCDFS


# Definitions #
# Classes #
class XLTEKEDFConverter(BaseObject):

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        bids_session: None = None,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.bids_session: None = None
        self.cdfs: None = None

        # Parent Attributes #
        super().__init__(init=False, **kwargs)

        # Object Construction #
        if init:
            self.construct(
                **kwargs,
            )
