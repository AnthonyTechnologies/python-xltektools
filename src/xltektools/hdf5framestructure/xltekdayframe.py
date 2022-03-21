""" xltekdayframe.py

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
    """A frame for directory which contains a day's worth of XLTEK EEG data.

    Class Attributes:
        default_frame_type: The default type frame to create from the contents of the directory.

    Attributes:
        _path: The path of the directory to wrap.
        glob_condition: The glob string to use when using the glob method.
        frame_type: The type of frame to create from the contents of the directory.
        frame_paths: The paths to the contained frames.

    Args:
        path: The path for this frame to wrap.
        frames: An iterable holding frames/objects to store in this frame.
        mode: Determines if the contents of this frame are editable or not.
        update: Determines if this frame will start_timestamp updating or not.
        open_: Determines if the frames will remain open after construction.
        **kwargs: The keyword arguments to create contained frames.
        init: Determines if this object will construct.
    """
    default_frame_type = HDF5XLTEKFrame

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: pathlib.Path | str | None = None,
        frames: Iterable[DirectoryTimeFrameInterface] | None = None,
        mode: str = 'r',
        update: bool = False,
        open_: bool = False,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Parent Attributes #
        super().__init__(init=False)

        # Set Attributes #
        self.glob_condition = "*.h5"

        # Object Construction #
        if init:
            self.construct(path=path, frames=frames, mode=mode, update=update, open_=open_, **kwargs)

    # Instance Methods
    # Constructors/Destructors
    def construct(
        self,
        path: pathlib.Path | str | None = None,
        frames: Iterable[DirectoryTimeFrameInterface] | None = None,
        mode: str = 'a',
        update: bool = False,
        open_: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            path: The path for this frame to wrap.
            frames: An iterable holding frames/objects to store in this frame.
            mode: Determines if the contents of this frame are editable or not.
            update: Determines if this frame will start_timestamp updating or not.
            open_: Determines if the frames will remain open after construction.
            **kwargs: The keyword arguments to create contained frames.
        """
        super().construct(path=path, frames=frames, mode=mode, update=update, open_=True, **kwargs)

        if not self.frames:
            try:
                self.date_from_path()
            except (ValueError, IndexError):
                pass

        if not open_:
            self.close()

    # Constructors/Destructors
    def construct_frames(self, **kwargs):
        for path in self.path.glob(self.glob_condition):
            if path not in self.frame_names:
                file_frame = self.frame_type.new_validated(path, **kwargs)
                if self.frame_creation_condition(file_frame):
                    self.frames.append(file_frame)
                    self.frame_names.add(path)
        self.frames.sort(key=lambda frame: frame.start)

    # Frames
    def frame_creation_condition(self, path):
        return True

    # File
    def date_from_path(self):
        date_string = self.path.parts[-1].split('_')[1]
        self._date = datetime.datetime.strptime(date_string, self.date_format).date()
