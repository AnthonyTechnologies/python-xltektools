"""xltekcontentsupdatetask.py

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
from asyncio import sleep
from queue import Empty
from typing import Any

# Third-Party Packages #
from cdfs import BaseCDFS
from taskblocks import AsyncEvent
from taskblocks import AsyncQueue
from taskblocks import AsyncQueueInterface
from taskblocks import TaskBlock

# Local Packages #
from ..tables import XLTEKContentsTableManifestation


# Definitions #
# Classes #
class XLTEKContentsUpdateTask(TaskBlock):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    # Attributes #
    cdfs: BaseCDFS | None = None
    table_name: str = "contents"
    contents_table: XLTEKContentsTableManifestation | None = None
    was_open: bool = False
    update_key: str = "start_id"
    contents_update_id: int = 0

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        cdfs: BaseCDFS | None = None,
        component_name: str | None = None,
        name: str = "",
        sets_up: bool = True,
        tears_down: bool = True,
        is_process: bool = False,
        s_kwargs: dict[str, Any] | None = None,
        t_kwargs: dict[str, Any] | None = None,
        d_kwargs: dict[str, Any] | None = None,
        *args: Any,
        init: bool = True,
        **kwargs: Any,
    ) -> None:

        # Parent Attributes #
        super().__init__(*args, init=False, **kwargs)

        # Construct #
        if init:
            self.construct(
                cdfs=cdfs,
                component_name=component_name,
                name=name,
                sets_up=sets_up,
                tears_down=tears_down,
                is_process=is_process,
                s_kwargs=s_kwargs,
                t_kwargs=t_kwargs,
                d_kwargs=d_kwargs,
            )

    @property
    def contents_entry_queue(self) -> AsyncQueueInterface:
        """The queue to get studies from."""
        return self.inputs.queues["contents_entry"]

    @contents_entry_queue.setter
    def contents_entry_queue(self, value: AsyncQueueInterface) -> None:
        self.inputs.queues["contents_entry"] = value

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        cdfs: BaseCDFS | None = None,
        component_name: str | None = None,
        name: str | None = None,
        sets_up: bool | None = None,
        tears_down: bool | None = None,
        is_process: bool | None = None,
        s_kwargs: dict[str, Any] | None = None,
        t_kwargs: dict[str, Any] | None = None,
        d_kwargs: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            cdfs: The CDFS object to use.
            component_name: The name of the CDFS component to use.
            name: Name of this object.
            sets_up: Determines if setup will be run.
            tears_down: Determines if teardown will be run.
            is_process: Determines if this task will run in another process.
            s_kwargs: Contains the keyword arguments to be used in the setup method.
            t_kwargs: Contains the keyword arguments to be used in the task method.
            d_kwargs: Contains the keyword arguments to be used in the teardown method.
            *args: Arguments for inheritance.
            **kwargs: Keyword arguments for inheritance.
        """
        if cdfs is not None:
            self.cdfs = cdfs

        if component_name is not None:
            self.table_name = component_name

        # Construct Parent #
        super().construct(
            name=name,
            sets_up=sets_up,
            tears_down=tears_down,
            is_process=is_process,
            s_kwargs=s_kwargs,
            t_kwargs=t_kwargs,
            d_kwargs=d_kwargs,
            *args,
            **kwargs,
        )

    # IO
    def construct_io(self) -> None:
        """Abstract method that constructs the io for this object."""
        self.inputs.queues["contents_entry"] = AsyncQueue()
        self.inputs.events["entries_done"] = AsyncEvent()
        self.outputs.events["done"] = AsyncEvent()

    async def entry_queue_get(self, interval: float = 0.0) -> list[dict[str, Any]] | None:
        items = []
        while self.loop_event.is_set():
            try:
                items.append(self.contents_entry_queue.get(block=False))
            except Empty:
                if items:
                    return items
                elif self.inputs.events["entries_done"].is_set():
                    self.loop_event.clear()
                    self.outputs.events["done"].set()
                    return None
                else:
                    await sleep(interval)

    # Setup
    async def setup(self, *args: Any, **kwargs: Any) -> None:
        """The method to run before executing task."""
        if not self.cdfs.is_open:
            self.cdfs.open()
        self.contents_table = self.cdfs.contents_database.tables[self.tables_name]
        update_id = await self.contents_table.get_last_update_id_async()
        self.contents_update_id = 0 if update_id is None else update_id

    # TaskBlock
    async def task(self, *args: Any, **kwargs: Any) -> None:
        """The main method to execute."""
        entries = await self.entry_queue_get()
        if entries is None:
            return

        update_id = self.contents_update_id
        for entry in entries:
            entry["update_id"] = update_id
        self.contents_update_id += 1

        await self.contents_table.update_entries_async(
                entries=entries,
                key=self.update_key,
                begin=True,
            )

    # Teardown
    async def teardown(self, *args: Any, **kwargs: Any) -> None:
        """The method to run after executing task."""
        if not self.was_open:
            await self.cdfs.close_async()
