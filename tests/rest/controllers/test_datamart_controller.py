import json
from datetime import datetime
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from beanie import PydanticObjectId

from domain.apps.models import ClickHouseCredential
from domain.datamart.models import DataMart
from domain.datamart_actions.models import DatamartAction
from domain.spreadsheets.models import DatabaseClient
from tests.utils import filter_response


def test_save_datamart_table(
    client_init, datamart_service, datamart_data, datamart_response
):
    response = client_init.post("/datamart", data=json.dumps(datamart_data))
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(datamart_response)
    datamart_service.build_datamart_table.assert_called_with(
        **{
            "app_id": PydanticObjectId("000000000000000000000003"),
            "datasource_id": PydanticObjectId("000000000000000000000004"),
            "name": "test-table",
            "query": "select event_name, user_id from events",
            "user_id": "mock-user-id",
        }
    )
    datamart_service.save_datamart.assert_called_once()


def test_get_datamart(client_init, datamart_service, datamart_response):
    response = client_init.get("/datamart/000000000000000000000006")
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(datamart_response)

    datamart_service.get_datamart_table.assert_called_once_with(
        **{"id": "000000000000000000000006"}
    )


@pytest.mark.asyncio
async def test_update_datamart(
    client_init,
    datamart_data,
    app_service,
    datasource_service,
    datamart_response,
    datamart_service,
    mock_user_id,
):
    response = client_init.put(
        "/datamart/000000000000000000000006", data=json.dumps(datamart_data)
    )
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(datamart_response)
    datasource_service.get_datasource.assert_called_with(
        "000000000000000000000004",
    )
    datamart_service.build_datamart_table.assert_called_with(
        **{
            "app_id": PydanticObjectId("000000000000000000000003"),
            "datasource_id": PydanticObjectId("000000000000000000000004"),
            "name": "test-table",
            "query": "select event_name, user_id from events",
            "user_id": "mock-user-id",
        }
    )

    update_datamart_kwargs = datamart_service.update_datamart_table.call_args.kwargs
    datamart_service.update_datamart_table.assert_called_once()

    assert {
        "app_id": PydanticObjectId("00000000000000000000000d"),
        "created_at": ANY,
        "datasource_id": PydanticObjectId("000000000000000000000004"),
        "enabled": True,
        "id": PydanticObjectId("000000000000000000000006"),
        "last_refreshed": datetime(2022, 11, 24, 0, 0),
        "name": "name",
        "table_name": "dUKQaHtqxM",
        "query": "select event_name, user_id from events",
        "revision_id": None,
        "updated_at": None,
        "user_id": PydanticObjectId("000000000000000000000005"),
    } == update_datamart_kwargs["new_table"].dict()

    assert "000000000000000000000006" == update_datamart_kwargs["id"]


def test_compute_transient_datamart(
    client_init,
    datamart_transient_data,
    transient_datamart_response,
    datamart_service,
    spreadsheets_service,
):
    response = client_init.post(
        "/datamart/transient",
        data=json.dumps(datamart_transient_data),
    )
    assert response.status_code == 200
    assert response.json() == transient_datamart_response

    spreadsheets_service.get_transient_spreadsheets.assert_called_once_with(
        **{
            "query": "select event_name, user_id from events",
            "credential": ClickHouseCredential(
                username="test_username",
                password="test_password",
                databasename="test_database",
            ),
            "client": DatabaseClient.CLICKHOUSE,
            "query_id": None,
            "app_id": PydanticObjectId("000000000000000000000003"),
            "skip_query_limit": False,
        }
    )


def test_get_datamart_list(client_init, datamart_service):
    response = client_init.get("/datamart?datasource_id=000000000000000000000004")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000006",
            "appId": "00000000000000000000000d",
            "createdAt": ANY,
            "datasourceId": "000000000000000000000004",
            "enabled": True,
            "lastRefreshed": "2022-11-24T00:00:00",
            "name": "name",
            "tableName": "dUKQaHtqxM",
            "query": "select event_name, user_id from events",
            "revisionId": None,
            "updatedAt": None,
            "user": {
                "email": "user011@example.com",
                "firstName": "Test",
                "id": "000000000000000000000006",
                "lastName": "User",
                "picture": "https://images.example.com/avatar-1.png",
                "slackChannel": "#alerts",
                "hasVisitedSheets": False,
            },
            "userId": "000000000000000000000005",
            "actions": [
                {
                    "_id": "000000000000000000000006",
                    "revisionId": None,
                    "createdAt": ANY,
                    "updatedAt": None,
                    "datasourceId": "000000000000000000000004",
                    "appId": "00000000000000000000000d",
                    "userId": "00000000000000000000000f",
                    "datamartId": "000000000000000000000010",
                    "type": "google_sheet",
                    "schedule": {
                        "time": None,
                        "period": None,
                        "date": None,
                        "day": None,
                        "frequency": "hourly",
                        "datamartId": None,
                    },
                    "meta": {
                        "spreadsheet": {"id": "1qu87sylkjuesopp98", "name": "Test"},
                        "sheet": "Sheet1",
                    },
                    "enabled": True,
                }
            ],
        }
    ]
    datamart_service.get_datamart_tables_for_app_id.assert_called_once_with(
        **{"app_id": PydanticObjectId("000000000000000000000003")}
    )


def test_delete_datamart(
    client_init, datamart_service, app_service, datamart_action_service
):
    response = client_init.delete("/datamart/00000000000000000000001b")
    assert response.status_code == 200

    datamart_service.delete_datamart_table.assert_called_once_with(
        **{
            "clickhouse_credential": ClickHouseCredential(
                username="test_username",
                password="test_password",
                databasename="test_database",
            ),
            "datamart_id": "00000000000000000000001b",
            "table_name": "dUKQaHtqxM",
        },
        app_id="000000000000000000000004"
    )

    datamart_service.get_datamart_table.assert_called_with(
        **{"id": "00000000000000000000001b"}
    )
    app_service.get_app.assert_called_with(**{"id": "00000000000000000000000d"})
    datamart_action_service.delete_datamart_actions_for_datamart.assert_called_with(
        datamart_id="00000000000000000000001b"
    )
