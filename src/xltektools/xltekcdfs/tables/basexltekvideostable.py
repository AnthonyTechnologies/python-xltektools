""" basexltekvideostable.py
A node component which implements time content information in its dataset.
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

# Third-Party Packages #
from cdfs.tables import BaseTimeContentsTable
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import BigInteger

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKVideosTable(BaseTimeContentsTable):
    __tablename__ = "xltekvideos"
    __mapper_args__ = {"polymorphic_identity": "xltekvideos"}
    start_id = mapped_column(BigInteger)
    end_id = mapped_column(BigInteger)
