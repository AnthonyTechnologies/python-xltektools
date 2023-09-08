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
from pathlib import Path
from typing import Any

# Third-Party Packages #
from baseobjects import BaseObject
import numpy as np
from pyedflib.highlevel import make_signal_headers, make_header, write_edf

# Local Packages #
from ..xltekcdfs import XLTEKCDFS


# Definitions #
# Classes #
class XLTEKCDFSEDFConverter(BaseObject):

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        cdfs: None = None,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.cdfs: None = None
        self.channel_list: list = []

        # Parent Attributes #
        super().__init__(init=False, **kwargs)

        # Object Construction #
        if init:
            self.construct(
                cdfs=cdfs,
                **kwargs,
            )

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        cdfs: None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:

        """

        if cdfs is not None:
            self.cdfs = cdfs

        super().construct(**kwargs)

    def formated_save_edf(
        self,
        path: Path,
        signals: list | np.ndarray,
        signal_headers: list[dict[str, Any]],
        header: dict[str, Any],
        digital: bool = False,
        file_type: int = -1,
    ) -> None:
        write_edf(
            edf_file=path.as_posix(),
            signals=signals,
            signal_headers=signal_headers,
            header=header,
            digital=digital,
            file_type=file_type,
        )

    def save_edf(
        self,
        path: Path,
        signals: list | np.ndarray,
        signal_names: list[str],
        signal_kwargs: dict[str, Any],
        header_kwargs: dict[str, Any],
        digital: bool = False,
        file_type: int = -1,
    ) -> None:
        self.formated_save_edf(
            path=path,
            signals=signals,
            signal_headers=make_signal_headers(signal_names, **signal_kwargs),
            header=make_header(**header_kwargs),
            digital=digital,
            file_type=file_type,
        )

    def convert_edf_day(self):
        self.cdfs.data.validate
