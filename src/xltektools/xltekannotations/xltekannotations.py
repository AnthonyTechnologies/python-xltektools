""" xltekannotations.py.py

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
from typing import Any

# Third-Party Packages #
from sqlalchemy.orm import DeclarativeBase
from sqlalchemyobjects import Database
from sqlalchemyobjects.tables import TableManifestation

# Local Packages #
from .tables import XLTEKAnnotationsInformationTableManifestation
from .tables import XLTEKAnnotationsTableManifestation
from .xltekannotationsasyncschema import XLTEKAnnotationsAsyncSchema
from .xltekannotationsasyncschema import XLTEKAnnotationsInformationTable
from .xltekannotationsasyncschema import XLTEKAnnotationsTable


# Definitions #
# Classes #
class XLTEKAnnotations(Database):

    # Attributes #
    meta_table_name: str = "meta_information"

    schema: type[DeclarativeBase] | None = XLTEKAnnotationsAsyncSchema
    table_maps: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] = {
        meta_table_name: (XLTEKAnnotationsInformationTableManifestation, XLTEKAnnotationsInformationTable, {}),
        "annotations": (XLTEKAnnotationsTableManifestation, XLTEKAnnotationsTable, {}),
    }
