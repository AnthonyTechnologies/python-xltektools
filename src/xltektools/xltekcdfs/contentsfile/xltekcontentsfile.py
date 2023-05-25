""" xltekcontentsfile.py

"""
import pathlib

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
from pathlib import Path

# Third-Party Packages #
from hdf5objects import HDF5Map, HDF5Group
from cdfs.contentsfile import TimeContentsFileMap, TimeContentsFile, ContentsFileComponent, TimeContentGroupComponent

# Local Packages #
from ...hdf5xltek import HDF5XLTEK
from .data import XLTEKDataContentGroupMap
from .video import XLTEKVideoContentGroupMap


# Definitions #
# Classes #
class XLTEKContentsFileComponent(ContentsFileComponent):
    file_type = HDF5XLTEK

    def correct_entry(self, node_group, index, entry, path):
        node_map_component = node_group.node_map.components["tree_node"]
        if not path.is_file():
            node_map_component.delete_entry(index)
        else:
            with self.file_type.new_validated(path) as file:
                node_map_component.set_entry(
                    index=index,
                    start=file.start_datetime if file.start_datetime != entry["Start"] else None,
                    end=file.end_datetime if file.end_datetime != entry["End"] else None,
                    sample_rate=file.start_datetime if file.sample_rate != entry["Sample Rate"] else None,
                    min_shape=file.start_datetime if file.data.shape != entry["Minimum Shape"] else None,
                    max_shape=file.start_datetime if file.data.shape != entry["Maximum Shape"] else None,
                )

    def _correct_contents(self, path: Path, node_group):
        node_map_component = node_group.node_map.components["tree_node"]

        # Correct registered entries
        registered = set()
        for i, frame_info in node_map_component.entry_iter():
            child_path = path / frame_info["Path"]
            ref = frame_info.get("Node", False)
            if ref:
                child_node_component = self.composite[ref].components["tree_node"]
                self._correct_contents(child_path, child_node_component)
                if child_node_component.node_map.size == 0:
                    min_shape = (0, 0)
                    max_shape = (0, 0)
                    sample_rate = None
                else:
                    min_shape = child_node_component.min_shape
                    max_shape = child_node_component.max_shape
                    sample_rate = child_node_component.sample_rate
                node_map_component.set_entry(
                    index=i,
                    start=child_node_component.get_start_datetime(),
                    end=child_node_component.get_end_datetime(),
                    min_shape=min_shape,
                    max_shape=max_shape,
                    sample_rate=sample_rate,
                )
            else:
                self.correct_entry(node_group, i, frame_info, child_path)
                registered.add(child_path)

        # Correct unregistered
        for new_path in set(path.glob("*.h5")) - registered:
            file = self.file_type.new_validated(new_path)
            if file is not None:
                node_group.require_child_start(
                    path=file.path.name,
                    start=file.start_datetime,
                    end=file.end_datetime,
                    sample_rate=file.sample_rate,
                    min_shape=file.data.shape,
                    max_shape=file.data.shape,
                )
                file.close()

    def correct_contents(self, path: pathlib.Path | None = None):
        if path is None:
            path = self.composite.path.parent

        self._correct_contents(path, self.get_root_node_component())

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
        "contents": (XLTEKContentsFileComponent, {"root_location": "contents"}),
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
            self.contents_root_node.insert_recursive_entry(
                paths=entry_paths,
                start=start,
                min_shape=(0, 0),
                max_shape=(0, 0),
            )
            self.video_root_node.insert_recursive_entry(paths=entry_paths, start=start)
