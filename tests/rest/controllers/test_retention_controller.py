import json
from unittest.mock import ANY

import pytest
from beanie import PydanticObjectId

from domain.common.date_models import DateFilter, DateFilterType, LastDateFilter
from domain.retention.models import EventSelection, Granularity
from tests.utils import filter_response


def test_create_retention(client_init, retention_data, retention_response):
    response = client_init.post("/retention", data=json.dumps(retention_data))
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(retention_response)


def test_get_retention(client_init, retention_service, retention_response):
    response = client_init.get("/retention/000000000000000000000006")
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(retention_response)

    retention_service.get_retention.assert_called_once_with(
        "000000000000000000000006",
    )


@pytest.mark.asyncio
async def test_update_retention(
    client_init,
    retention_data,
    datasource_service,
    retention_response,
    retention_service,
    mock_user_id,
):
    response = client_init.put(
        "/retention/000000000000000000000006", data=json.dumps(retention_data)
    )
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(retention_response)
    datasource_service.get_datasource.assert_called_with(
        "000000000000000000000004",
    )
    retention_service.build_retention.assert_called_with(
        **{
            "app_id": PydanticObjectId("000000000000000000000003"),
            "datasource_id": PydanticObjectId("000000000000000000000003"),
            "date_filter": DateFilter(
                filter=LastDateFilter(days=4), type=DateFilterType.LAST
            ),
            "goal_event": EventSelection(event="goal_event", filters=None),
            "granularity": Granularity.DAYS,
            "name": "test",
            "segment_filter": None,
            "start_event": EventSelection(event="start_event", filters=None),
            "user_id": "mock-user-id",
        }
    )

    update_retention_kwargs = retention_service.update_retention.call_args.kwargs
    retention_service.update_retention.assert_called_once()

    assert {
        "app_id": PydanticObjectId("00000000000000000000000d"),
        "created_at": ANY,
        "datasource_id": ANY,
        "date_filter": {"filter": {"days": 4}, "type": DateFilterType.LAST},
        "enabled": True,
        "goal_event": {"event": "goal_event", "filters": None},
        "granularity": Granularity.DAYS,
        "id": PydanticObjectId("000000000000000000000006"),
        "name": "name",
        "revision_id": None,
        "segment_filter": None,
        "start_event": {"event": "start_event", "filters": None},
        "updated_at": None,
        "user_id": PydanticObjectId("000000000000000000000005"),
    } == update_retention_kwargs["new_retention"].dict()

    assert "000000000000000000000006" == update_retention_kwargs["retention_id"]


def test_compute_transient_retention(
    client_init,
    retention_transient_data,
    transient_retention_response,
    retention_service,
):
    response = client_init.post(
        "/retention/transient",
        data=json.dumps(retention_transient_data),
    )
    assert response.status_code == 200
    assert response.json() == transient_retention_response

    retention_service.compute_retention.assert_called_with(
        **{
            "datasource_id": "000000000000000000000004",
            "date_filter": DateFilter(
                filter=LastDateFilter(days=4), type=DateFilterType.LAST
            ),
            "goal_event": EventSelection(event="goal_event", filters=None),
            "granularity": Granularity.DAYS,
            "segment_filter": None,
            "start_event": EventSelection(event="start_event", filters=None),
            "app_id": "000000000000000000000003",
        }
    )


def test_get_retention_list(client_init, retention_service):
    response = client_init.get("/retention?datasource_id=000000000000000000000004")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000006",
            "appId": "00000000000000000000000d",
            "createdAt": ANY,
            "datasourceId": "000000000000000000000004",
            "dateFilter": {"filter": {"days": 4}, "type": "last"},
            "enabled": True,
            "goalEvent": {"event": "goal_event", "filters": None},
            "granularity": "days",
            "name": "name",
            "revisionId": ANY,
            "segmentFilter": None,
            "startEvent": {"event": "start_event", "filters": None},
            "updatedAt": ANY,
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
        }
    ]
    retention_service.get_retentions_for_datasource_id.assert_called_once_with(
        **{"datasource_id": "000000000000000000000004"}
    )


def test_delete_retention(client_init, retention_service):
    response = client_init.delete(
        "/retention/00000000000000000000001b?datasource_id=00000000000000000000001b"
    )
    assert response.status_code == 200

    retention_service.delete_retention.assert_called_once_with(
        **{
            "retention_id": "00000000000000000000001b",
        }
    )


@pytest.mark.asyncio
async def test_get_saved_retention_for_app(client_init, retention_service):
    response = client_init.get("/retention?app_id=000000000000000000000008")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000006",
            "revisionId": None,
            "createdAt": ANY,
            "updatedAt": None,
            "datasourceId": "000000000000000000000004",
            "appId": "00000000000000000000000d",
            "userId": "000000000000000000000005",
            "name": "name",
            "startEvent": {"event": "start_event", "filters": None},
            "goalEvent": {"event": "goal_event", "filters": None},
            "dateFilter": {"filter": {"days": 4}, "type": "last"},
            "segmentFilter": None,
            "granularity": "days",
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
    retention_service.get_retentions_for_apps.assert_called_once_with(
        **{"app_ids": [PydanticObjectId("000000000000000000000004")]}
    )
