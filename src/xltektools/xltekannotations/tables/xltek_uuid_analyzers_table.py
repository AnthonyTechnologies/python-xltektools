"""xltek_uuid_analyzers_table.py
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
class BaseXLTEKUuidAnalyzersTableSchema(BaseUpdateTableSchema):
    """A schema for a containing the UuidAnalyzers annotations in an XLTEK Study.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy.

    Columns:
        analysis_context: The analysis context for the spike.
        analysis_id: The ID of the analysis of the spike.
        channel_number: The channel number where the spike occured.
    """

    # Class Attributes #
    __tablename__ = "uuid_analyzers"
    __mapper_args__ = {"polymorphic_identity": "uuid_analyzers"}

    # Columns #
    analysis_context: Mapped[int] = mapped_column(nullable=True)
    channel_number: Mapped[int] = mapped_column(nullable=True)

    type: Mapped[str] = mapped_column(nullable=True)
    user: Mapped[str] = mapped_column(nullable=True)
    len: Mapped[int] = mapped_column(nullable=True)
    analyzer_name: Mapped[str] = mapped_column(nullable=True)
    is_removeable: Mapped[bool] = mapped_column(nullable=True)
    use_creator: Mapped[int] = mapped_column(nullable=True)

    # Class Methods #
    @classmethod
    def format_entry_kwargs(
        cls,
        id_: str | UUID | None = None,
        analysis_id: str | UUID | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Formats entry keyword arguments for creating or updating table entries.

        Args:
            id_: The ID of the entry, if specified.
            analysis_id: The analysis ID of the entry, if specified. Defaults to None.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary of keyword arguments for the entry.
        """
        kwargs = super().format_entry_kwargs(id_=id_, **kwargs)

        if analysis_id is not None:
            kwargs["analysis_id"] = UUID(hex=analysis_id) if isinstance(analysis_id, str) else analysis_id

        return kwargs

    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        """Updates the row of the table with the provided dictionary or keyword arguments.

        Args:
            dict_: A dictionary of attributes/columns to update. Defaults to None.
            **kwargs: Additional keyword arguments for the attributes to update.
        """
        dict_ = ({} if dict_ is None else dict_) | kwargs

        if (analysis_id := dict_.get("analysis_id", None)) is not None:
            self.analysis_id = UUID(hex=analysis_id) if isinstance(analysis_id, str) else analysis_id

        super().update(dict_)

    def as_dict(self) -> dict[str, Any]:
        """Creates a dictionary with all the contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the row.
        """
        entry = super().as_dict()
        entry.update(
            type=self.Type,
            user=self.User,
            len=self.__len__,
            analysis_context=self.AnalysisContext,
            analyzer_name=self.AnalyzerName,
            channel_number=self.ChannelNumber,
            is_removeable=self.IsRemoveable,
            use_creator=self.UseCreator,
        )
        return entry

    def as_entry(self) -> dict[str, Any]:
        """Creates a dictionary with the entry contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the entry.
        """
        entry = super().as_entry()
        entry.update(
            type=self.Type,
            user=self.User,
            len=self.__len__,
            analysis_context=self.AnalysisContext,
            analyzer_name=self.AnalyzerName,
            channel_number=self.ChannelNumber,
            is_removeable=self.IsRemoveable,
            use_creator=self.UseCreator,
        )
        return entry


class XLTEKUuidAnalyzersTableManifestation(UpdateTableManifestation):
    """The manifestation of a XLTEKUuidAnalyzersTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table: The SQLAlchemy declarative table which this object act as the interface for.

    Args:
        table: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """
