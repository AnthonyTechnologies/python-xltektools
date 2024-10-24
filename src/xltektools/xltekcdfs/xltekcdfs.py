"""xltekcdfs.py
The main API object for an XLTEK CDFS.
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
    """The main API object for an XLTEK CDFS.

    This class extends the BaseCDFS class and provides additional functionality specific to XLTEK data files.

    Class Attributes:
        default_component_types: A dictionary defining the default component types and their configurations.

    Attributes:
        schema: The schema class for defining the database structure and used for database operations.
        tables: The SQLAlchemy tables managed by this CDFS object.

    Args:
        path: The path to the CDFS. Defaults to None.
        name: The subject ID. Defaults to None.
        mode: Determines if the contents of the CDFS will be editable or not. Defaults to "r".
        open_: Determines if the CDFS will remain open after construction. Defaults to True.
        load: Determines if the CDFS will be constructed. Defaults to True.
        create: Determines if the CDFS will be created. Defaults to False.
        build: Determines if the CDFS will be built upon creation. Defaults to True.
        contents_name: The name of the contents main contents table. Defaults to None.
        component_kwargs: Additional keyword arguments for components. Defaults to None.
        init: Determines if the object will be constructed. Defaults to True.
        **kwargs: Additional keyword arguments.
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
        """The subject ID."""
        return self.components["meta_information"].name

    @name.setter
    def name(self, value: str) -> None:
        self.components["meta_information"].name = value

    @property
    def start_datetime(self) -> str | None:
        """The start datetime."""
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
        open_: bool = True,
        load: bool = True,
        create: bool = False,
        build: bool = True,
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
                build=build,
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
        open_: bool = True,
        load: bool = True,
        create: bool = False,
        build: bool = True,
        contents_name: str | None = None,
        component_kwargs: dict[str, dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            path: The path to the CDFS. Defaults to None.
            name: The subject ID. Defaults to None.
            mode: Determines if the contents of the CDFS will be editable or not. Defaults to "r".
            open_: Determines if the CDFS will remain open after construction. Defaults to True.
            load: Determines if the CDFS will be constructed. Defaults to True.
            create: Determines if the CDFS will be created. Defaults to False.
            build: Determines if the CDFS will be built upon creation. Defaults to True.
            contents_name: The name of the contents main contents table. Defaults to None.
            component_kwargs: Additional keyword arguments for components. Defaults to None.
            **kwargs: Additional keyword arguments.
        """
        # Add default meta information to component kwargs
        meta_information = {"name": name}
        meta_kwargs = {"init_info": meta_information}
        new_component_kwargs = {"meta_information": meta_kwargs}
        update_recursive(new_component_kwargs, component_kwargs or {})

        super().construct(
            path=path,
            mode=mode,
            open_=open_,
            load=load,
            create=create,
            build=build,
            contents_name=contents_name,
            component_kwargs=new_component_kwargs,
            **kwargs,
        )
