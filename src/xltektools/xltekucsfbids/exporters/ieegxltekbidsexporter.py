"""ieegxltekbidsexporter.py

"""
# Package Header #
from xltektools.header import *

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
from baseobjects.functions import MethodMultiplexer, CallableMultiplexObject
from ucsfbids.exporters import IEEGBIDSExporter

# Local Packages #
from ...xltekcdfs import XLTEKCDFSEDFExporter
from ..modalities import IEEGXLTEK


# Definitions #
# Classes #
class IEEGXLTEKBIDSExporter(IEEGBIDSExporter, CallableMultiplexObject):

    # Attributes #
    cdfs_exporter: XLTEKCDFSEDFExporter | None = None
    export_data: MethodMultiplexer

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        bids_object: Any = None,
        files_names: set[str, ...] | None = None,
        exclude_names: set[str, ...] | None = None,
        name_map: dict[str, str] | None = None,
        type_map: dict[type, type] | None = None,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.export_data: MethodMultiplexer = MethodMultiplexer(instance=self, select="export_data_as_days")

        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(
                bids_object=bids_object,
                files_names=files_names,
                exclude_names=exclude_names,
                name_map=name_map,
                type_map=type_map,
                **kwargs,
            )

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        bids_object: Any = None,
        files_names: set[str, ...] | None = None,
        exclude_names: set[str, ...] | None = None,
        name_map: dict[str, str] | None = None,
        type_map: dict[type, type] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            bids_object: The UCSFBIDS object to export.
            files_names: The set of file names to export.
            exclude_names: The set of file names to exclude from export.
            name_map: A mapping of names.
            type_map: A mapping of types.
            **kwargs: Additional keyword arguments.
        """
        super().construct(
            bids_object=bids_object,
            files_names=files_names,
            exclude_names=exclude_names,
            name_map=name_map,
            type_map=type_map,
            **kwargs,
        )

        if self.cdfs_exporter is None:
            self.cdfs_exporter = XLTEKCDFSEDFExporter(cdfs=self.bids_object.components["cdfs"].get_cdfs())

    def load_channels(self) -> list[str, ...]:
        channel_names = list(self.bids_object.load_electrodes()["name"])
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

    def execute_export(
        self,
        path: Path,
        name: str | None = None,
        files: bool | set[str, ...] | None = True,
        **kwargs: Any,
    ) -> None:
        """Executes the export process for the modality.

        Args:
            path: The root path to export the modality to.
            name: The new name of the exported modality. Defaults to None, retaining the original name.
            files: A set of files to export or a boolean indicating whether to export files.
            **kwargs: Additional keyword arguments.
        """
        if name is None:
            name = self.bids_object.full_name

        new_path = path / f"{self.bids_object.name}"
        new_path.mkdir(exist_ok=True)
        if files or files is None:
            self.export_files(path=new_path, name=name, files=files)

        self.export_data(path=new_path, name=name)


# Assign exporter
IEEGXLTEK.exporters["BIDS"] = (IEEGXLTEKBIDSExporter, {})
