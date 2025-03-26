"""ieegxltekcomponent.py

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
from pathlib import Path
from typing import Any, ClassVar

# Third-Party Packages #
from baseobjects.composition import BaseComponent
from mxbids.modalities import IEEG

# Local Packages #
from ...xltekannotations import XLTEKAnnotationsDatabase


# Definitions #
# Classes #
class IEEGXLTEKAnnotationsComponent(BaseComponent):
    """An MXBIDS Component which contains an annotations database as part of its structure.

    Class Attributes:
        namespace: The namespace of the subclass.
        name: The name of which the subclass will be registered as.
        registry: A registry of all subclasses of this class.
        registration: Determines if this class/subclass will be added to the registry.
        default_meta_info: The default meta information about the session.
        cdfs_type: The type of CDFS the session objects of this class will use.

    Attributes:
        _path: The path to session.
        _is_open: Determines if this session and its contents are open.
        _mode: The file mode of this session.
        meta_info: The meta information that describes this session.
        name: The name of this session.
        parent_name: The name of the parent subject of this session.
        cdfs: The CDFS object of this session.

    Args:
        path: The path to the session's directory.
        name: The name of the session.
        parent_path: The parent path of this session.
        mode: The file mode to set this session to.
        create: Determines if this session will be created if it does not exist.
        init: Determines if this object will construct.
        kwargs: The keyword arguments for inheritance.
    """
    # Class Attributes #
    _module_: ClassVar[str | None] = "xltektools.xltekmxbids"

    # Attributes #
    suffix: str = "XLTEKannotations"
    annotations_database: XLTEKAnnotationsDatabase | None = None

    # Instance Methods #
    # Construction/Destruction
    def build(self) -> None:
        """Builds the annotations database for this modality."""
        self.construct_annotations_database(create=True, build=True)

    def load(self) -> None:
        """Loads the annotations database for this modality."""
        self.construct_annotations_database(open_=True, create=False)

    # CDFS Object
    def construct_annotations_database(
        self, 
        file_name: str | None = None,
        open_: bool = False,
        create: bool = False,
        *,
        path: Path | None = None,
        **kwargs: Any,
    ) -> XLTEKAnnotationsDatabase:
        """Creates or loads the Annotations of this modality.

        Args:
            file_name: The name of the annotations database file. If None, the name will be generated from modality.
            open_: Determines if the annotation database will be opened.
            *
            create: Determines if the annotation database will will be created.
            **kwargs: The keyword arguments for the annotations database.

        Returns:
            The CDFS of this modality.
        """
        if path is None:
            if file_name is None:
                file_name = self.generate_file_name()
                
            path = self._composite().path / file_name

        self.annotations_database = XLTEKAnnotationsDatabase(path=path, open_=open_, create=create, **kwargs)
        return self.annotations_database

    def create_annotations_database(self, file_name: str | None = None, **kwargs: Any) -> XLTEKAnnotationsDatabase:
        """Creates the annotations database of this modality.

        Args:
            file_name: The name of the annotations database of the annotations database. If None, the name will be generated from modality.
            **kwargs: The keyword arguments for creating the annotations database.

        Returns:
            The annotations database of this modality.
        """
        return self.construct_annotations_database(file_name=file_name, create=True, **kwargs)

    def require_annotations_database(self, file_name: str | None = None, **kwargs: Any) -> XLTEKAnnotationsDatabase:
        """Gets the annotations_database of this modality, creating it if it does not exsist.

        Args:
            file_name: The name of the annotations database file. If None, the name will be generated from modality.
            **kwargs: The keyword arguments for creating the annotations_database.

        Returns:
            The annotations_database of this modality.
        """
        if self.annotations_database is None:
            self.construct_annotations_database(file_name=file_name, create=True, **kwargs)

        return self.annotations_database

    def load_annotations_database(self, file_name: str | None = None, **kwargs: Any) -> XLTEKAnnotationsDatabase:
        """Loads the annotations database of this modality from the file system.

        Args:
            file_name: The name of the annotations database file. If None, the name will be generated from modality.
            **kwargs: The keyword arguments for creating the annotations database.

        Returns:
            The annotations_database of this modality.
        """
        return self.construct_annotations_database(file_name=file_name, open_=True, **kwargs)

    def get_annotations_database(self, file_name: str | None = None, **kwargs: Any) -> XLTEKAnnotationsDatabase:
        """Gets the annotations database of this modality, loading it if it is not present.

        Args:
            file_name: The name of the annotations database file. If None, the name will be generated from modality.
            **kwargs: The keyword arguments for creating the annotations database.

        Returns:
            The annotations_database of this modality.
        """
        if self.annotations_database is None:
            self.construct_annotations_database(file_name=file_name, **kwargs)

        return self.annotations_database

    # File
    def generate_file_name(self) -> str:
        """Generates a name for the annotations database from the subject and session name.

        Returns:
            The name of the annotations database.
        """
        return f"{self._composite().full_name}_{self.suffix}.sqlite3"
    

# Registration #
IEEG.component_types_register.register_class(IEEGXLTEKAnnotationsComponent)
