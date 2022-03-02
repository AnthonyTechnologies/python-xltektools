""" xltekstudyframe.py

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
import pathlib

# Third-Party Packages #
from framestructure import DirectoryTimeFrame

# Local Packages #
from .xltekdayframe import XLTEKDayFrame


# Definitions #
# Classes #
class XLTEKStudyFrame(DirectoryTimeFrame):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    default_frame_type = XLTEKDayFrame

    # Magic Methods #
    # Construction/Destruction
    def __init__(self, s_id=None, studies_path=None, path=None, frames=None, mode='r', update=True,
                 open_=True, init=True, **kwargs):
        super().__init__(init=False)

        self._studies_path = None
        self.subject_id = ""

        if init:
            self.construct(s_id=s_id, studies_path=studies_path, path=path, frames=frames, mode=mode, update=update,
                           open_=open_, **kwargs)

    @property
    def studies_path(self):
        return self._studies_path

    @studies_path.setter
    def studies_path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._studies_path = value
        else:
            self._studies_path = pathlib.Path(value)

    # Instance Methods
    # Constructors/Destructors
    def construct(self, s_id=None, studies_path=None, path=None, frames=None, mode='r',
                  update=True, open_=True, **kwargs):
        if s_id is not None:
            self.subject_id = s_id

        if studies_path is not None:
            self.studies_path = studies_path

        if path is None:
            path = pathlib.Path(self.studies_path, self.subject_id)

        super().construct(path=path, frames=frames, mode=mode, update=update, open_=open_, **kwargs)
