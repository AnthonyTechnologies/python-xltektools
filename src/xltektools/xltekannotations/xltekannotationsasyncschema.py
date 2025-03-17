"""xltekannotationsschema.py
The SQLAlchemy schema for an XLTEK annotations SQLite database and its component tables.
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
from .tables import (
    BaseXLTEKAnnotationsInformationTableSchema,
    BaseXLTEKAnnotationsTableSchema,
    BaseXLTEKXLSpikeTableSchema,
    BaseXLTEKXLEventTableSchema,
    BaseXLTEKCommentTableSchema,
    BaseXLTEKCorticalStimOnTableSchema,
    BaseXLTEKCorticalStimOffTableSchema,
    BaseXLTEKCorticalStimEtcTableSchema,
    BaseXLTEKClipnoteTableSchema,
    BaseXLTEKClipnoteCommentTableSchema,
    BaseXLTEKUuidAnalyzersTableSchema,
    BaseXLTEKUuidVideoErrorsTableSchema,
    BaseXLTEKUuidBoxAndBlocksTableSchema,
    BaseXLTEKUuidPatientEventsTableSchema,
    BaseXLTEKUuidVideoOpsTableSchema,
    BaseXLTEKUuidSaturationOpsTableSchema,
)


# Definitions #
# Classes #
class XLTEKAnnotationsAsyncSchema(AsyncAttrs, DeclarativeBase):
    """The root SQLAlchemy schema for an XLTEK annotations SQLite database in an asynchronous context.

    This class is used for defining the schema of an XLTEK annotations database and serves as a base class for managing
    database operations asynchronously. It inherits attributes and methods from the `AsyncAttrs` and `DeclarativeBase`
    classes to facilitate interaction with an SQL database in an asynchronous environment.
    """


class XLTEKAnnotationsInformationTableSchema(BaseXLTEKAnnotationsInformationTableSchema, XLTEKAnnotationsAsyncSchema):
    """The SQLAlchemy schema for the information table of an XLTEK annotations SQLite database."""


class XLTEKAnnotationsTableSchema(BaseXLTEKAnnotationsTableSchema, XLTEKAnnotationsAsyncSchema):
    """The SQLAlchemy schema for the main table of an XLTEK annotations SQLite database."""


class XLTEKXLSpikeTableSchema(BaseXLTEKXLSpikeTableSchema, XLTEKAnnotationsTableSchema):
    """The SQLAlchemy schema for the spike table of an XLTEK annotations SQLite database."""


# class XLTEKXLEventTableSchema(BaseXLTEKXLEventTableSchema, XLTEKAnnotationsTableSchema):
#     pass


class XLTEKCommentTableSchema(BaseXLTEKCommentTableSchema, XLTEKAnnotationsTableSchema):
    """The SQLAlchemy schema for the comment table of an XLTEK annotations SQLite database."""


# class XLTEKCorticalStimOnTableSchema(BaseXLTEKCorticalStimOnTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKCorticalStimOffTableSchema(BaseXLTEKCorticalStimOffTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKCorticalStimEtcTableSchema(BaseXLTEKCorticalStimEtcTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKClipnoteTableSchema(BaseXLTEKClipnoteTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKClipnoteCommentTableSchema(BaseXLTEKClipnoteCommentTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKUuidAnalyzersTableSchema(BaseXLTEKUuidAnalyzersTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKUuidVideoErrorsTableSchema(BaseXLTEKUuidVideoErrorsTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKUuidBoxAndBlocksTableSchema(BaseXLTEKUuidBoxAndBlocksTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKUuidPatientEventsTableSchema(BaseXLTEKUuidPatientEventsTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKUuidVideoOpsTableSchema(BaseXLTEKUuidVideoOpsTableSchema, XLTEKAnnotationsTableSchema):
#     pass
#
#
# class XLTEKUuidSaturationOpsTableSchema(BaseXLTEKUuidSaturationOpsTableSchema, XLTEKAnnotationsTableSchema):
#     pass
