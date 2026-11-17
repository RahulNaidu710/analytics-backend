import datetime
import json
from unittest.mock import ANY, AsyncMock

import pytest
from beanie import PydanticObjectId

from domain.apps.models import App, ClickHouseCredential
from domain.spreadsheets.models import (
    ColumnType,
    DatabaseClient,
    SpreadSheetColumn,
    SpreadsheetType,
)


@pytest.mark.asyncio
async def test_compute_transient_spreadsheets_with_credentials(
    client_init,
    spreadsheets_service,
    datasource_service,
    transient_spreadsheet_data,
    app_service,
):
    response = client_init.post(
        "/workbooks/spreadsheets/transient", data=json.dumps(transient_spreadsheet_data)
    )
    assert response.status_code == 200
    assert response.json() == {
        "headers": [SpreadSheetColumn(name="event_name", type=ColumnType.QUERY_HEADER)],
        "data": [
            {"event_name": "test_event_1"},
            {"event_name": "test_event_2"},
            {"event_name": "test_event_3"},
            {"event_name": "test_event_4"},
            {"event_name": "test_event_5"},
        ],
        "sql": "select * from events",
    }
    spreadsheets_service.get_transient_spreadsheets.assert_called_once_with(
        **{
            "query": "SELECT  event_name FROM  events WHERE timestamp>=toDate(2023-02-11)",
            "credential": ClickHouseCredential(
                username="test_username",
                password="test_password",
                databasename="test_database",
            ),
            "client": DatabaseClient.CLICKHOUSE,
            "query_id": None,
            "app_id": "000000000000000000000003",
            "skip_query_limit": False,
        }
    )
    datasource_service.get_datasource.assert_called_with("23412414123123")
    datasource_service.create_row_policy_for_datasources_by_app.assert_not_called()

    app_service.get_app.assert_called_once_with(
        id=PydanticObjectId("000000000000000000000003")
    )
    app_service.create_clickhouse_user.assert_not_called()


@pytest.mark.asyncio
async def test_compute_transient_spreadsheets(
    client_init,
    spreadsheets_service,
    datasource_service,
    transient_spreadsheet_data,
    app_service,
):
    app_service.get_app = AsyncMock(
        return_value=App(
            id=PydanticObjectId("000000000000000000000004"),
            revision_id=None,
            created_at=datetime.datetime(2022, 11, 8, 7, 57, 35, 691000),
            updated_at=datetime.datetime(2022, 11, 8, 7, 57, 35, 691000),
            name="mixpanel1",
            user_id=PydanticObjectId("000000000000000000000005"),
            shared_with=set(),
            clickhouse_credential=None,
        )
    )
    response = client_init.post(
        "/workbooks/spreadsheets/transient", data=json.dumps(transient_spreadsheet_data)
    )
    assert response.status_code == 200
    assert response.json() == {
        "headers": [SpreadSheetColumn(name="event_name", type=ColumnType.QUERY_HEADER)],
        "data": [
            {"event_name": "test_event_1"},
            {"event_name": "test_event_2"},
            {"event_name": "test_event_3"},
            {"event_name": "test_event_4"},
            {"event_name": "test_event_5"},
        ],
        "sql": "select * from events",
    }
    spreadsheets_service.get_transient_spreadsheets.assert_called_with(
        **{
            "query": "SELECT  event_name FROM  events WHERE timestamp>=toDate(2023-02-11)",
            "credential": ClickHouseCredential(
                username="test_username",
                password="test_password",
                databasename="test_database",
            ),
            "client": DatabaseClient.CLICKHOUSE,
            "query_id": None,
            "app_id": "000000000000000000000003",
            "skip_query_limit": False,
        }
    )
    datasource_service.get_datasource.assert_called_with("23412414123123")
    datasource_service.create_row_policy_for_datasources_by_app.assert_called_with(
        **{
            "app": App(
                id=PydanticObjectId("000000000000000000000004"),
                revision_id=None,
                created_at=datetime.datetime(2022, 11, 8, 7, 57, 35, 691000),
                updated_at=datetime.datetime(2022, 11, 8, 7, 57, 35, 691000),
                name="mixpanel1",
                user_id=PydanticObjectId("000000000000000000000005"),
                shared_with=set(),
                enabled=True,
                clickhouse_credential=None,
            ),
            "username": "test_username",
        }
    )

    app_service.get_app.assert_called_with(
        id=PydanticObjectId("000000000000000000000003")
    )
    app_service.create_clickhouse_user.assert_called_once_with(
        **{
            "id": PydanticObjectId("000000000000000000000004"),
            "app_name": "mixpanel1",
        }
    )


@pytest.mark.asyncio
async def test_get_saved_workbooks(client_init, spreadsheets_service):
    response = client_init.get("/workbooks?datasource_id=000000000000000000000008")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000016",
            "revisionId": None,
            "createdAt": ANY,
            "updatedAt": None,
            "datasourceId": "000000000000000000000008",
            "appId": "00000000000000000000000a",
            "userId": "000000000000000000000009",
            "name": "Test Workbook",
            "spreadsheets": [
                {
                    "name": "Sheet1",
                    "headers": [{"name": "event_name", "type": "QUERY_HEADER"}],
                    "is_sql": True,
                    "query": "SELECT  event_name FROM  events",
                    "subHeaders": None,
                    "edit_mode": True,
                    "sheet_type": SpreadsheetType.SIMPLE_SHEET,
                    "meta": {"dsId": "", "selectedColumns": []},
                    "ai_query": None,
                    "charts": [],
                    "column_format": None,
                }
            ],
            "enabled": True,
            "user": {
                "id": "000000000000000000000006",
                "firstName": "Test",
                "lastName": "User",
                "email": "user011@example.com",
                "picture": "https://images.example.com/avatar-1.png",
                "slackChannel": "#alerts",
                "hasVisitedSheets": False,
            },
        }
    ]
    spreadsheets_service.get_workbooks_for_datasource_id.assert_called_once_with(
        **{"datasource_id": "000000000000000000000008"}
    )


@pytest.mark.asyncio
async def test_get_saved_workbooks_for_app(client_init, spreadsheets_service):
    response = client_init.get("/workbooks?app_id=000000000000000000000008")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000016",
            "revisionId": None,
            "createdAt": ANY,
            "updatedAt": None,
            "datasourceId": "000000000000000000000008",
            "appId": "00000000000000000000000a",
            "userId": "000000000000000000000009",
            "name": "Test Workbook",
            "spreadsheets": [
                {
                    "name": "Sheet1",
                    "headers": [{"name": "event_name", "type": "QUERY_HEADER"}],
                    "is_sql": True,
                    "query": "SELECT  event_name FROM  events",
                    "subHeaders": None,
                    "edit_mode": True,
                    "sheet_type": SpreadsheetType.SIMPLE_SHEET,
                    "meta": {"dsId": "", "selectedColumns": []},
                    "ai_query": None,
                    "charts": [],
                    "column_format": None,
                }
            ],
            "enabled": True,
            "user": {
                "id": "000000000000000000000006",
                "firstName": "Test",
                "lastName": "User",
                "email": "user011@example.com",
                "picture": "https://images.example.com/avatar-1.png",
                "slackChannel": "#alerts",
                "hasVisitedSheets": False,
            },
        }
    ]
    spreadsheets_service.get_workbooks_for_app.assert_called_once()


@pytest.mark.asyncio
async def test_get_saved_workbooks_by_user_id(client_init, spreadsheets_service):
    response = client_init.get("/workbooks")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000016",
            "revisionId": None,
            "createdAt": ANY,
            "updatedAt": None,
            "datasourceId": "000000000000000000000008",
            "appId": "00000000000000000000000a",
            "userId": "000000000000000000000009",
            "name": "Test Workbook",
            "spreadsheets": [
                {
                    "name": "Sheet1",
                    "headers": [{"name": "event_name", "type": "QUERY_HEADER"}],
                    "is_sql": True,
                    "subHeaders": None,
                    "query": "SELECT  event_name FROM  events",
                    "edit_mode": True,
                    "sheet_type": SpreadsheetType.SIMPLE_SHEET,
                    "meta": {"dsId": "", "selectedColumns": []},
                    "ai_query": None,
                    "charts": [],
                    "column_format": None,
                }
            ],
            "enabled": True,
            "user": {
                "id": "000000000000000000000006",
                "firstName": "Test",
                "lastName": "User",
                "email": "user011@example.com",
                "picture": "https://images.example.com/avatar-1.png",
                "slackChannel": "#alerts",
                "hasVisitedSheets": False,
            },
        }
    ]
    spreadsheets_service.get_workbooks_for_user_id.assert_called_once()


@pytest.mark.asyncio
async def test_get_saved_workbook_by_id(client_init, spreadsheets_service):
    response = client_init.get("/workbooks/000000000000000000000006")
    assert response.status_code == 200
    assert response.json() == {
        "_id": "000000000000000000000016",
        "appId": "00000000000000000000000a",
        "createdAt": ANY,
        "datasourceId": "000000000000000000000008",
        "enabled": True,
        "name": "Test Workbook",
        "revisionId": None,
        "spreadsheets": [
            {
                "headers": [{"name": "event_name", "type": "QUERY_HEADER"}],
                "is_sql": True,
                "name": "Sheet1",
                "subHeaders": None,
                "query": "SELECT  event_name FROM  events",
                "edit_mode": True,
                "sheet_type": SpreadsheetType.SIMPLE_SHEET,
                "meta": {"dsId": "", "selectedColumns": []},
                "ai_query": None,
                "charts": [],
                "column_format": None,
            }
        ],
        "updatedAt": None,
        "userId": "000000000000000000000009",
    }

    spreadsheets_service.get_workbook_by_id.assert_called_once_with(
        **{"workbook_id": "000000000000000000000006"},
    )


@pytest.mark.asyncio
async def test_create_workbook(client_init, workbook_data):
    response = client_init.post("/workbooks", data=json.dumps(workbook_data))
    assert response.status_code == 200
    assert response.json() == {
        "_id": "000000000000000000000016",
        "revisionId": None,
        "createdAt": ANY,
        "updatedAt": None,
        "datasourceId": "000000000000000000000008",
        "appId": "00000000000000000000000a",
        "userId": "000000000000000000000009",
        "name": "Test Workbook",
        "spreadsheets": [
            {
                "name": "Sheet1",
                "headers": [{"name": "event_name", "type": "QUERY_HEADER"}],
                "is_sql": True,
                "subHeaders": None,
                "query": "SELECT  event_name FROM  events",
                "edit_mode": True,
                "sheet_type": SpreadsheetType.SIMPLE_SHEET,
                "meta": {"dsId": "", "selectedColumns": []},
                "ai_query": None,
                "charts": [],
                "column_format": None,
            }
        ],
        "enabled": True,
    }


@pytest.mark.asyncio
async def test_update_workbook(client_init, workbook_data, spreadsheets_service):
    response = client_init.put(
        "/workbooks/000000000000000000000006", data=json.dumps(workbook_data)
    )
    assert response.status_code == 200
    spreadsheets_service.update_workbook.assert_called_once()

    assert {
        "id": PydanticObjectId("000000000000000000000016"),
        "revision_id": None,
        "created_at": ANY,
        "updated_at": None,
        "datasource_id": PydanticObjectId("000000000000000000000008"),
        "app_id": PydanticObjectId("00000000000000000000000a"),
        "user_id": PydanticObjectId("000000000000000000000009"),
        "name": "Test Workbook",
        "spreadsheets": [
            {
                "name": "Sheet1",
                "headers": [{"name": "event_name", "type": ColumnType.QUERY_HEADER}],
                "is_sql": True,
                "subHeaders": None,
                "query": "SELECT  event_name FROM  events",
                "edit_mode": True,
                "sheet_type": SpreadsheetType.SIMPLE_SHEET,
                "meta": {"dsId": "", "selectedColumns": []},
                "ai_query": None,
                "column_format": None,
                "charts": [],
            }
        ],
        "enabled": True,
    } == spreadsheets_service.update_workbook.call_args.kwargs["workbook"].dict()


@pytest.mark.asyncio
async def test_delete_workbook(client_init, spreadsheets_service):
    response = client_init.delete("/workbooks/00000000000000000000001b")
    assert response.status_code == 200

    spreadsheets_service.delete_workbook.assert_called_once_with(
        **{
            "workbook_id": "00000000000000000000001b",
        }
    )


@pytest.mark.asyncio
async def test_vlookup(client_init, spreadsheets_service):
    response = client_init.post(
        "/workbooks/vlookup",
        json={
            "datasourceId": "00000000000000000000001c",
            "searchQuery": "select event_name, user_id from default.events where datasource_id = '00000000000000000000001c'",
            "lookupQuery": "select event_name, user_id from default.events where datasource_id = '00000000000000000000001c'",
            "searchKeyColumn": "event_name",
            "lookupColumn": "user_id",
            "lookupIndexColumn": "event_name",
        },
    )
    assert response.status_code == 200
    assert response.json() == ["test1", "test2"]
    spreadsheets_service.compute_vlookup.assert_called_once_with(
        app_id="000000000000000000000003",
        **{
            "lookup_column": "user_id",
            "lookup_index_column": "event_name",
            "search_column": "event_name",
            "lookup_query": "select event_name, user_id from default.events where "
            "datasource_id = '00000000000000000000001c'",
            "search_query": "select event_name, user_id from default.events where "
            "datasource_id = '00000000000000000000001c'",
        },
    )
