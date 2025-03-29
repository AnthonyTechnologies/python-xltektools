"""xltekxlspiketable.py
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
from sqlalchemy import Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

# Local Packages #
from .xltekannotationstable import BaseXLTEKAnnotationsTableSchema, XLTEKAnnotationsTableManifestation


# Definitions #
# Classes #
class BaseXLTEKXLSpikeTableSchema(BaseXLTEKAnnotationsTableSchema):
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
    __tablename__ = "xlspike"
    __mapper_args__ = {"polymorphic_identity": "xlspike"}

    # Columns #
    id = mapped_column(ForeignKey("annotations.id"), primary_key=True)
    analysis_context: Mapped[int] = mapped_column(nullable=True)
    analysis_id = mapped_column(Uuid, nullable=True)
    channel_number: Mapped[int] = mapped_column(nullable=True)
    user: Mapped[str] = mapped_column(nullable=True)

    # Class Methods #
    # Base
    @classmethod
    def to_sql_types(cls, dict_: dict[str, Any] | None = None, /, **kwargs) -> dict[str, Any]:
        """Casts Python types of an entry to SQLAlchemy types.

        Only table item elements (columns) which must cast to an SQLAlchemy type are cast to SQLAlchemy types.
        Additionally, all elements are optional, such that they do not need to be provided. This way any subset of the
        elements can cast. For example: when updating a table item, a few elements can updated without providing all
        elements.

        Args:
            dict_: A dictionary representing the entry with Python types.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary representing the entry with SQLAlchemy types.
        """
        # Format parent entry
        sql_entry = super().to_sql_types(dict_, **kwargs)

        # Format ID
        if (id_ := sql_entry.get("analysis_id", None)) is not None:
            match id_:
                case UUID():
                    pass
                case str():
                    sql_entry["analysis_id"] = UUID(hex=id_)
                case int():
                    sql_entry["analysis_id"] = UUID(int=id_)

        # Return formated entry
        return sql_entry


class XLTEKXLSpikeTableManifestation(XLTEKAnnotationsTableManifestation):
    """The manifestation of a XLTEKXLSpikeTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table: The SQLAlchemy declarative table which this object act as the interface for.

    Args:
        table: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """
