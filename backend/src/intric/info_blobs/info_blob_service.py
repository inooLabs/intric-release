from typing import TYPE_CHECKING, Optional
from uuid import UUID

from intric.actors import SpaceAction
from intric.admin.quota_service import QuotaService
from intric.groups_legacy.group_service import GroupService
from intric.info_blobs.info_blob import (
    InfoBlobAdd,
    InfoBlobInDB,
    InfoBlobMetadataFilter,
    InfoBlobMetadataFilterPublic,
    InfoBlobUpdate,
)
from intric.info_blobs.info_blob_repo import InfoBlobRepository
from intric.main.exceptions import (
    NameCollisionException,
    NotFoundException,
    UnauthorizedException,
)
from intric.main.logging import get_logger
from intric.users.user import UserInDB

if TYPE_CHECKING:
    from intric.actors import ActorManager
    from intric.spaces.space_repo import SpaceRepository
    from intric.spaces.space_service import SpaceService
    from intric.websites.infrastructure.update_website_size_service import (
        UpdateWebsiteSizeService,
    )

logger = get_logger(__name__)


class InfoBlobService:
    def __init__(
        self,
        *,
        repo: InfoBlobRepository,
        space_repo: "SpaceRepository",
        user: UserInDB,
        quota_service: QuotaService,
        group_service: GroupService,
        update_website_size_service: "UpdateWebsiteSizeService",
        space_service: "SpaceService",
        actor_manager: "ActorManager",
    ):
        self.repo = repo
        self.space_repo = space_repo
        self.group_service = group_service
        self.update_website_size_service = update_website_size_service
        self.user = user
        self.quota_service = quota_service
        self.space_service = space_service
        self.actor_manager = actor_manager

    async def _get_actor(self, info_blob: Optional[InfoBlobInDB], group_id: Optional[UUID]):
        if info_blob is None and group_id is None:
            raise ValueError("One of info_blob and group_id has to exist")

        if group_id is not None:
            space = await self.space_repo.get_space_by_collection(collection_id=group_id)

        else:
            if info_blob.group_id is not None:
                space = await self.space_repo.get_space_by_collection(info_blob.group_id)
            elif info_blob.website_id is not None:
                space = await self.space_repo.get_space_by_website(info_blob.website_id)
            elif info_blob.integration_knowledge_id is not None:
                space = await self.space_repo.get_space_by_integration_knowledge(
                    info_blob.integration_knowledge_id
                )

        return self.actor_manager.get_space_actor_from_space(space)

    async def _validate(
        self,
        info_blob: Optional[InfoBlobInDB],
        action: SpaceAction = SpaceAction.READ,
    ):
        if info_blob is None:
            raise NotFoundException("InfoBlob not found")

        await self._can_perform_action(info_blob=info_blob, group_id=None, action=action)

    async def _can_perform_action(
        self,
        info_blob: Optional[InfoBlobInDB] = None,
        group_id: Optional[UUID] = None,
        action: SpaceAction = SpaceAction.READ,
    ):
        actor = await self._get_actor(info_blob=info_blob, group_id=group_id)
        match action:
            case SpaceAction.READ:
                if not actor.can_read_info_blobs():
                    raise UnauthorizedException()
            case SpaceAction.CREATE:
                if not actor.can_create_info_blobs():
                    raise UnauthorizedException()
            case SpaceAction.DELETE:
                if not actor.can_delete_info_blobs():
                    raise UnauthorizedException()

    async def _delete_if_same_title(self, info_blob: InfoBlobAdd):
        if info_blob.title:
            if info_blob.group_id:
                info_blob_deleted = await self.repo.delete_by_title_and_group(
                    info_blob.title, info_blob.group_id
                )

                if info_blob_deleted is not None:
                    logger.debug(
                        f"Info blob ({info_blob_deleted.title}) in group "
                        f"({info_blob.group_id}) was replaced"
                    )

            elif info_blob.website_id:
                info_blob_deleted = await self.repo.delete_by_title_and_website(
                    info_blob.title, info_blob.website_id
                )

                if info_blob_deleted is not None:
                    logger.debug(
                        f"Info blob ({info_blob_deleted.title}) in website "
                        f"({info_blob.website_id}) was replaced"
                    )

    async def add_info_blob_without_validation(self, info_blob: InfoBlobAdd):
        await self._delete_if_same_title(info_blob)
        size_of_text = await self.quota_service.add_text(info_blob.text)
        info_blob.size = size_of_text
        info_blob_in_db = await self.repo.add(info_blob)

        return info_blob_in_db

    async def add_info_blob(self, info_blob: InfoBlobAdd):
        info_blob_in_db = await self.add_info_blob_without_validation(info_blob)

        await self._validate(info_blob_in_db)

        return info_blob_in_db

    async def add_info_blobs(self, group_id: UUID, info_blobs: list[InfoBlobAdd]):
        await self._can_perform_action(group_id=group_id, action=SpaceAction.CREATE)

        return [await self.add_info_blob(blob) for blob in info_blobs]

    async def update_info_blob(self, info_blob: InfoBlobUpdate):
        current_info_blob = await self.repo.get(info_blob.id)

        if info_blob.title:
            info_blob_with_same_name = await self.repo.get_by_title_and_group(
                info_blob.title, current_info_blob.group.id
            )

            if info_blob_with_same_name is not None:
                raise NameCollisionException(
                    "Info blob with same name already exists in the same group"
                )

        info_blob_updated = await self.repo.update(info_blob)

        await self._validate(info_blob_updated, action=SpaceAction.EDIT)

        return info_blob_updated

    async def update_info_blob_size(self, info_blob_id: UUID):
        updated_info_blob = await self.repo.update_size(info_blob_id=info_blob_id)

        if updated_info_blob.group_id is not None:
            await self.group_service.update_group_size(updated_info_blob.group_id)
        if updated_info_blob.website_id is not None:
            await self.update_website_size_service.update_website_size(updated_info_blob.website_id)

        return updated_info_blob

    async def get_by_id(self, id: str):
        blob = await self.repo.get(id)

        await self._validate(blob)

        return blob

    async def get_by_user(self, metadata_filter: InfoBlobMetadataFilter | None = None):
        info_blobs = await self.repo.get_by_user(user_id=self.user.id)

        if metadata_filter:

            def filter_func(item: InfoBlobInDB):
                filter_dict = metadata_filter.model_dump(exclude_none=True)
                item_dict = item.model_dump()
                return filter_dict.items() <= item_dict.items()

            info_blobs = list(filter(filter_func, info_blobs))

        return [blob for blob in info_blobs]

    async def get_by_filter(
        self,
        metadata_filter: InfoBlobMetadataFilterPublic,
    ):
        metadata_filter_with_user = InfoBlobMetadataFilter(
            **metadata_filter.model_dump(), user_id=self.user.id
        )
        return await self.get_by_user(metadata_filter_with_user)

    async def get_by_group(self, id: UUID) -> list[InfoBlobInDB]:
        group = await self.group_service.get_group(id)
        return await self.repo.get_by_group(group.id)

    async def get_by_website(self, id: UUID) -> list[InfoBlobInDB]:
        space = await self.space_service.get_space_by_website(website_id=id)
        actor = self.actor_manager.get_space_actor_from_space(space)

        if not actor.can_read_info_blobs():
            raise UnauthorizedException()

        return await self.repo.get_by_website(website_id=id)

    async def delete(self, id: str):
        info_blob_deleted = await self.repo.delete(id)

        await self._validate(info_blob_deleted, action=SpaceAction.DELETE)

        return info_blob_deleted
