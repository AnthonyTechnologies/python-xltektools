""" basexltekcontentstable.py
A node component which implements time content information in its dataset.
"""
# Package Header #
from ....header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import pathlib
from typing import Any

# Third-Party Packages #
from cdfs.contentsfile import BaseTimeContentsTable
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import BigInteger

# Local Packages #
from ....hdf5xltek import HDF5XLTEK


# Definitions #
# Classes #
class BaseXLTEKContentsTable(BaseTimeContentsTable):
    __mapper_args__ = {"polymorphic_identity": "xltekcontents"}
    start_id = mapped_column(BigInteger)
    end_id = mapped_column(BigInteger)

    file_type: type[HDF5XLTEK] | None = HDF5XLTEK

    # Class Methods #
    @classmethod
    def correct_contents(cls, session, path: pathlib.Path) -> None:
        # Correct registered entries
        registered = set()
        for item in cls.get_all(session=session):
            entry = item.as_entry()
            full_path = path / entry["path"]
            with cls.file_type.new_validated(full_path) as file:
                if file is not None:
                    item.update({
                        "path": file.path.name,
                        "start": file.start_datetime,
                        "end": file.end_datetime,
                        "sample_rate": file.sample_rate,
                        "shape": file.data.shape,
                        "start_id": file.start_id,
                        "end_id": file.end_id,
                    })
                    file.close()
            registered.add(full_path)

        # Correct unregistered
        entries = []
        for new_path in set(path.rglob("*.h5")) - registered:
            file = cls.file_type.new_validated(new_path)
            if file is not None:
                entries.append({
                    "path": file.path.name,
                    "start": file.start_datetime,
                    "end": file.end_datetime,
                    "sample_rate": file.sample_rate,
                    "shape": file.data.shape,
                    "start_id": file.start_id,
                    "end_id": file.end_id,
                })
                file.close()
        cls.insert_all(session=session, items=entries, as_entries=True)
    
    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        dict_ = ({} if dict_ is None else dict_) | kwargs
        if start_id := dict_.get("start_id", None) is not None:
            self.start_id = start_id
        if end_id := dict_.get("end_id", None) is not None:
            self.end_id = end_id
        super().update(dict_)
