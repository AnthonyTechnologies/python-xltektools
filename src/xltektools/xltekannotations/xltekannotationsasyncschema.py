"""xltekannotationsschema.py

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

# Third-Party Packages #
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

# Local Packages #
from .tables import BaseXLTEKAnnotationsInformationTable, BaseXLTEKAnnotationsTable


# Definitions #
# Classes #
class XLTEKAnnotationsAsyncSchema(AsyncAttrs, DeclarativeBase):
    pass


class XLTEKAnnotationsInformationTable(BaseXLTEKAnnotationsInformationTable, XLTEKAnnotationsAsyncSchema):
    pass


class XLTEKAnnotationsTable(BaseXLTEKAnnotationsTable, XLTEKAnnotationsAsyncSchema):
    pass
