"""xltekcdfs.py

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
from typing import ClassVar, Any

# Third-Party Packages #
from baseobjects.operations import update_recursive
from cdfs import BaseCDFS
from sqlalchemy.orm import DeclarativeBase

# Local Packages #
from .xltekcdfsasyncschema import XLTEKCDFSAsyncSchema, XLTEKMetaInformationTable, XLTEKContentsTable, XLTEKVideosTable
from .components import XLTEKMetaInformationCDFSComponent, XLTEKContentsCDFSComponent


# Definitions #
# Classes #
class XLTEKCDFS(BaseCDFS):
    """

    Class Attributes:

    Attributes:

    Args:

    """

    # Class Attributes #
    default_component_types: ClassVar[dict[str, tuple[type, dict[str, Any]]]] = {
        "meta_information": (XLTEKMetaInformationCDFSComponent, {"table_name": "meta_information"}),
        "contents": (XLTEKContentsCDFSComponent, {"table_name": "contents"}),
    }

    # Attributes #
    schema: type[DeclarativeBase] | None = XLTEKCDFSAsyncSchema

    tables: dict[str, type[DeclarativeBase]] = {
        "meta_information": XLTEKMetaInformationTable,
        "contents": XLTEKContentsTable,
        "videos": XLTEKVideosTable,
    }

    # Properties #
    @property
    def name(self) -> str | None:
        """The subject ID from the file attributes."""
        return self.components["meta_information"].name

    @name.setter
    def name(self, value: str) -> None:
        self.components["meta_information"].name = value

    @property
    def start_datetime(self) -> str | None:
        """The start datetime from the file attributes."""
        return self.components["meta_information"].start_datetime

    @start_datetime.setter
    def start_datetime(self, value: str) -> None:
        self.components["meta_information"].start_datetime = value

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: pathlib.Path | str | None = None,
        name: str | None = None,
        mode: str = "r",
        open_: bool = False,
        load: bool = False,
        create: bool = False,
        update: bool = False,
        contents_name: str | None = None,
        component_kwargs: dict[str, dict[str, Any]] | None = None,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(
                path=path,
                name=name,
                mode=mode,
                open_=open_,
                load=load,
                create=create,
                update=update,
                contents_name=contents_name,
                component_kwargs=component_kwargs,
                **kwargs,
            )

    # Instance Methods
    # Constructors/Destructors
    def construct(
        self,
        path: pathlib.Path | str | None = None,
        name: str | None = None,
        mode: str = "r",
        open_: bool = False,
        load: bool = False,
        create: bool = False,
        update: bool = False,
        contents_name: str | None = None,
        component_kwargs: dict[str, dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            path: The path for this proxy to wrap.
            name: The subject ID.
            mode: Determines if the contents of this proxy are editable or not.
            update: Determines if this proxy will start_timestamp updating or not.
            open_: Determines if the arrays will remain open after construction.
            load: Determines if the arrays will be constructed.
            **kwargs: The keyword arguments to create contained arrays.
        """
        meta_information = {"name": name}
        meta_kwargs = {"init_info": meta_information}
        new_component_kwargs = {"meta_information": meta_kwargs}
        update_recursive(new_component_kwargs, component_kwargs)

        super().construct(
            path=path,
            mode=mode,
            open_=open_,
            load=load,
            create=create,
            update=update,
            contents_name=contents_name,
            component_kwargs=new_component_kwargs,
            **kwargs,
        )
