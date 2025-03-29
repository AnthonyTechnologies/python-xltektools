#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_xltekannotations.py

"""

# Imports #
# Standard Libraries #
from pathlib import Path
from uuid import uuid4

# Third-Party Packages #
import pytest

# Local Packages #
from src.xltektools.xltekannotations.xltekannotationsdatabase import XLTEKAnnotationsDatabase


# Definitions #
# Classes #
class TestXLTEKAnnotations:
    """Test suite for the XLTEKAnnotationsDatabase class.

    Provides unit tests for the functionality of the XLTEKAnnotationsDatabase class,
    including operations like initialization, insertion of annotations, and async
    functionalities. Utilizes fixtures, mock objects, and pytest to ensure proper
    behavior of the class under various scenarios.

    Test cases include:
        - Initialization and attributes verification.
        - Manifesting table structure.
        - Insertion of single and multiple annotations.
        - Testing of synchronous and asynchronous insertion capabilities.
    """

    @pytest.fixture
    def temp_dir(self, tmpdir) -> Path:
        return Path(tmpdir)

    @pytest.fixture
    def annotation_database(self, temp_dir) -> XLTEKAnnotationsDatabase:
        """Creates and provides an XLTEKAnnotationsDatabase with a specific path.

        This pytest fixture is used to initialize and pass a pre-configured instance of XLTEKAnnotations for testing 
        purposes. The instance is created with a given file path.

        Returns:
            XLTEKAnnotationsDatabase: An instance of XLTEKAnnotations configured with the
            specified path.
        """
        return XLTEKAnnotationsDatabase(path=temp_dir / "XLTEKannotations_test.sqlite3", create=True)

    def test_init(self, temp_dir: Path) -> None:
        empty_database = XLTEKAnnotationsDatabase(path=temp_dir / "XLTEKannotations_empty_test.sqlite3")
        assert isinstance(empty_database, XLTEKAnnotationsDatabase)
        assert empty_database.schema is not None
        assert empty_database.tables

    def test_create_database(self, temp_dir: Path) -> None:
        empty_database = XLTEKAnnotationsDatabase(path=temp_dir / "XLTEKannotations_empty_test.sqlite3")
        empty_database.create_database()
        assert empty_database.is_open
        assert empty_database.path.exists()
        empty_database.close()
        assert not empty_database.is_open

    def test_insert_annotation(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_insert_test.sqlite3",
            create=True,
            open_=True,
        )
        sample_entry = {
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "random",
        }

        # Test
        annotation_database.insert_annotation(entry=sample_entry, begin=True)

        # Validation
        assert annotation_database.tables["annotations"].get_all(as_python=True)
        annotation_database.close()

    @pytest.mark.asyncio
    async def test_insert_annotation_async(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_insert_test.sqlite3",
            create=True,
            open_=True,
        )
        sample_entry = {
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "random",
        }

        # Test
        await annotation_database.insert_annotation_async(entry=sample_entry, begin=True)

        # Validation
        assert await annotation_database.tables["annotations"].get_all_async(as_python=True)
        await annotation_database.close_async()

    def test_insert_xlspike(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_insert_test.sqlite3",
            create=True,
            open_=True,
        )
        xlspike_entry = {
            "id": uuid4(),
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "XLSpike",
            "analysis_context": 3,
            "analysis_id": uuid4(),
            "channel_number": 0,
            "user": "system",
        }

        # Test
        annotation_database.insert_annotation(entry=xlspike_entry, begin=True)

        # Validation
        assert annotation_database.tables["xlspike"].get_all(as_python=True)
        annotation_database.close()

    @pytest.mark.asyncio
    async def test_insert_xlspike_async(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_insert_test.sqlite3",
            create=True,
            open_=True,
        )
        xlspike_entry = {
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "XLSpike",
            "analysis_context": 3,
            "analysis_id": uuid4(),
            "channel_number": 0,
            "user": "system",
        }

        # Test
        await annotation_database.insert_annotation_async(entry=xlspike_entry, begin=True)

        # Validation
        assert await annotation_database.tables["xlspike"].get_all_async(as_python=True)
        annotation_database.close()
        
    def test_insert_comment(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_insert_test.sqlite3",
            create=True,
            open_=True,
        )
        comment_entry = {
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The user can write a comment here.",
            "type": "Custom [Comment]",
            "user": "system",
        }

        # Test
        annotation_database.insert_annotation(entry=comment_entry, begin=True)

        # Validation
        assert annotation_database.tables["comments"].get_all(as_python=True)
        annotation_database.close()

    @pytest.mark.asyncio
    async def test_insert_comment_async(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_insert_test.sqlite3",
            create=True,
            open_=True,
        )
        comment_entry = {
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The user can write a comment here.",
            "type": "Custom [Comment]",
            "user": "system",
        }

        # Test
        await annotation_database.insert_annotation_async(entry=comment_entry, begin=True)

        # Validation
        assert await annotation_database.tables["comments"].get_all_async(as_python=True)
        annotation_database.close()

    @pytest.mark.asyncio
    async def test_insert_annotations_async(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_insert_test.sqlite3",
            create=True,
            open_=True,
        )
        n_entries = 3
        random_entry = {
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "random",
        }
        xlspike_entry = {
            "id": uuid4(),
            "tz_offset": 0,
            "nanostamp": 2,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "XLSpike",
            "analysis_context": 3,
            "analysis_id": uuid4(),
            "channel_number": 0,
            "user": "system",
        }
        comment_entry = {
            "tz_offset": 0,
            "nanostamp": 3,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The user can write a comment here.",
            "type": "Custom [Comment]",
            "user": "system",
        }
        sample_entries = [random_entry, xlspike_entry, comment_entry]

        # Test
        await annotation_database.insert_annotations_async(entries=sample_entries, begin=True)

        # Validation
        assert len(await annotation_database.tables["annotations"].get_all_async(as_python=True)) == n_entries
        await annotation_database.close_async()

    @pytest.mark.asyncio
    async def test_upsert_annotations_async(self, temp_dir: Path) -> None:
        # Setup
        annotation_database = XLTEKAnnotationsDatabase(
            path=temp_dir / "XLTEKannotations_update_test.sqlite3",
            create=True,
            open_=True,
        )
        n_entries = 3
        random_entry = {
            "id": uuid4(),
            "tz_offset": 0,
            "nanostamp": 1,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "random",
        }
        xlspike_entry = {
            "id": uuid4(),
            "tz_offset": 0,
            "nanostamp": 2,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The system or the user can write a comment here.",
            "type": "XLSpike",
            "analysis_context": 3,
            "analysis_id": uuid4(),
            "channel_number": 0,
            "user": "system",
        }
        comment_entry = {
            "tz_offset": 0,
            "nanostamp": 3,
            "origin": "test_computer",
            "system_text": "System Generated",
            "text": "The user can write a comment here.",
            "type": "Custom [Comment]",
            "user": "system",
        }
        sample_entries = [random_entry, xlspike_entry, comment_entry]

        # Test
        await annotation_database.insert_annotations_async(entries=sample_entries, begin=True)
        assert len(await annotation_database.tables["annotations"].get_all_async(as_python=True)) == n_entries

        n_entries2 = 5
        xlspike_entry["text"] = "This should be updated."
        sample_entries2 = sample_entries + [xlspike_entry | {"id": uuid4()},]

        await annotation_database.upsert_annotations_async(entries=sample_entries2, begin=True)
        assert len(list((await annotation_database.tables["annotations"].get_all_async()).scalars())) == n_entries2

        annotation_schema = annotation_database.tables["annotations"].table_schema
        statement = annotation_schema.create_find_column_value_statement("id", xlspike_entry["id"])

        async with annotation_database.create_async_session() as session:
            result = await session.execute(statement)
            updated_text = await result.scalar_one().awaitable_attrs.text

        assert updated_text == "This should be updated."
        await annotation_database.close_async()


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])
