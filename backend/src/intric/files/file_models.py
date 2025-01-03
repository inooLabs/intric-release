from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

from intric.main.models import InDB


class FileType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


class FileBase(BaseModel):
    name: str
    checksum: str
    size: int
    mimetype: Optional[str] = None

    file_type: FileType


class FileBaseWithContent(FileBase):
    text: Optional[str] = None
    blob: Optional[bytes] = None

    @model_validator(mode="after")
    def require_one_of_text_or_image(self) -> "FileBaseWithContent":
        if self.text is None and self.blob is None:
            raise ValueError("One of 'text' or 'blob' is required")

        return self


class FileInfo(InDB, FileBase):
    user_id: UUID
    tenant_id: UUID


class FileCreate(FileBaseWithContent):
    user_id: UUID
    tenant_id: UUID


class File(InDB, FileCreate):
    pass


class FilePublic(InDB):
    name: str
    mimetype: str
    size: int


class AcceptedFileType(BaseModel):
    mimetype: str
    size_limit: int


class Limit(BaseModel):
    max_files: int
    max_size: int


class FileRestrictions(BaseModel):
    accepted_file_types: list[AcceptedFileType]
    limit: Limit