from collections import namedtuple
from unittest.mock import AsyncMock, MagicMock
from beanie import PydanticObjectId

import pytest

from domain.platform_users.models import PlatformUser
from domain.platform_users.service import PlatformUserService
from utils.errors import BusinessError


class TestUserService:
    def setup_method(self):
        self.service = PlatformUserService()
        self.first_name = "ExamplePerson001"
        self.last_name = "ExamplePerson002"
        self.email = "user014@example.com"
        self.password = "argon2"
        self.new_password = "argon3"
        self.api_key = "TEST_CREDENTIAL_009"
        self.user_id = "000000000000000000000003"
        self.ds_id = "000000000000000000000003"
        PlatformUser.id = MagicMock(return_value=PydanticObjectId(self.ds_id))
        PlatformUser.api_key = MagicMock(return_value=self.api_key)
        PlatformUser.get_settings = MagicMock()
        PlatformUser.insert = AsyncMock()
        FindMock = namedtuple("FindMock", ["to_list"])
        PlatformUser.find = MagicMock(
            return_value=FindMock(
                to_list=AsyncMock(),
            ),
        )
        PlatformUser.find_one = AsyncMock()

    @pytest.mark.asyncio
    async def test_create_user_with_password_new_user(self):
        user = await self.service.create_user_with_password(
            self.first_name, self.last_name, self.email, self.password
        )

        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.email == self.email
        assert user.password == user.password
        user.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_with_password_new_user(self):
        existing_user = MagicMock()
        PlatformUser.email = MagicMock()
        PlatformUser.find_one = AsyncMock(return_value=existing_user)
        with pytest.raises(BusinessError, match="User already exists with this email"):
            user = await self.service.create_user_with_password(
                self.first_name, self.last_name, self.email, self.password
            )

    @pytest.mark.asyncio
    async def test_get_user_by_api_key(self):
        await self.service.get_user_by_api_key(
            api_key=self.api_key,
        )
        PlatformUser.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_api_key(self):
        FindOneMock = namedtuple("FindOneMock", ["update"])
        self.update_mock = AsyncMock()
        PlatformUser.find_one = MagicMock(
            return_value=FindOneMock(update=self.update_mock)
        )
        await self.service.update_api_key(
            user_id=self.user_id,
            api_key=self.api_key,
        )
        self.update_mock.assert_called_once_with(
            {"$set": {"api_key": "TEST_CREDENTIAL_009"}}
        )
