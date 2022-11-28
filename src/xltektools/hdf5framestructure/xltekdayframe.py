""" xltekdayframe.py
A frame for directory which contains a day's worth of XLTEK EEG data.
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
from collections.abc import Iterable
import datetime
import pathlib
from typing import Any

# Third-Party Packages #
from framestructure import DirectoryTimeFrame, DirectoryTimeFrameInterface

# Local Packages #
from .hdf5xltekframe import HDF5XLTEKFrame


# Definitions #
# Classes #
class XLTEKDayFrame(DirectoryTimeFrame):
    """A frame for a directory which contains a day's worth of XLTEK EEG data.

    Class Attributes:
        default_frame_type: The default type frame to create from the contents of the directory.

    Attributes:
        glob_condition: The glob string to use when using the glob method.
        date_format: The format of the date string.
        subject_id: The subject ID of the file.

    Args:
        s_id: The subject ID.
        path: The path for this frame to wrap.
        frames: An iterable holding frames/objects to store in this frame.
        mode: Determines if the contents of this frame are editable or not.
        update: Determines if this frame will start_timestamp updating or not.
        open_: Determines if the frames will remain open after construction.
        load: Determines if the frames will be constructed.
        init: Determines if this object will construct.
        **kwargs: The keyword arguments to create contained frames.
    """
    default_frame_type = HDF5XLTEKFrame

    # Class Methods #
    @classmethod
    def validate_path(cls, path: str | pathlib.Path) -> bool:
        """Validates if the path can be used as a XLTEK Day.

        Args:
            path: The path to directory/file object that this frame will wrap.

        Returns:
            If the path is usable.
        """
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        try:
            files = list(path.glob("*.h5"))
            if files:
                return True
            else:
                return False
        except IOError:
            return False

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        s_id: str | pathlib.Path | None = None,
        path: pathlib.Path | str | None = None,
        frames: Iterable[DirectoryTimeFrameInterface] | None = None,
        mode: str = 'r',
        update: bool = False,
        open_: bool = False,
        load: bool = True,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Parent Attributes #
        super().__init__(init=False)

        # Set Attributes #
        self.glob_condition: str = "*.h5"
        self.date_format: str = "%Y-%m-%d"

        self.subject_id: str | None = None

        # Object Construction #
        if init:
            self.construct(
                s_id=s_id,
                path=path,
                frames=frames,
                mode=mode,
                update=update,
                open_=open_,
                load=load,
                **kwargs,
            )

    # Instance Methods
    # Constructors/Destructors
    def construct(
        self,
        s_id: str | None = None,
        path: pathlib.Path | str | None = None,
        frames: Iterable[DirectoryTimeFrameInterface] | None = None,
        mode: str = 'r',
        update: bool = False,
        open_: bool = False,
        load: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            s_id: The subject ID of the file.
            path: The path for this frame to wrap.
            frames: An iterable holding frames/objects to store in this frame.
            mode: Determines if the contents of this frame are editable or not.
            update: Determines if this frame will start_timestamp updating or not.
            open_: Determines if the frames will remain open after construction.
            load: Determines if the frames will be constructed.
            **kwargs: The keyword arguments to create contained frames.
        """
        if s_id is not None:
            self.subject_id = s_id

        super().construct(
            path=path,
            frames=frames,
            mode=mode,
            update=update,
            open_=open_,
            load=load,
            s_id=s_id,
            **kwargs,
        )

        if not self.frames:
            try:
                self.date_from_path()
            except (ValueError, IndexError):
                pass

        if not open_:
            self.close()

    def construct_frames(self, open_=False, **kwargs) -> None:
        """Constructs the frames for this object.

        Args:
            open_: Determines if the frames will remain open after construction.
            **kwargs: The keyword arguments to create contained frames.
        """
        for path in self.path.glob(self.glob_condition):
            if path not in self.frame_paths:
                file_frame = self.frame_type.new_validated(path, open_=open_, **kwargs)
                if self.frame_creation_condition(frame=file_frame):
                    self.frames.append(file_frame)
                    self.frame_paths.add(path)
        self.frames.sort(key=lambda frame: frame.start_timestamp)
        self.clear_caches()

    def frame_creation_condition(
        self,
        path: str | pathlib.Path | None = None,
        frame: DirectoryTimeFrameInterface | None = None,
        **kwargs: Any,
    ) -> bool:
        """Determines if a frame will be constructed.

        Args:
            path: The path to create a frame from.
            frame: A frame to check if it should be created.
            **kwargs: Additional keyword arguments for deciding if the frame will be created.

        Returns:
            If the path can be constructed.
        """
        return True if frame is not None else False

    # File
    def date_from_path(self) -> None:
        """Sets date from the name of the directory."""
        date_string = self.path.parts[-1].split('_')[1]
        self._date = datetime.datetime.strptime(date_string, self.date_format).date()
