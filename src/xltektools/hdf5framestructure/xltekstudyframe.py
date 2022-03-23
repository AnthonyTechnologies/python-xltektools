""" xltekstudyframe.py
A frame for a directory which contains a subject's worth of XLTEK EEG data.
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
import pathlib
from typing import Any

# Third-Party Packages #
from framestructure import DirectoryTimeFrame, DirectoryTimeFrameInterface

# Local Packages #
from .xltekdayframe import XLTEKDayFrame


# Definitions #
# Classes #
class XLTEKStudyFrame(DirectoryTimeFrame):
    """A frame for a directory which contains a subject's worth of XLTEK EEG data.

    Class Attributes:
        default_frame_type: The default type frame to create from the contents of the directory.

    Attributes:
        _studies_path: The parent directory to this XLTEK study frame.
        subject_id: The subject ID.

    Args:
        path: The path for this frame to wrap.
        s_id: The subject ID.
        studies_path: The parent directory to this XLTEK study frame.
        frames: An iterable holding frames/objects to store in this frame.
        mode: Determines if the contents of this frame are editable or not.
        update: Determines if this frame will start_timestamp updating or not.
        open_: Determines if the frames will remain open after construction.
        load: Determines if the frames will be constructed.
        init: Determines if this object will construct.
        **kwargs: The keyword arguments to create contained frames.
    """
    default_frame_type = XLTEKDayFrame

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: pathlib.Path | str | None = None,
        s_id: str | None = None,
        studies_path: pathlib.Path | str | None = None,
        frames: Iterable[DirectoryTimeFrameInterface] | None = None,
        mode: str = 'r',
        update: bool = False,
        open_: bool = True,
        load: bool = True,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Parent Attributes #
        super().__init__(init=False)

        # Set Attributes #
        self._studies_path = None
        self.subject_id = ""

        # Object Construction #
        if init:
            self.construct(
                path=path,
                s_id=s_id,
                studies_path=studies_path,
                frames=frames,
                mode=mode,
                update=update,
                load=load,
                open_=open_,
                **kwargs,
            )

    @property
    def studies_path(self):
        """The parent directory to this XLTEK study frame."""
        return self._studies_path

    @studies_path.setter
    def studies_path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._studies_path = value
        else:
            self._studies_path = pathlib.Path(value)

    # Instance Methods
    # Constructors/Destructors
    def construct(
        self,
        path: pathlib.Path | str | None = None,
        s_id: str | None = None,
        studies_path: pathlib.Path | str | None = None,
        frames: Iterable[DirectoryTimeFrameInterface] | None = None,
        mode: str = 'r',
        update: bool = False,
        open_: bool = False,
        load: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            path: The path for this frame to wrap.
            s_id: The subject ID.
            studies_path: The parent directory to this XLTEK study frame.
            frames: An iterable holding frames/objects to store in this frame.
            mode: Determines if the contents of this frame are editable or not.
            update: Determines if this frame will start_timestamp updating or not.
            open_: Determines if the frames will remain open after construction.
            load: Determines if the frames will be constructed.
            **kwargs: The keyword arguments to create contained frames.
        """
        if s_id is not None:
            self.subject_id = s_id

        if studies_path is not None:
            self.studies_path = studies_path

        if path is None and (s_id is not None or studies_path is not None):
            path = pathlib.Path(self.studies_path, self.subject_id)

        super().construct(path=path, frames=frames, mode=mode, update=update, open_=open_, load=load, **kwargs)

        if self.path is not None and self.studies_path is None:
            self.studies_path = self.path.parent

    def construct_frames(self, open_=False, **kwargs) -> None:
        """Constructs the frames for this object.

        Args:
            open_: Determines if the frames will remain open after construction.
            **kwargs: The keyword arguments to create contained frames.
        """
        for path in self.path.glob(self.glob_condition):
            if path not in self.frame_paths:
                if self.frame_creation_condition(path):
                    self.frames.append(self.frame_type(s_id=self.subject_id, path=path, open_=open_, **kwargs))
                    self.frame_paths.add(path)
        self.frames.sort(key=lambda frame: frame.start_timestamp)
        self.clear_caches()
