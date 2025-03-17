""" annotationsdatabaseupdater.py
A block object which writes updates to the XLTEK annotations_database contents table.
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
from datetime import tzinfo
from typing import Any, ClassVar

# Third-Party Packages #
from blockobjects import BaseBlock

# Local Packages #
from ..xltekannotationsdatabase import XLTEKAnnotationsDatabase


# Definitions #
# Classes #
class AnnotationsDatabaseUpdater(BaseBlock):
    """A block object which writes updates to the XLTEK annotations_database contents table.

    Class Attributes:
        default_input_names: The default ordered tuple with the names of the inputs.
        init_setup: Determines if the setup will occur during initialization.

    Attributes:
        default_input_names: Specifies default input names for the block.
        init_setup: Indicates whether the initial setup is complete.
        annotations_database: Represents the annotations_database with which this block interacts.
        was_open: Tracks whether the annotations_database was open before setup.
        id_key: Identifies the unique key used to determine if an entry should be updated or inserted in the table.
    """

    # Class Attributes #
    default_input_names: ClassVar[tuple[str, ...]] = ("write_packet",)
    init_setup: ClassVar[bool] = False

    # Class Methods #
    @classmethod
    def create_write_packet_info(
        cls,
        type_: str = "",
        nanostamp: int | None = None,
        tz: tzinfo | None = None,
        entry: dict[str, Any] | None = None,
    ) -> dict:
        return {
            "type": type_,
            "entry": {"tz_offset": tz, "nanostamp": nanostamp} | entry,
        }

    # Attributes #
    no_output_sentinel: Any = None
    was_open: bool = False
    id_key: str = "id"

    annotations_database: XLTEKAnnotationsDatabase | None = None

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        annotations_database: XLTEKAnnotationsDatabase | None = None,
        *args: Any,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #

        # Parent Attributes #
        super().__init__(init=False)

        # Construct #
        if init:
            self.construct(annotations_database, *args, **kwargs)

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        annotations_database: XLTEKAnnotationsDatabase | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Assign Attributes #
        if annotations_database is not None:
            self.annotations_database = annotations_database

        # Construct Parent #
        super().construct(*args, **kwargs)

    # Instance Methods #
    # Setup
    async def setup(self, *args: Any, **kwargs: Any) -> None:
        """Asynchronously sets up this block."""
        if not self.annotations_database:
            self.annotations_database.open()

    # Evaluate
    def evaluate(self, write_packet: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        """Updates an entry in the annotations' database.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result from updating the entry in the contents table.
        """
        # Get table to add entry to
        entry = write_packet["entry"]

        # Update Contents
        self.annotations_database.insert_annotation(
            entry=entry,
            key=self.id_key,
            begin=True,
        )

    async def evaluate_async(self, write_packet: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        """Asynchronously updates an entry in the annotations' database.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result from updating the entry in the contents table.
        """
        # Get table to add entry to
        entry = write_packet["entry"]

        # Update Contents
        await self.annotations_database.insert_annotation_async(
            entry=entry,
            key=self.id_key,
            begin=True,
        )

    # Teardown
    async def teardown(self, *args: Any, **kwargs: Any) -> None:
        """Asynchronously tears down this block."""
        if not self.was_open:
            await self.annotations_database.close_async()

        await self.outputs.put_item_async(self.signal_io_name, {"done_flag": True})
