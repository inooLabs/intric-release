from typing import TYPE_CHECKING, Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased, selectinload

from intric.ai_models.completion_models.completion_model import CompletionModelSparse
from intric.ai_models.embedding_models.embedding_model import EmbeddingModelSparse
from intric.database.database import AsyncSession
from intric.database.tables.ai_models_table import (
    CompletionModels,
    CompletionModelSettings,
    EmbeddingModels,
    EmbeddingModelSettings,
)
from intric.database.tables.assistant_table import Assistants
from intric.database.tables.groups_table import Groups
from intric.database.tables.info_blobs_table import InfoBlobs
from intric.database.tables.spaces_table import (
    Spaces,
    SpacesCompletionModels,
    SpacesEmbeddingModels,
    SpacesUsers,
)
from intric.database.tables.websites_table import CrawlRuns, Websites
from intric.main.exceptions import UniqueException
from intric.spaces.api.space_models import SpaceMember
from intric.spaces.space import Space
from intric.spaces.space_factory import SpaceFactory

if TYPE_CHECKING:
    from intric.assistants.assistant import Assistant
    from intric.assistants.assistant_repo import AssistantRepository


class SpaceRepository:
    def __init__(
        self,
        session: AsyncSession,
        factory: SpaceFactory,
        assistant_repo: "AssistantRepository",
    ):
        self.session = session
        self.factory = factory
        self.assistant_repo = assistant_repo

    def _options(self):
        return [
            selectinload(Spaces.members).selectinload(SpacesUsers.user),
            selectinload(Spaces.assistants),
            selectinload(Spaces.services),
            selectinload(Spaces.websites)
            .selectinload(Websites.latest_crawl)
            .selectinload(CrawlRuns.job),
            selectinload(Spaces.websites).selectinload(Websites.embedding_model),
            selectinload(Spaces.apps),
        ]

    async def _get_groups(self, space_id: UUID):
        query = (
            sa.select(
                Groups,
                sa.func.coalesce(sa.func.count(InfoBlobs.id).label("infoblob_count")),
            )
            .outerjoin(InfoBlobs, Groups.id == InfoBlobs.group_id)
            .where(Groups.space_id == space_id)
            .group_by(Groups.id)
            .order_by(Groups.created_at)
            .options(selectinload(Groups.embedding_model))
        )

        res = await self.session.execute(query)
        return res.all()

    async def _get_completion_models(self, space_in_db: Spaces):
        space_id = space_in_db.id
        tenant_id = space_in_db.tenant_id

        cm = aliased(CompletionModels)
        cms = aliased(CompletionModelSettings)
        scm = aliased(SpacesCompletionModels)

        stmt = (
            sa.select(cm, cms.is_org_enabled)
            .join(scm, scm.completion_model_id == cm.id)
            .outerjoin(
                cms,
                sa.and_(
                    cms.completion_model_id == cm.id,
                    cms.tenant_id == tenant_id,
                ),
            )
            .filter(scm.space_id == space_id)
        )

        res = await self.session.execute(stmt)
        return res.all()

    async def _get_embedding_models(self, space_in_db: Spaces):
        space_id = space_in_db.id
        tenant_id = space_in_db.tenant_id

        em = aliased(EmbeddingModels)
        ems = aliased(EmbeddingModelSettings)
        sem = aliased(SpacesEmbeddingModels)

        stmt = (
            sa.select(em, ems.is_org_enabled)
            .join(sem, sem.embedding_model_id == em.id)
            .outerjoin(
                ems,
                sa.and_(
                    ems.embedding_model_id == em.id,
                    ems.tenant_id == tenant_id,
                ),
            )
            .filter(sem.space_id == space_id)
        )

        res = await self.session.execute(stmt)
        return res.all()

    async def _set_embedding_models(
        self, space_in_db: Spaces, embedding_models: list[EmbeddingModelSparse]
    ):
        # Delete all
        stmt = sa.delete(SpacesEmbeddingModels).where(
            SpacesEmbeddingModels.space_id == space_in_db.id
        )
        await self.session.execute(stmt)

        if embedding_models:
            stmt = sa.insert(SpacesEmbeddingModels).values(
                [
                    dict(embedding_model_id=embedding_model.id, space_id=space_in_db.id)
                    for embedding_model in embedding_models
                ]
            )
            await self.session.execute(stmt)

    async def _set_completion_models(
        self, space_in_db: Spaces, completion_models: list[CompletionModelSparse]
    ):
        # Delete all
        stmt = sa.delete(SpacesCompletionModels).where(
            SpacesCompletionModels.space_id == space_in_db.id
        )
        await self.session.execute(stmt)

        if completion_models:
            stmt = sa.insert(SpacesCompletionModels).values(
                [
                    dict(
                        completion_model_id=completion_model.id, space_id=space_in_db.id
                    )
                    for completion_model in completion_models
                ]
            )
            await self.session.execute(stmt)

    async def _set_members(self, space_in_db: Spaces, members: dict[UUID, SpaceMember]):
        # Delete all
        stmt = sa.delete(SpacesUsers).where(SpacesUsers.space_id == space_in_db.id)
        await self.session.execute(stmt)

        # Add members
        if members:
            spaces_users = [
                dict(
                    space_id=space_in_db.id,
                    user_id=member.id,
                    role=member.role.value,
                )
                for member in members.values()
            ]

            stmt = sa.insert(SpacesUsers).values(spaces_users)
            await self.session.execute(stmt)

        # This allows the newly added members to be reflected in the space
        await self.session.refresh(space_in_db)

    async def _set_default_assistant(
        self, space_in_db: Spaces, assistant: Optional["Assistant"]
    ):
        if assistant is None:
            return

        # Unset all others
        stmt = (
            sa.update(Assistants)
            .values(is_default=False)
            .where(Assistants.space_id == space_in_db.id)
            .where(Assistants.id != assistant.id)
        )
        await self.session.execute(stmt)

        # Set the default to default
        stmt = (
            sa.update(Assistants)
            .values(is_default=True)
            .where(Assistants.id == assistant.id)
        )
        await self.session.execute(stmt)

    async def _get_default_assistant(self, space_in_db: Spaces):
        stmt = (
            sa.select(Assistants.id)
            .where(Assistants.space_id == space_in_db.id)
            .where(Assistants.is_default)
        )
        assistant_id = await self.session.scalar(stmt)

        return await self.assistant_repo.get_by_id(assistant_id)

    async def _get_from_query(self, query: sa.Select):
        entry_in_db = await self.get_record_with_options(query)

        if not entry_in_db:
            return

        groups = await self._get_groups(entry_in_db.id)
        completion_models = await self._get_completion_models(entry_in_db)
        embedding_models = await self._get_embedding_models(entry_in_db)
        default_assistant = await self._get_default_assistant(entry_in_db)

        return self.factory.create_space_from_db(
            entry_in_db,
            groups_in_db=groups,
            completion_models_in_db=completion_models,
            embedding_models_in_db=embedding_models,
            default_assistant=default_assistant,
        )

    async def get_record_with_options(self, query):
        for option in self._options():
            query = query.options(option)

        return await self.session.scalar(query)

    async def get_records_with_options(self, query):
        for option in self._options():
            query = query.options(option)

        return await self.session.scalars(query)

    async def add(self, space: Space) -> Space:
        query = (
            sa.insert(Spaces)
            .values(
                name=space.name,
                description=space.description,
                tenant_id=space.tenant_id,
                user_id=space.user_id,
            )
            .returning(Spaces)
        )

        try:
            entry_in_db = await self.get_record_with_options(query)
        except IntegrityError as e:
            raise UniqueException("Users can only have one personal space") from e

        await self._set_completion_models(entry_in_db, space.completion_models)
        await self._set_embedding_models(entry_in_db, space.embedding_models)
        await self._set_members(entry_in_db, space.members)

        completion_models = await self._get_completion_models(entry_in_db)
        embedding_models = await self._get_embedding_models(entry_in_db)

        return self.factory.create_space_from_db(
            entry_in_db,
            completion_models_in_db=completion_models,
            embedding_models_in_db=embedding_models,
        )

    async def get(self, id: UUID) -> Space:
        query = sa.select(Spaces).where(Spaces.id == id)

        return await self._get_from_query(query)

    async def get_personal_space(self, user_id: UUID) -> Space:
        query = sa.select(Spaces).where(Spaces.user_id == user_id)

        return await self._get_from_query(query)

    async def update(self, space: Space) -> Space:
        query = (
            sa.update(Spaces)
            .values(name=space.name, description=space.description)
            .where(Spaces.id == space.id)
            .returning(Spaces)
        )
        entry_in_db = await self.get_record_with_options(query)

        groups = await self._get_groups(space.id)

        await self._set_completion_models(entry_in_db, space.completion_models)
        await self._set_embedding_models(entry_in_db, space.embedding_models)
        await self._set_members(entry_in_db, space.members)
        await self._set_default_assistant(entry_in_db, space.default_assistant)

        completion_models = await self._get_completion_models(entry_in_db)
        embedding_models = await self._get_embedding_models(entry_in_db)

        return self.factory.create_space_from_db(
            entry_in_db,
            groups_in_db=groups,
            completion_models_in_db=completion_models,
            embedding_models_in_db=embedding_models,
            default_assistant=space.default_assistant,
        )

    async def delete(self, id: UUID):
        query = sa.delete(Spaces).where(Spaces.id == id)
        await self.session.execute(query)

    async def get_spaces(self, user_id: UUID) -> list[Space]:
        query = (
            sa.select(Spaces)
            .join(SpacesUsers, Spaces.members)
            .where(SpacesUsers.user_id == user_id)
            .distinct()
            .order_by(Spaces.created_at)
        )

        records = await self.get_records_with_options(query)

        return [self.factory.create_space_from_db(record) for record in records]