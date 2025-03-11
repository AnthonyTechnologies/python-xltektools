"""xltekannotationsschema.py

"""
from .tables.xltek_clipnote_table import BaseXLTEKClipnoteTableSchema
from .tables.xltek_comment_table import BaseXLTEKCommentTableSchema
from .tables.xltek_uuid_box_and_blocks_table import BaseXLTEKUuidBoxAndBlocksTableSchema
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
from .tables import BaseXLTEKAnnotationsInformationTableSchema, BaseXLTEKAnnotationsTableSchema, \
    BaseXLTEKUuidAnalyzersTableSchema
from .tables import BaseXLTEKXLSpikeTableSchema
from .tables import BaseXLTEKXLEventTableSchema
from .tables import BaseXLTEKCommentTableSchema
from .tables import BaseXLTEKCorticalStimOnTableSchema
from .tables import BaseXLTEKClipnoteTableSchema
from .tables import BaseXLTEKClipnoteCommentTableSchema
from .tables import BaseXLTEKCorticalStimEtcTableSchema
from .tables import BaseXLTEKCorticalStimOffTableSchema
from .tables import BaseXLTEKCommentTableSchema
from .tables import BaseXLTEKUuidAnalyzersTableSchema
from .tables import BaseXLTEKUuidBoxAndBlocksTableSchema
from .tables import BaseXLTEKAnnotationsTableSchema
from .tables import BaseXLTEKUuidSaturationOpsTableSchema
from .tables import BaseXLTEKUuidVideoErrorsTableSchema
from .tables import BaseXLTEKUuidVideoOpsTableSchema
from .tables import BaseXLTEKUuidPatientEventsTableSchema


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


class XLTEKCommentTableSchema(BaseXLTEKCommentTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKCorticalStimOnTableSchema(BaseXLTEKCorticalStimOnTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKCorticalStimOffTableSchema(BaseXLTEKCorticalStimOffTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKCorticalStimEtcTableSchema(BaseXLTEKCorticalStimEtcTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKClipnoteTableSchema(BaseXLTEKClipnoteTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKClipnoteCommentTableSchema(BaseXLTEKClipnoteCommentTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKUuidAnalyzersTableSchema(BaseXLTEKUuidAnalyzersTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKUuidVideoErrorsTableSchema(BaseXLTEKUuidVideoErrorsTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKUuidBoxAndBlocksTableSchema(BaseXLTEKUuidBoxAndBlocksTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKUuidPatientEventsTableSchema(BaseXLTEKUuidPatientEventsTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKUuidVideoOpsTableSchema(BaseXLTEKUuidVideoOpsTableSchema, XLTEKAnnotationsTableSchema):
    pass


class XLTEKUuidSaturationOpsTableSchema(BaseXLTEKUuidSaturationOpsTableSchema, XLTEKAnnotationsTableSchema):
    pass