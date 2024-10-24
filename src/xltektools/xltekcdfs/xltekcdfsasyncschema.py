"""xltekcdfsschema.py

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
from .tables import BaseXLTEKMetaInformationTable, BaseXLTEKContentsTable, BaseXLTEKVideosTable


# Definitions #
# Classes #
class XLTEKCDFSAsyncSchema(AsyncAttrs, DeclarativeBase):
    pass


class XLTEKMetaInformationTable(BaseXLTEKMetaInformationTable, XLTEKCDFSAsyncSchema):
    pass


class XLTEKContentsTable(BaseXLTEKContentsTable, XLTEKCDFSAsyncSchema):
    pass


class XLTEKVideosTable(BaseXLTEKVideosTable, XLTEKCDFSAsyncSchema):
    pass
