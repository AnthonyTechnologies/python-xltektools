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
from .tables import BaseXLTEKAnnotationsInformationTableSchema, BaseXLTEKAnnotationsTableSchema
from .tables import BaseXLTEKXLSpikeTableSchema
from .tables import BaseXLTEKXLEventTableSchema


# Definitions #
# Classes #
class XLTEKAnnotationsAsyncSchema(AsyncAttrs, DeclarativeBase):
    pass


class XLTEKAnnotationsInformationTableSchema(BaseXLTEKAnnotationsInformationTableSchema, XLTEKAnnotationsAsyncSchema):
    pass


class XLTEKAnnotationsTableSchema(BaseXLTEKAnnotationsTableSchema, XLTEKAnnotationsAsyncSchema):
    pass


class XLTEKXLSpikeTableSchema(BaseXLTEKXLSpikeTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKXLEventTableSchema(BaseXLTEKXLEventTableSchema, XLTEKAnnotationsTableSchema):
    pass
