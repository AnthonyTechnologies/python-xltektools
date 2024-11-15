"""xltekcdfs.py
The main API object for an XLTEK CDFS.
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
from datetime import datetime, tzinfo
from typing import ClassVar, Any

# Third-Party Packages #
from cdfs import BaseCDFS
from sqlalchemy.orm import DeclarativeBase
from sqlalchemyobjects.tables import TableManifestation

# Local Packages #
from .tables import XLTEKMetaInformationTableManifestation, XLTEKContentsTableManifestation
from .xltekcdfsasyncschema import XLTEKCDFSAsyncSchema, XLTEKMetaInformationTable, XLTEKContentsTable
from .components import XLTEKCDFSMetaInformationComponent, XLTEKCDFSContentsComponent


# Definitions #
# Classes #
class XLTEKCDFS(BaseCDFS):
    """The main API object for an XLTEK CDFS.

    This class extends the BaseCDFS class and provides additional functionality specific to XLTEK data files.

    Class Attributes:
        default_component_types: A dictionary defining the default component types and their configurations.

    Attributes:
        _path: The file path to the CDFS.
        _is_open: Indicates if the CDFS is currently open.
        _mode: The mode in which the CDFS is opened (e.g., 'r' for read, 'w' for write).
        _swmr_mode: Indicates if Single-Writer-Multiple-Reader mode is enabled.
        schema: The contents database schema class.
        table_map: A map which outlines which table are within the contents database.
        contents_database_type: The type of the contents database file.
        contents_database_name: The name of the contents database file.
        contents_database: The contents database file object.

    Args:
        path: The path to the CDFS.
        mode: The mode in which the CDFS is opened.
        open_: Whether to open the CDFS.
        create: Whether to create the CDFS.
        build: Whether to build the CDFS.
        load: Whether to load the CDFS.
        contents_name: The name of the contents database file.
        init: Whether to initialize the object.
        **kwargs: Additional keyword arguments.

    """

    # Class Attributes #
    default_component_types: ClassVar[dict[str, tuple[type, dict[str, Any]]]] = {
        "meta_information": (XLTEKCDFSMetaInformationComponent, {}),
        "contents": (XLTEKCDFSContentsComponent, {}),
    }

    # Attributes #
    meta_table_name: str = "meta_information"

    schema: type[DeclarativeBase] | None = XLTEKCDFSAsyncSchema
    table_maps: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] = {
        meta_table_name:  (XLTEKMetaInformationTableManifestation, XLTEKMetaInformationTable, {}),
        "contents": (XLTEKContentsTableManifestation, XLTEKContentsTable, {}),
    }

    # Properties #
    @property
    def meta_information(self) -> dict[str, Any]:
        return self.contents_database.tables[self.meta_table_name].meta_information

    @property
    def name(self) -> str | None:
        """The subject ID from the file attributes."""
        return self.contents_database.tables[self.meta_table_name].meta_information["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.contents_database.tables[self.meta_table_name].set_meta_information(name=value)

    @property
    def start_datetime(self):
        return self.contents_database.tables[self.meta_table_name].meta_information["start"]

    @start_datetime.setter
    def start_datetime(self, value: datetime) -> None:
        self.contents_database.tables[self.meta_table_name].set_meta_information(start=value, timezone=value.tzinfo)

    @property
    def timezone(self):
        return self.contents_database.tables[self.meta_table_name].meta_information["timezone"]

    @timezone.setter
    def timezone(self, value: tzinfo | str) -> None:
        self.contents_database.tables[self.meta_table_name].set_meta_information(timezone=value)

    @property
    def age(self):
        return self.contents_database.tables[self.meta_table_name].meta_information["age"]

    @age.setter
    def age(self, value: int) -> None:
        self.contents_database.tables[self.meta_table_name].set_meta_information(age=value)

    @property
    def sex(self):
        return self.contents_database.tables[self.meta_table_name].meta_information["sex"]

    @sex.setter
    def sex(self, value: int) -> None:
        self.contents_database.tables[self.meta_table_name].set_meta_information(sex=value)

    @property
    def species(self):
        return self.contents_database.tables[self.meta_table_name].meta_information["species"]

    @species.setter
    def species(self, value: str) -> None:
        self.contents_database.tables[self.meta_table_name].set_meta_information(species=value)

    @property
    def recording_unit(self):
        return self.contents_database.tables[self.meta_table_name].meta_information["recording_unit"]

    @recording_unit.setter
    def recording_unit(self, value: str) -> None:
        self.contents_database.tables[self.meta_table_name].set_meta_information(recording_unit=value)
