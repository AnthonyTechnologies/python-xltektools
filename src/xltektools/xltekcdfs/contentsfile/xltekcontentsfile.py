""" xltekcontentsfile.py

"""
# Package Header #
from ...header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from collections.abc import Mapping, Iterable
import datetime

# Third-Party Packages #
from hdf5objects import HDF5Map, HDF5Group
from cdfs.contentsfile import TimeContentsFileMap, TimeContentsFile, ContentsFileComponent, TimeContentGroupComponent

# Local Packages #
from .data import XLTEKDataContentGroupMap
from .video import XLTEKVideoContentGroupMap


# Definitions #
# Classes #
class XLTEKContentsFileMap(TimeContentsFileMap):
    """A map for BaseHDF5 files."""
    default_attribute_names = TimeContentsFileMap.default_attribute_names | {
        "subject_id": "subject_id",
        "age": "age",
        "sex": "sex",
        "species": "species",
        "units": "units",
    }
    default_attributes = TimeContentsFileMap.default_attributes | {
        "age": "",
        "sex": "U",
        "species": "Homo Sapien",
        "units": "volts"
    }
    default_map_names = TimeContentsFileMap.default_map_names | {"video_contents": "video_contents"}
    default_maps = {
        "contents": XLTEKDataContentGroupMap(),
        "video_contents": XLTEKVideoContentGroupMap(),
    }


class XLTEKContentsFile(TimeContentsFile):
    FILE_TYPE: str = "ContentsFile"
    default_map: HDF5Map = XLTEKContentsFileMap()
    default_component_types = {
        "contents": (ContentsFileComponent, {"root_location": "contents"}),
        "videos": (ContentsFileComponent, {"root_location": "video_contents"}),
    }

    @property
    def video_root(self) -> HDF5Group:
        return self.components["videos"].get_root()

    @property
    def video_root_node(self) -> TimeContentGroupComponent:
        return self.components["videos"].get_root_node_component()

    def build_swmr(
        self,
        paths: Iterable[str | Iterable[str], ...],
        starts: Iterable[datetime.date],
        **kwargs,
    ) -> None:
        for entry_paths, start in zip(paths, starts):
            self.contents_root_node.insert_recursive_entry(paths=entry_paths, start=start)
            self.video_root_node.insert_recursive_entry(paths=entry_paths, start=start)
