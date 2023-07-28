""" basexltekvideostable.py
A node component which implements time content information in its dataset.
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
from datetime import datetime
from decimal import Decimal
from typing import Any
import uuid

# Third-Party Packages #
from cdfs.contentsfile import BaseTimeContentsTable
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import BigInteger

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKVideoTable(BaseTimeContentsTable):
    __mapper_args__ = {"polymorphic_identity": "xltekvideos"}
    start_id = mapped_column(BigInteger)
    end_id = mapped_column(BigInteger)
