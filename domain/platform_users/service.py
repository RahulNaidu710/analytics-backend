from datetime import datetime

from beanie import PydanticObjectId

from authorisation import OAuthUser
from utils.errors import BusinessError

from .models import PlatformUser


class PlatformUserService:
    async def create_user_if_not_exists(self, oauth_user: OAuthUser):
        existing_user = await PlatformUser.find_one(
            PlatformUser.email == oauth_user.email
        )
        if existing_user:
            if not existing_user.is_signed_up:
                return await self._upgrade_invited_user(
                    oauth_user=oauth_user, id=existing_user.id
                )
            else:
                return existing_user
        return await self._create_user(oauth_user)

    async def create_user_with_password(
        self, first_name: str, last_name: str, email: str, password_hash: str
    ):
        email = email.lower()
        existing_user = await PlatformUser.find_one(PlatformUser.email == email)
        if existing_user:
            if not existing_user.is_signed_up:
                existing_user.first_name = first_name
                existing_user.last_name = last_name
                existing_user.email = email
                existing_user.password = password_hash
                existing_user.has_visted_sheets = False
                await existing_user.save()
                return existing_user
            raise BusinessError("User already exists with this email")

        platform_user = PlatformUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password_hash,
            has_visted_sheets=False,
        )
        await platform_user.insert()
        return platform_user

    async def reset_user_password(self, email: str, hashed_password: str):
        email = email.lower()
        await PlatformUser.find_one(PlatformUser.email == email).update(
            {"$set": {"password": hashed_password}}
        )
        return await PlatformUser.find_one(PlatformUser.email == email)

    async def save_password(self, user: PlatformUser, password_hash: str):
        user.password = password_hash
        return await user.save()

    async def _build_user(self, oauth_user: OAuthUser):
        return PlatformUser(
            first_name=oauth_user.given_name,
            last_name=oauth_user.family_name,
            email=oauth_user.email,
            picture=oauth_user.picture,
            has_visted_sheets=False,
        )

    async def _create_user(self, oauth_user: OAuthUser):
        platform_user = await self._build_user(oauth_user=oauth_user)
        await platform_user.insert()
        return platform_user

    async def get_user(self, id: str):
        return await PlatformUser.get(id)

    async def get_user_by_email(self, email: str):
        return await PlatformUser.find_one(PlatformUser.email == email)

    async def get_user_by_api_key(self, api_key: str):
        return await PlatformUser.find_one(PlatformUser.api_key == api_key)

    async def save_slack_credentials(self, user_id, slack_url, slack_channel):
        await PlatformUser.find_one(
            PlatformUser.id == PydanticObjectId(user_id),
        ).update({"$set": {"slack_url": slack_url, "slack_channel": slack_channel}})

        return

    async def remove_slack_credentials(self, user_id):
        await PlatformUser.find_one(
            PlatformUser.id == PydanticObjectId(user_id),
        ).update({"$unset": {"slack_url": 1, "slack_channel": 1}})

    async def update_visited_sheets_status(self, user_id):
        await PlatformUser.find_one(
            PlatformUser.id == PydanticObjectId(user_id),
        ).update({"$set": {"has_visted_sheets": True}})

    async def update_sheet_token(self, user_id, token: str):
        await PlatformUser.find_one(
            PlatformUser.id == PydanticObjectId(user_id),
        ).update({"$set": {"sheet_token": token}})

    async def update_api_key(self, user_id: str, api_key: str):
        await PlatformUser.find_one(
            PlatformUser.id == PydanticObjectId(user_id),
        ).update({"$set": {"api_key": api_key}})

    async def create_invited_user(self, email: str):
        platform_user = PlatformUser(
            first_name="",
            last_name="",
            email=email,
            is_signed_up=False,
            has_visted_sheets=False,
        )
        await platform_user.insert()
        return platform_user

    async def _upgrade_invited_user(self, oauth_user: OAuthUser, id: PydanticObjectId):
        user = await self._build_user(oauth_user=oauth_user)
        to_update = {
            "updated_at": datetime.utcnow(),
            "is_signed_up": True,
        }
        to_update.update(
            user.dict(
                exclude={"id", "created_at", "email", "updated_at", "is_signed_up"}
            )
        )

        await PlatformUser.find_one(
            PlatformUser.id == id,
        ).update({"$set": to_update})

        return await PlatformUser.find_one(
            PlatformUser.id == id,
        )

    async def get_all_platform_users(self):
        return await PlatformUser.find().to_list()
