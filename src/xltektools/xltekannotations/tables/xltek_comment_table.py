"""xltek_comment_table.py
A schema for a containing the XLSpike annotations in an XLTEK Study.
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
from typing import Any
from uuid import UUID

# Third-Party Packages #
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemyobjects.tables import BaseUpdateTableSchema, UpdateTableManifestation

# Local Packages #


# Definitions #
# Classes #
class BaseXLTEKCommentTableSchema(BaseUpdateTableSchema):
    """A schema for a containing the XLSpike annotations in an XLTEK Study.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy.

    Columns:
        analysis_context: The analysis context for the spike.
        analysis_id: The ID of the analysis of the spike.
        channel_number: The channel number where the spike occured.
    """

    # Class Attributes #
    __tablename__ = "comment"
    __mapper_args__ = {"polymorphic_identity": "comment"}

    # Columns #
    user: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=True)

    # Instance Methods #

    def as_dict(self) -> dict[str, Any]:
        """Creates a dictionary with all the contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the row.
        """
        entry = super().as_dict()
        entry.update(
            type=self.type,
            user=self.user,
        )
        return entry

    def as_entry(self) -> dict[str, Any]:
        """Creates a dictionary with the entry contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the entry.
        """
        entry = super().as_entry()
        entry.update(
            type=self.type,
            user=self.user,
        )
        return entry


class XLTEKCommentTableManifestation(UpdateTableManifestation):
    """The manifestation of a XLTEKCommentTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table: The SQLAlchemy declarative table which this object act as the interface for.

    Args:
        table: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """
