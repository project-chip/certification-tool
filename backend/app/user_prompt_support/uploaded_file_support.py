from abc import abstractmethod
from typing import BinaryIO, Optional, Protocol, runtime_checkable


class UploadFile(Protocol):
    """Protocol to handle file objects uploaded to the backend.

    Attributes:
        file: A tempfile containing the contents of the uploaded file.
        content_type: A str with the content type (MIME type / media type).
        filename: The name of the file.
    """

    file: BinaryIO
    filename: Optional[str]

    @property
    def content_type(self) -> Optional[str]:
        ...


@runtime_checkable
class UploadedFileSupport(Protocol):
    """Support class required for subclasses that request a file upload from user."""

    @abstractmethod
    def handle_uploaded_file(self, file: UploadFile) -> None:
        pass
