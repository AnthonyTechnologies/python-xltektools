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
from collections.abc import Mapping

# Third-Party Packages #
from hdf5objects import HDF5Map
from cdfs.contentsfile import TimeContentsFileMap, TimeContentsFile, TimeNodeMap, TimeLeafMap, ContentsFileComponent

# Local Packages #
from .xltekdatamaps import XLTEKDataContentGroupMap


# Definitions #
# Classes #
class XLTEKContentsFileMap(TimeContentsFileMap):
    """A map for BaseHDF5 files."""
    default_attribute_names = TimeContentsFileMap.default_attribute_names | {
        "subject_id": "subject_id",
        "age": "age",
        "sex": "sex",
        "species": "species",
    }
    default_attributes = TimeContentsFileMap.default_attributes | {"age": "", "sex": "U", "species": "Homo Sapien"}
    default_maps: Mapping[str, HDF5Map] = {
        "data_content": XLTEKDataContentGroupMap(),
    }


class XLTEKContentsFile(TimeContentsFile):
    FILE_TYPE: str = "ContentsFile"
    default_map: HDF5Map = XLTEKContentsFileMap()
    default_component_types = {"contents": (ContentsFileComponent, {"data_location": "data_content"})}
