""" xltecdfskmetainformationcomponent.py.py

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
from datetime import datetime, tzinfo
from typing import Any

# Third-Party Packages #
from cdfs.components import BaseCDFSContentsComponent

# Local Packages #


# Definitions #
# Classes #
class XLTEKCDFSMetaInformationComponent(BaseCDFSContentsComponent):

    # Attributes #
    table_name = "meta_information"

    # Properties #
    @property
    def meta_information(self) -> dict[str, Any]:
        return self.contents_table.meta_information

    @property
    def name(self) -> str | None:
        """The subject ID from the file attributes."""
        return self.contents_table.meta_information["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.contents_table.set_meta_information(name=value)

    @property
    def start_datetime(self):
        return self.contents_table.meta_information["start"]

    @start_datetime.setter
    def start_datetime(self, value: datetime) -> None:
        self.contents_table.set_meta_information(start=value, timezone=value.tzinfo)

    @property
    def timezone(self):
        return self.contents_table.meta_information["timezone"]

    @timezone.setter
    def timezone(self, value: tzinfo | str) -> None:
        self.contents_table.set_meta_information(timezone=value)

    @property
    def age(self):
        return self.contents_table.meta_information["age"]

    @age.setter
    def age(self, value: int) -> None:
        self.contents_table.set_meta_information(age=value)

    @property
    def sex(self):
        return self.contents_table.meta_information["sex"]

    @sex.setter
    def sex(self, value: int) -> None:
        self.contents_table.set_meta_information(sex=value)

    @property
    def species(self):
        return self.contents_table.meta_information["species"]

    @species.setter
    def species(self, value: str) -> None:
        self.contents_table.set_meta_information(species=value)

    @property
    def recording_unit(self):
        return self.contents_table.meta_information["recording_unit"]

    @recording_unit.setter
    def recording_unit(self, value: str) -> None:
        self.contents_table.set_meta_information(recording_unit=value)