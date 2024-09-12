from instorage.allowed_origins.allowed_origin_repo import AllowedOriginRepository
from instorage.roles.permissions import Permission, validate_permissions
from instorage.users.user import UserInDB


class AllowedOriginService:
    def __init__(self, user: UserInDB, repo: AllowedOriginRepository):
        self.user = user
        self.repo = repo

    @validate_permissions(Permission.ADMIN)
    async def get(self):
        return await self.repo.get_by_tenant(self.user.tenant_id)
