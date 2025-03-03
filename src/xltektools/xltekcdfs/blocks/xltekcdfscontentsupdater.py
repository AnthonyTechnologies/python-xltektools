""" xltekcdfscontentsupdater.py
A block object which writes updates to the XLTEK CDFS contents table.
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
from typing import Any, ClassVar

# Third-Party Packages #
from cdfs import BaseCDFS
from blockobjects import BaseBlock

# Local Packages #
from ..tables import XLTEKContentsTableManifestation


# Definitions #
# Classes #
class XLTEKCDFSContentsUpdater(BaseBlock):
    """A block object which writes updates to the XLTEK CDFS contents table.

    Class Attributes:
        default_input_names: The default ordered tuple with the names of the inputs.
        init_setup: Determines if the setup will occur during initialization.

    Attributes:
        default_input_names: Specifies default input names for the block.
        init_setup: Indicates whether the initial setup is complete.
        cdfs: Represents the CDFS with which this block interacts.
        table_name: The name of the table being updated in the CDFS.
        contents_table: Represents the manifestation of the contents table.
        was_open: Tracks whether the CDFS was open before setup.
        id_key: Identifies the key used for updating entries in the table.
        contents_update_id: Tracks the update ID for the contents table.
    """

    # Class Attributes #
    default_input_names: ClassVar[tuple[str, ...]] = ("entry",)
    init_setup: ClassVar[bool] = False

    # Attributes #
    no_output_sentinel: Any = None

    cdfs: BaseCDFS | None = None
    table_name: str = "contents"
    contents_table: XLTEKContentsTableManifestation | None = None
    was_open: bool = False
    id_key: str = "start_id"
    contents_update_id: int = 0

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        cdfs: BaseCDFS | None = None,
        *args: Any,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #

        # Parent Attributes #
        super().__init__(init=False)

        # Construct #
        if init:
            self.construct(cdfs, *args, **kwargs)

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        cdfs: BaseCDFS | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Assign Attributes #
        if cdfs is not None:
            self.cdfs = cdfs

        # Construct Parent #
        super().construct(*args, **kwargs)

    # Instance Methods #
    # Setup
    async def setup(self, *args: Any, **kwargs: Any) -> None:
        """Asynchronously sets up this block."""
        if not self.cdfs:
            self.cdfs.open()
        self.contents_table = self.cdfs.contents_database.tables[self.table_name]
        update_id = await self.contents_table.get_last_update_id_async()
        self.contents_update_id = 0 if update_id is None else update_id

    # Evaluate
    def evaluate(self, entry: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        """Updates an entry in the contents table, either updating or inserting.

        Args:
            entry: The dictionary containing entry data to be updated.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result from updating the entry in the contents table.
        """
        # Set Update ID
        self.contents_update_id += 1
        entry["update_id"] = self.contents_update_id

        # Update Contents
        self.contents_table.update_entry(
            entries=entry,
            key=self.id_key,
            begin=True,
        )

    async def evaluate_async(self, entry: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        """Asynchronously updates an entry in the contents table, either updating or inserting.

        Args:
            entry: The dictionary containing entry data to be updated.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result from updating the entry in the contents table.
        """
        # Set Update ID
        self.contents_update_id += 1
        entry["update_id"] = self.contents_update_id

        # Update Contents
        await self.contents_table.update_entry_async(
            entry=entry,
            key=self.id_key,
            begin=True,
        )

    # Teardown
    async def teardown(self, *args: Any, **kwargs: Any) -> None:
        """Asynchronously tears down this block."""
        if not self.was_open:
            await self.cdfs.close_async()

        await self.outputs.put_item_async(self.signal_io_name, {"done_flag": True})
