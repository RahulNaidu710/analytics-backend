import json
from unittest.mock import ANY

import pytest
from beanie import PydanticObjectId

from domain.datamart_actions.models import (
    ActionType,
    Frequency,
    GoogleSheetMeta,
    Schedule,
    Spreadsheet,
)
from tests.utils import filter_response


def test_save_datamart_action(
    client_init, datamart_action_service, datamart_action_data, datamart_action_response
):
    response = client_init.post(
        "/datamart_actions", data=json.dumps(datamart_action_data)
    )
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(datamart_action_response)
    datamart_action_service.save_datamart_action.assert_called_once()


def test_get_datamart_action(
    client_init, datamart_action_service, datamart_action_response
):
    response = client_init.get("/datamart_actions/000000000000000000000006")
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(datamart_action_response)

    datamart_action_service.get_datamart_action.assert_called_once_with(
        **{"id": "000000000000000000000006"}
    )


@pytest.mark.asyncio
async def test_update_datamart_action(
    client_init,
    datamart_action_data,
    datamart_action_response,
    datamart_action_service,
):
    response = client_init.put(
        "/datamart_actions/000000000000000000000006",
        data=json.dumps(datamart_action_data),
    )
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(datamart_action_response)
    datamart_action_service.build_datamart_action.assert_called_with(
        datasource_id=PydanticObjectId("000000000000000000000004"),
        datamart_id=PydanticObjectId("000000000000000000000006"),
        app_id=PydanticObjectId("00000000000000000000000d"),
        user_id="mock-user-id",
        schedule=Schedule(
            time=None, period=None, date=None, day=None, frequency=Frequency.HOURLY, datamartId=None
        ),
        type=ActionType.GOOGLE_SHEET,
        meta=GoogleSheetMeta(
            spreadsheet=Spreadsheet(id="1qu87sylkjuesopp98", name="Test"),
            sheet="Sheet1",
        ),
    )

    update_datamart_kwargs = (
        datamart_action_service.update_datamart_action.call_args.kwargs
    )
    datamart_action_service.update_datamart_action.assert_called_once()

    assert {
        "id": PydanticObjectId("000000000000000000000006"),
        "revision_id": None,
        "created_at": ANY,
        "updated_at": None,
        "datasource_id": PydanticObjectId("000000000000000000000004"),
        "app_id": PydanticObjectId("00000000000000000000000d"),
        "user_id": PydanticObjectId("00000000000000000000000f"),
        "datamart_id": PydanticObjectId("000000000000000000000010"),
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
    } == update_datamart_kwargs["action"].dict()
    assert "000000000000000000000006" == update_datamart_kwargs["id"]


def test_delete_datamart_action(
    client_init,
    datamart_action_service,
):
    response = client_init.delete("/datamart_actions/00000000000000000000001b")
    assert response.status_code == 200

    datamart_action_service.delete_datamart_action.assert_called_once_with(
        **{"id": "00000000000000000000001b"}
    )


def test_get_spreadsheets(
    client_init,
    datamart_action_service,
):
    response = client_init.get("/datamart_actions/google/spreadsheets")
    assert response.status_code == 200
    assert response.json() == [
        {"id": "1qFp3w6nKRhvVc", "name": "Test"},
        {"id": "1n0-0y3hrr6B16oicXjw0Mg", "name": "Example Report"},
        {"id": "1abavuF9ocO4JU1C_01gBub", "name": "Testing 1"},
    ]
    datamart_action_service.get_google_spreadsheets.assert_called_once_with(
        **{"refresh_token": ANY}
    )


def test_get_sheet_names(
    client_init,
    datamart_action_service,
):
    response = client_init.get(
        "/datamart_actions/google/sheets/00000000000000000000001b"
    )
    assert response.status_code == 200
    assert response.json() == [
        "Sheet1",
        "Sheet2",
        "Sheet3",
    ]
    datamart_action_service.get_sheet_names.assert_called_once_with(
        **{"refresh_token": ANY, "spreadsheet_id": "00000000000000000000001b"}
    )
