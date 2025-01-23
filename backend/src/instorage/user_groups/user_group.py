# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from instorage.main.models import InDB, ModelId
from instorage.users.user import UserInDBBase, UserPublicBase


class UserGroupBase(BaseModel):
    name: str


class UserGroupCreateRequest(UserGroupBase):
    pass


class UserGroupCreate(UserGroupBase):
    tenant_id: UUID


class UserGroupUpdateRequest(UserGroupBase):
    name: Optional[str] = None

    users: list[ModelId] = []


class UserGroupUpdate(UserGroupUpdateRequest):
    id: UUID


class UserGroupInDBBase(UserGroupBase, InDB):
    tenant_id: UUID


class UserGroupInDB(UserGroupInDBBase):
    users: list[UserInDBBase] = []


class UserGroupPublic(UserGroupBase, InDB):
    users: list[UserPublicBase] = []