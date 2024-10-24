""" xltekmetainformationcdfscomponent.py.py

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
from datetime import datetime

# Third-Party Packages #
from cdfs.components import MetaInformationCDFSComponent

# Local Packages #
from ..tables import BaseXLTEKMetaInformationTable


# Definitions #
# Classes #
class XLTEKMetaInformationCDFSComponent(MetaInformationCDFSComponent):
    # Attributes #
    _table: type[BaseXLTEKMetaInformationTable] | None = None

    # Properties #
    @property
    def name(self) -> str | None:
        """The subject ID from the file attributes."""
        return self.meta_information["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.set_meta_information(name=value)

    @property
    def start_datetime(self):
        return self.meta_information["start"]

    @start_datetime.setter
    def start_datetime(self, value: datetime) -> None:
        self.set_meta_information(start=value, timezone=value.tzinfo)
