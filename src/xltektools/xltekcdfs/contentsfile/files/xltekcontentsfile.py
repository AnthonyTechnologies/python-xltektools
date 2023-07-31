"""xltekcontentsfile.py

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
import pathlib

# Third-Party Packages #
from baseobjects import BaseObject
from cdfs.contentsfile import TimeContentsFile
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncEngine

# Local Packages #
from ..bases import BaseXLTEKMetaInformationTable, BaseXLTEKContentsTable, BaseXLTEKVideosTable


# Definitions #
# Classes #
class XLTEKContentsFileAsyncSchema(AsyncAttrs, DeclarativeBase):
    pass


class XLTEKMetaInformationTable(BaseXLTEKMetaInformationTable, XLTEKContentsFileAsyncSchema):
    pass


class XLTEKContentsTable(BaseXLTEKContentsTable, XLTEKContentsFileAsyncSchema):
    pass


class XLTEKVideosTable(BaseXLTEKVideosTable, XLTEKContentsFileAsyncSchema):
    pass


class XLTEKContentsFile(TimeContentsFile):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    schema: type[DeclarativeBase] = XLTEKContentsFileAsyncSchema
    meta_information_table = type[XLTEKMetaInformationTable] = XLTEKMetaInformationTable
    contents: type[XLTEKContentsTable] = XLTEKContentsTable
    videos: type[XLTEKVideosTable] = XLTEKVideosTable

    # Magic Methods #
    # Construction/Destruction