""" basexltekmetainformationtable.py
A node component which implements time content information in its dataset.
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

# Third-Party Packages #
from cdfs.contentsfile import BaseMetaInformationTable
from sqlalchemy.orm import Mapped, mapped_column

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKMetaInformationTable(BaseMetaInformationTable):
    __mapper_args__ = {"polymorphic_identity": "xltekmetainfromation"}
    subject_id: Mapped[str]
    age: Mapped[int]
    sex: Mapped[str] = mapped_column(default="U")
    species: Mapped[str] = mapped_column(default="Homo Sapien")
    recording_unit: Mapped[str] = mapped_column(default="microvolts")

