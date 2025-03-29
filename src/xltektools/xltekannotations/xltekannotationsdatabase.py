""" xltekannotationsdatabase.py.py

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
from asyncio import gather
from collections.abc import Iterable
from collections import deque
from itertools import chain
from pathlib import Path
from typing import Any

# Third-Party Packages #
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemyobjects import Database
from sqlalchemyobjects.tables import TableManifestation
from .tables.uuid_gen import generate_uuid_for_token

# Local Packages #
from .tables import (
    XLTEKAnnotationsInformationTableManifestation,
    XLTEKAnnotationsTableManifestation,
    XLTEKXLSpikeTableManifestation,
    XLTEKXLEventTableManifestation,
    XLTEKCommentTableManifestation,
    XLTEKCorticalStimOnTableManifestation,
    XLTEKCorticalStimOffTableManifestation,
    XLTEKCorticalStimEtcTableManifestation,
    XLTEKClipnoteTableManifestation,
    XLTEKClipnoteCommentTableManifestation,
    XLTEKUuidAnalyzersTableManifestation,
    XLTEKUuidVideoErrorsTableManifestation,
    XLTEKUuidBoxAndBlocksTableManifestation,
    XLTEKUuidPatientEventsTableManifestation,
    XLTEKUuidVideoOpsTableManifestation,
    XLTEKUuidSaturationOpsTableManifestation,
)
from .xltekannotationsasyncschema import (
    XLTEKAnnotationsAsyncSchema,
    XLTEKAnnotationsInformationTableSchema,
    XLTEKAnnotationsTableSchema,
    XLTEKXLSpikeTableSchema,
    XLTEKCommentTableSchema
)


# Definitions #
# Classes #
class XLTEKAnnotationsDatabase(Database):

    # Attributes #
    meta_table_name: str = "meta_information"

    schema: type[DeclarativeBase] | None = XLTEKAnnotationsAsyncSchema
    table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] = {
        meta_table_name: (XLTEKAnnotationsInformationTableManifestation, XLTEKAnnotationsInformationTableSchema, {}),
        "annotations": (XLTEKAnnotationsTableManifestation, XLTEKAnnotationsTableSchema, {}),
        "xlspike":  (XLTEKXLSpikeTableManifestation, XLTEKXLSpikeTableSchema, {}),
        # "xlevent": (XLTEKXLEventTableManifestation, XLTEKXLEventTableSchema, {}),
        "comments": (XLTEKCommentTableManifestation, XLTEKCommentTableSchema, {}),
        # "corticalstimon": (XLTEKCorticalStimOnTableManifestation, XLTEKCorticalStimOnTableSchema, {}),
        # "corticalstimoff": (XLTEKCorticalStimOffTableManifestation, XLTEKCorticalStimOffTableSchema, {}),
        # "corticalstimetc": (XLTEKCorticalStimEtcTableManifestation, XLTEKCorticalStimEtcTableSchema, {}),
        # "clipnote_comment": (XLTEKClipnoteCommentTableManifestation, XLTEKClipnoteCommentTableSchema, {}),
        # "clipnote": (XLTEKClipnoteTableManifestation, XLTEKClipnoteTableSchema, {}),
        # "uuid_analyzers": (XLTEKUuidAnalyzersTableManifestation, XLTEKUuidAnalyzersTableSchema, {}),
        # "uuid_video_errors": (XLTEKUuidVideoErrorsTableManifestation, XLTEKUuidVideoErrorsTableSchema, {}),
        # "uuid_box_and_blocks": (XLTEKUuidBoxAndBlocksTableManifestation, XLTEKUuidBoxAndBlocksTableSchema, {}),
        # "uuid_patient_events": (XLTEKUuidPatientEventsTableManifestation, XLTEKUuidPatientEventsTableSchema, {}),
        # "uuid_video_ops": (XLTEKUuidVideoOpsTableManifestation, XLTEKUuidVideoOpsTableSchema, {}),
        # "uuid_saturation_ops": (XLTEKUuidSaturationOpsTableManifestation, XLTEKUuidSaturationOpsTableSchema, {}),
    }

    annotation_type_map: dict[str, str] = {
        "base": "annotations",
        "annotation": "annotations",
        "xlspike": "xlspike",
        "XLSpike": "xlspike",
        # "xlevent": "xlevent",
        "Custom [Comment]": "comments",
        "comments": "comments",
        # "corticalstimon": "corticalstimon",
        # "corticalstimoff": "corticalstimoff",
        # "corticalstimetc": "corticalstimetc",
        # 'clipnote_comment': 'clipnote_comment',
        # "clipnote": "clipnote",
        # "uuid_analyzers": "uuid_analyzers",
        # "uuid_video_errors": "uuid_video_errors",
        # "uuid_box_and_blocks": "uuid_box_and_blocks",
        # "uuid_patient_events": "uuid_patient_events",
        # "uuid_video_ops": "uuid_video_ops",
        # "uuid_saturation_ops": "uuid_saturation_ops",
    }

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: str | Path | None = None,
        schema: type[DeclarativeBase] | None = None,
        table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] | None = None,
        open_: bool = False,
        create: bool = False,
        *,
        init: bool = True,
        **kwargs,
    ) -> None:
        # New Attributes #
        self.annotations_types = {}

        # Parent Attributes #
        super().__init__()

        # Object Construction #
        if init:
            self.construct(
                path,
                schema,
                table_map,
                open_,
                create,
                **kwargs,
            )

    # Instance Methods #
    # Annotations
    def insert_annotation(
        self,
        entry: dict[str, Any] | None = None,
        session: Session | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Inserts an item into the table.

        Args:
            entry: A dictionary representing the entry to insert. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        table_name = self.annotation_type_map.get(entry["type"], "annotations")
        if "table_type" not in entry and table_name != "annotations":
            entry["table_type"] = table_name
        self.tables[table_name].insert(entry=entry, session=session, begin=begin, **kwargs)

    async def insert_annotation_async(
        self,
        entry: dict[str, Any] | None = None,
        session: AsyncSession | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously inserts an item into the table.

        Args:
            entry: A dictionary representing the entry to insert. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        table_name = self.annotation_type_map.get(entry["type"], "annotations")
        if "table_type" not in entry and table_name != "annotations":
            entry["table_type"] = table_name
        await self.tables[table_name].insert_async(entry=entry, session=session, begin=begin, **kwargs)

    def insert_annotations(
        self,
        entries: Iterable[dict[str, Any]] = (),
        session: Session | None = None,
        begin: bool = False,
    ) -> None:
        """Inserts multiple annotations into the table.

        Args:
            entries: The entries to insert. Defaults to an empty iterable.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is None:
            session = self.create_session()
            was_open = False
        else:
            was_open = True

        if begin:
            with session.begin():
                stim_began = False

                #Potential check point for whether we need to call the uuid_gen for the paired cortical_stim tokens
                for entry in entries:

                    #update_entrys begin here
                    if entry['event'] == 'StartStimulation' :

                        stim_began = True

                        entry_token = entry['token']
                        token_uuid = generate_uuid_for_token(entry_token)
                        entry['token_uuid'] = token_uuid

                    elif entry['event'] == 'OnStimulationEnded' :

                        if stim_began :
                            #No need to generate a new UUID, since this entry needs to be paired with its respective stimulation one
                            entry['token_uuid'] = token_uuid
                            stim_began = False

                    else :

                        if stim_began:
                            entry['token_uuid'] = token_uuid
                        else :
                            entry_token = entry['token']
                            entry['token_uuid'] = generate_uuid_for_token(entry_token)

                    self.annotations_types[entry["type"]].insert(entry=entry, session=session, begin=False)
        else:
            for entry in entries:
                self.annotations_types[entry["type"]].insert(entry=entry, session=session, begin=False)

        if not was_open:
            session.close()

    async def insert_annotations_async(
        self,
        entries: Iterable[dict[str, Any]] = (),
        session: AsyncSession | None = None,
        begin: bool = False,
    ) -> None:
        """Asynchronously inserts multiple annotations into the table.

        Args:
            entries: The entries to insert. Defaults to an empty iterable.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        items = []
        for entry in entries:
            table_name = self.annotation_type_map.get(entry["type"], "annotations")
            if "table_type" not in entry and table_name != "annotations":
                entry["table_type"] = table_name
            items.append(self.tables[table_name].item_from_dict(entry))

        if session is None:
            session = self.create_async_session()
            was_open = False
        else:
            was_open = True

        if begin:
            async with session.begin():
                await self.insert_all_async(items, session=session, begin=False)
        else:
            await self.insert_all_async(items, session=session, begin=False)

        if not was_open:
            await session.close()
    
    def upsert_annotation(
        self,
        entry: dict[str, Any] | None = None,
        session: Session | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Updates an entry in the table if it exists, otherwise, creates a new entry.

        Args:
            entry: A dictionary representing the entry to update_entry. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        table_name = self.annotation_type_map.get(entry["type"], "annotations")
        if "table_type" not in entry and table_name != "annotations":
            entry["table_type"] = table_name
        self.tables[table_name].upsert_entry(entry=entry, session=session, begin=begin, **kwargs)

    async def upsert_annotation_async(
        self,
        entry: dict[str, Any] | None = None,
        session: AsyncSession | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously, updates an entry in the table if it exists, otherwise, creates a new entry.

        Args:
            entry: A dictionary representing the entry to update_entry. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        table_name = self.annotation_type_map.get(entry["type"], "annotations")
        if "table_type" not in entry and table_name != "annotations":
            entry["table_type"] = table_name
        await self.tables[table_name].upsert_entry_async(entry=entry, session=session, begin=begin, **kwargs)

    def upsert_annotations(
        self,
        entries: Iterable[dict[str, Any]],
        session: Session | None = None,
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Updates multiple entries in the table if they exist, otherwise, creates new entries.

        Args:
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            session: The SQLAlchemy async session to use for the operation.
            key: The key (column name) to search by. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        # Get root annotations schema
        annotations_table_schema = self.tables["annotations"].table_schema

        # Prepare entries
        entry_dict = {}
        entry_dequed = deque()
        for entry in entries:
            # Get annotations type
            table_name = self.annotation_type_map.get(entry["type"], "annotations")
            if "table_type" not in entry and table_name != "annotations":
                entry["table_type"] = table_name

            # Separate entries with and without "key"
            if (value := entry.get(key, None)) is not None:
                entry_dict[value] = entry
            else:
                entry_dequed.append(self.tables[table_name].item_from_dict(entry))

        # Create find statement to find all items to update
        find_statement = annotations_table_schema.create_find_column_values_statement(key, entry_dict.keys())

        # Create Session
        if session is None:
            session = self.create_async_session()
            was_open = False
        else:
            was_open = True

        if begin:
            with session.begin():
                # Find all items to update
                items = session.execute(find_statement)

                # Update found items and remove them from dict
                for item in items.scalars():
                    item.update(entry_dict.pop(getattr(item, key)))

                # Item creation iterable
                item_iter = (self.tables[e["table_type"]].item_from_dict(e) for e in entry_dict.values())

                # Insert all other entries in the deque
                self.insert_all_async(chain(item_iter, entry_dequed), session=session, begin=False)
        else:
            # Find all items to update
            items = session.execute(find_statement)

            # Update found items and remove them from dict
            for item in items.scalars():
                item.update(entry_dict.pop(getattr(item, key)))

            # Item creation iterable
            item_iter = (self.tables[e["table_type"]].item_from_dict(e) for e in entry_dict.values())

            # Insert all other entries in the deque
            self.insert_all_async(chain(item_iter, entry_dequed), session=session, begin=False)

        if not was_open:
            session.close()

    async def upsert_annotations_async(
        self,
        entries: Iterable[dict[str, Any]],
        session: AsyncSession | None = None,
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Asynchronously, updates multiple entries in the table if they exist, otherwise, creates new entries.

        Args:
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            session: The SQLAlchemy async session to use for the operation.
            key: The key (column name) to search by. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        # Get root annotations schema
        annotations_table_schema = self.tables["annotations"].table_schema

        # Prepare entries
        entry_dict = {}
        entry_dequed = deque()
        for entry in entries:
            # Get annotations type
            table_name = self.annotation_type_map.get(entry["type"], "annotations")
            if "table_type" not in entry and table_name != "annotations":
                entry["table_type"] = table_name

            # Separate entries with and without "key"
            if (value := entry.get(key, None)) is not None:
                entry_dict[value] = entry
            else:
                entry_dequed.append(self.tables[table_name].item_from_dict(entry))

        # Create find statement to find all items to update
        find_statement = annotations_table_schema.create_find_column_values_statement(key, entry_dict.keys())

        # Create Session
        if session is None:
            session = self.create_async_session()
            was_open = False
        else:
            was_open = True

        if begin:
            async with session.begin():
                # Find all items to update
                items = await session.execute(find_statement)

                # Update found items and remove them from dict
                items = list(items.scalars())
                for item, value in zip(items, await gather(*(getattr(i.awaitable_attrs, key) for i in items))):
                    item.update(entry_dict.pop(value))

                # Item creation iterable
                item_iter = (self.tables[e["table_type"]].item_from_dict(e) for e in entry_dict.values())

                # Insert all other entries in the deque
                await self.insert_all_async(chain(item_iter, entry_dequed), session=session, begin=False)
        else:
            # Find all items to update
            items = await session.execute(find_statement)

            # Update found items and remove them from dict
            items = list(items.scalars())
            for item, value in zip(items, await gather(*(getattr(i.awaitable_attrs, key) for i in items))):
                item.update(entry_dict.pop(value))

            # Item creation iterable
            item_iter = (self.tables[e["table_type"]].item_from_dict(e) for e in entry_dict.values())

            # Insert all other entries in the deque
            await self.insert_all_async(chain(item_iter, entry_dequed), session=session, begin=False)

        if not was_open:
            await session.close()
    