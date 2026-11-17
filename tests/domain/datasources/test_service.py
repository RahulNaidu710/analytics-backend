from collections import namedtuple
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from beanie import PydanticObjectId

from domain.apps.models import App
from domain.common.models import IntegrationProvider
from domain.datasources.models import DataSource, DataSourceVersion
from domain.datasources.service import DataSourceService


class TestDataSourceService:
    def setup_method(self):
        DataSource.get_settings = MagicMock()
        App.get_settings = MagicMock()
        self.clickhouse_role = MagicMock()
        self.service = DataSourceService(
            auth_service=MagicMock(), clickhouse_role=self.clickhouse_role
        )
        self.ds_id = "000000000000000000000003"
        FindMock = namedtuple("FindMock", ["to_list"])

        self.clickhouse_role.create_user = MagicMock()
        self.clickhouse_role.create_row_policy = AsyncMock()
        self.clickhouse_role.grant_select_permission_to_user = MagicMock()

        self.username = "test_user"
        self.password = "test_password"
        DataSource.find = MagicMock(
            return_value=FindMock(
                to_list=AsyncMock(),
            ),
        )

        self.app = App(
            id=PydanticObjectId("000000000000000000000004"),
            revision_id=None,
            created_at=datetime(2022, 11, 8, 7, 57, 35, 691000),
            updated_at=datetime(2022, 11, 8, 7, 57, 35, 691000),
            name="mixpanel1",
            user_id=PydanticObjectId("000000000000000000000005"),
            shared_with=set(),
            clickhouse_credential=None,
        )
        self.datasource = DataSource(
            integration_id="000000000000000000000003",
            app_id="000000000000000000000003",
            user_id="000000000000000000000003",
            provider=IntegrationProvider.PLATFORM,
            external_source_id="123",
            version=DataSourceVersion.DEFAULT,
        )
        self.service.get_datasources_for_app_id = AsyncMock(
            return_value=[self.datasource]
        )
        self.service.create_user_policy_for_all_datasources = AsyncMock()

        DataSource.provider = MagicMock(return_value=IntegrationProvider.PLATFORM)
        DataSource.id = MagicMock(return_value=self.ds_id)
        DataSource.enabled = MagicMock(return_value=True)

    @pytest.mark.asyncio
    async def test_get_datasources_for_provider(self):
        await self.service.get_datasources_for_provider(
            provider=IntegrationProvider.PLATFORM
        )
        DataSource.find.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_row_policy_for_username(self):
        await self.service.create_row_policy_for_username(
            username=self.username, datasource_id=self.ds_id, app_id=self.app.id
        )
        self.clickhouse_role.create_row_policy.assert_called_once_with(
            datasource_id="000000000000000000000003",
            username="test_user",
            app_id=PydanticObjectId("000000000000000000000004"),
        )

    @pytest.mark.asyncio
    async def test_create_row_policy_for_datasources_by_app(self):
        await self.service.create_row_policy_for_datasources_by_app(
            app=self.app, username=self.username
        )
        self.service.get_datasources_for_app_id.assert_called_once_with(self.app.id)
        self.service.create_user_policy_for_all_datasources.assert_called_once_with(
            datasources=[self.datasource], username=self.username
        )
