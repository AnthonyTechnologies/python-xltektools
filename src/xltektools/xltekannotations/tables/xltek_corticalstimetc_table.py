"""xltek_corticalstimetc_table.py
A schema for a containing the corticalstimetc annotations in an XLTEK Study.
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
class BaseXLTEKCorticalStimEtcTableSchema(BaseUpdateTableSchema):
    """A schema for a containing the corticalstimetc annotations in an XLTEK Study.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy.

    Columns:
        analysis_context: The analysis context for the spike.
        analysis_id: The ID of the analysis of the spike.
        channel_number: The channel number where the spike occured.
    """

    # Class Attributes #
    __tablename__ = "corticalstimetc"
    __mapper_args__ = {"polymorphic_identity": "corticalstimetc"}

    # Columns #
    user: Mapped[str] = mapped_column(nullable=True)
    modification_user: Mapped[str] = mapped_column(nullable=True)

    # Instance Methods #

    def as_dict(self) -> dict[str, Any]:
        """Creates a dictionary with all the contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the row.
        """
        entry = super().as_dict()
        entry.update(
            cort_stim_event=self.CortStimEvent,
            delivered_current=self.DeliveredCurrent,
            event=self.Event,
            is_complete=self.IsComplete,
            never_displayed=self.NeverDisplayed,
            relays_active=self.RelaysActive,
            secondary=self.Secondary,
            stamp=self.Stamp,
            token=self.Token,
            type=self.Type,
            len=self.__len__,

            intensity=self.Intensity,
            negative_electrode=self.NegativeElectrode,
            negative_electrode_label=self.NegativeElectrodeLabel,
            positive_electrode=self.PositiveElectrode,
            positive_electrode_label=self.PositiveElectrodeLabel,
            pulse_duration=self.PulseDuration,
            pulse_frequency=self.PulseFrequency,
            train_duration=self.TrainDuration,
        )
        return entry

    def as_entry(self) -> dict[str, Any]:
        """Creates a dictionary with the entry contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the entry.
        """
        entry = super().as_entry()
        entry.update(
            cort_stim_event=self.CortStimEvent,
            delivered_current=self.DeliveredCurrent,
            event=self.Event,
            is_complete=self.IsComplete,
            never_displayed=self.NeverDisplayed,
            relays_active=self.RelaysActive,
            secondary=self.Secondary,
            stamp=self.Stamp,
            token=self.Token,
            type=self.Type,
            len=self.__len__,

            intensity=self.Intensity,
            negative_electrode=self.NegativeElectrode,
            negative_electrode_label=self.NegativeElectrodeLabel,
            positive_electrode=self.PositiveElectrode,
            positive_electrode_label=self.PositiveElectrodeLabel,
            pulse_duration=self.PulseDuration,
            pulse_frequency=self.PulseFrequency,
            train_duration=self.TrainDuration,

        )
        return entry


class XLTEKCorticalStimEtcTableManifestation(UpdateTableManifestation):
    """The manifestation of a XLTEKCorticalStimEtcTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table: The SQLAlchemy declarative table which this object act as the interface for.

    Args:
        table: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """
