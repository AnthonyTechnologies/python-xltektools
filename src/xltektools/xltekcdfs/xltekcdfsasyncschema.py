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
from .tables import BaseXLTEKMetaInformationTableSchema, BaseXLTEKContentsTableSchema


# Definitions #
# Classes #
class XLTEKCDFSAsyncSchema(AsyncAttrs, DeclarativeBase):
    pass


class XLTEKMetaInformationTableSchema(BaseXLTEKMetaInformationTableSchema, XLTEKCDFSAsyncSchema):
    pass


class XLTEKContentsTableSchema(BaseXLTEKContentsTableSchema, XLTEKCDFSAsyncSchema):
    pass
