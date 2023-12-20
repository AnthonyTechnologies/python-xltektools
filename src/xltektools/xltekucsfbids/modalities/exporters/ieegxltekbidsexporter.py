"""xlteksessionbidsexporter.py

"""
# Package Header #
from ....header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from collections.abc import Iterable
import datetime
from pathlib import Path
import shutil
from typing import Any

# Third-Party Packages #
from baseobjects.functions import MethodMultiplexer, CallableMultiplexObject
from ucsfbids.modalities.exporters import IEEGBIDSExporter

# Local Packages #
from ....xltekcdfs import XLTEKCDFSEDFExporter
from ..ieegxltek import IEEGXLTEK


# Definitions #
# Classes #
class IEEGXLTEKBIDSExporter(IEEGBIDSExporter, CallableMultiplexObject):

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        modality: None = None,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.cdfs_exporter: XLTEKCDFSEDFExporter | None = None
        self.export_data: MethodMultiplexer = MethodMultiplexer(instance=self, select="export_data_as_days")

        # Parent Attributes #
        super().__init__(init=False, **kwargs)

        # Object Construction #
        if init:
            self.construct(
                modality=modality,
                **kwargs,
            )

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        modality: None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:

        """
        super().construct(modality=modality, **kwargs)

        if self.cdfs_exporter is None:
            self.cdfs_exporter = XLTEKCDFSEDFExporter(cdfs=self.modality.require_cdfs(load=True))

    def load_channels(self) -> list[str, ...]:
        channel_names = list(self.modality.load_electrodes()["name"])
        n_channels = len(channel_names)
        if n_channels < 4 or tuple(channel_names[-4:]) != ("TRIG", "OSAT", "PR", "Pleth"):
            if n_channels > 128:
                channel_names.extend((f"BLANK{i + 1}" for i in range(n_channels, 256)))
            else:
                channel_names.extend((f"BLANK{i + 1}" for i in range(n_channels, 128)))
            channel_names.extend((f"DC{i + 1}" for i in range(16)))
            channel_names.extend(("TRIG", "OSAT", "PR", "Pleth"))

        return channel_names

    # IEEG
    def export_data_as_days(self, path: Path, name: str) -> None:
        self.cdfs_exporter.channel_names.clear()
        self.cdfs_exporter.channel_names.extend(self.load_channels())
        self.cdfs_exporter.export_as_days(path=path, name=name)

    def execute_export(self, path: Path, name: str) -> None:
        new_path = path / f"{self.modality.name}"
        new_path.mkdir(exist_ok=True)
        self.export_select_files(path=new_path, name=name)
        self.export_data(path=new_path, name=name)


# Assign exporter
IEEGXLTEK.default_exporters["BIDS"] = IEEGXLTEKBIDSExporter
