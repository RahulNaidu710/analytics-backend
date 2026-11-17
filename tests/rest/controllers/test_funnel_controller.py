import json
from unittest.mock import ANY

import pytest
from beanie import PydanticObjectId

from domain.funnels.models import FunnelStep
from tests.utils import filter_response


def test_create_funnel(client_init, funnel_data, funnel_response):
    response = client_init.post("/funnels", data=json.dumps(funnel_data))
    assert response.status_code == 200
    assert response.json().keys() == funnel_response.keys()
    assert filter_response(response.json()) == filter_response(funnel_response)


def test_compute_transient_funnel(
    client_init, funnel_data, computed_transient_funnel_response
):
    response = client_init.post("/funnels/transient", data=json.dumps(funnel_data))
    assert response.status_code == 200
    assert response.json() == computed_transient_funnel_response


def test_get_saved_funnel(client_init, funnel_service, funnel_response):
    response = client_init.get("/funnels/000000000000000000000006")
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(funnel_response)

    funnel_service.get_funnel.assert_called_once_with(
        "000000000000000000000006",
    )


@pytest.mark.asyncio
async def test_update_funnel(
    client_init,
    funnel_data,
    datasource_service,
    funnel_response,
    funnel_service,
    mock_user_id,
    notification_service,
):
    response = client_init.put(
        "/funnels/000000000000000000000006", data=json.dumps(funnel_data)
    )
    assert response.status_code == 200
    assert filter_response(response.json()) == filter_response(funnel_response)
    datasource_service.get_datasource.assert_called_with(
        "000000000000000000000003",
    )
    funnel_service.build_funnel.assert_called_with(
        PydanticObjectId(funnel_data["datasourceId"]),
        PydanticObjectId(funnel_data["appId"]),
        mock_user_id,
        funnel_data["name"],
        [
            FunnelStep(
                event="Login",
                filters=None,
            ),
            FunnelStep(event="Chapter_Click", filters=None),
            FunnelStep(
                event="Topic_Click",
                filters=None,
            ),
        ],
        funnel_data["randomSequence"],
        None,
        None,
        None,
    )

    update_funnel_kwargs = funnel_service.update_funnel.call_args.kwargs
    funnel_service.update_funnel.assert_called_once()

    assert {
        "created_at": ANY,
        "datasource_id": PydanticObjectId("000000000000000000000004"),
        "app_id": PydanticObjectId("00000000000000000000000d"),
        "id": PydanticObjectId("000000000000000000000006"),
        "name": "name",
        "random_sequence": False,
        "revision_id": ANY,
        "steps": [
            {
                "event": "Login",
                "filters": None,
            },
            {"event": "Chapter_Click", "filters": None},
            {
                "event": "Topic_Click",
                "filters": None,
            },
        ],
        "updated_at": None,
        "user_id": PydanticObjectId("000000000000000000000005"),
        "date_filter": None,
        "enabled": True,
        "conversion_window": None,
        "segment_filter": None,
    } == update_funnel_kwargs["new_funnel"].dict()

    assert "000000000000000000000006" == update_funnel_kwargs["funnel_id"]

    notification_service.fetch_and_delete_notification.assert_called_once_with(
        **{
            "reference_id": "000000000000000000000006",
            "datasource_id": "000000000000000000000003",
        }
    )


def test_get_funnel_trends(client_init, funnel_trend_response, funnel_service):
    response = client_init.get("/funnels/000000000000000000000006/trends")
    assert response.status_code == 200
    assert response.json() == funnel_trend_response

    funnel_service.get_funnel_trends.assert_called_once_with(
        **{
            "datasource_id": "000000000000000000000004",
            "app_id": "00000000000000000000000d",
            "steps": [
                FunnelStep(
                    event="Login",
                    filters=None,
                ),
                FunnelStep(event="Chapter_Click", filters=None),
                FunnelStep(
                    event="Topic_Click",
                    filters=None,
                ),
            ],
            "date_filter": None,
            "conversion_window": None,
            "random_sequence": False,
            "segment_filter": None,
        }
    )


def test_get_transient_funnel_trends(
    client_init, funnel_data, funnel_trend_response, funnel_service
):
    response = client_init.post(
        "/funnels/trends/transient", data=json.dumps(funnel_data)
    )
    assert response.status_code == 200
    assert response.json() == funnel_trend_response

    funnel_service.get_funnel_trends.assert_called_with(
        **{
            "datasource_id": "000000000000000000000003",
            "app_id": "000000000000000000000003",
            "steps": [
                FunnelStep(
                    event="Login",
                    filters=None,
                ),
                FunnelStep(event="Chapter_Click", filters=None),
                FunnelStep(
                    event="Topic_Click",
                    filters=None,
                ),
            ],
            "date_filter": None,
            "conversion_window": None,
            "random_sequence": False,
            "segment_filter": None,
        }
    )


def test_transient_funnel_analytics(
    client_init, funnel_conversion_request, funnel_user_conversion_response
):
    response = client_init.post(
        "/funnels/analytics/transient", data=json.dumps(funnel_conversion_request)
    )

    assert response.status_code == 200
    assert response.json() == funnel_user_conversion_response


def test_get_funnels(client_init, funnel_service):
    response = client_init.get("/funnels?datasource_id=000000000000000000000004")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000006",
            "appId": "00000000000000000000000d",
            "createdAt": ANY,
            "datasourceId": "000000000000000000000004",
            "name": "name",
            "randomSequence": False,
            "revisionId": ANY,
            "steps": [
                {"event": "Login", "filters": None},
                {"event": "Chapter_Click", "filters": None},
                {"event": "Topic_Click", "filters": None},
            ],
            "updatedAt": ANY,
            "user": {
                "id": "000000000000000000000006",
                "email": "user011@example.com",
                "firstName": "Test",
                "lastName": "User",
                "picture": "https://images.example.com/avatar-1.png",
                "slackChannel": "#alerts",
                "hasVisitedSheets": False,
            },
            "userId": "000000000000000000000005",
            "dateFilter": None,
            "enabled": True,
            "conversionWindow": None,
            "segmentFilter": None,
        }
    ]
    funnel_service.get_funnels_for_datasource_id.assert_called_once_with(
        **{"datasource_id": "000000000000000000000004"}
    )


def test_delete_funnel(client_init, funnel_service, notification_service):
    response = client_init.delete(
        "/funnels/00000000000000000000001b?datasource_id=00000000000000000000001b"
    )
    assert response.status_code == 200

    funnel_service.delete_funnel.assert_called_once_with(
        **{
            "funnel_id": "00000000000000000000001b",
        }
    )

    notification_service.fetch_and_delete_notification.assert_called_with(
        **{
            "reference_id": "00000000000000000000001b",
            "datasource_id": "00000000000000000000001b",
        }
    )


@pytest.mark.asyncio
async def test_get_saved_funnels_for_app(client_init, funnel_service):
    response = client_init.get("/funnels?app_id=000000000000000000000008")

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
            "steps": [
                {"event": "Login", "filters": None},
                {"event": "Chapter_Click", "filters": None},
                {"event": "Topic_Click", "filters": None},
            ],
            "randomSequence": False,
            "dateFilter": None,
            "conversionWindow": None,
            "segmentFilter": None,
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
    funnel_service.get_funnels_for_apps.assert_called_once_with(
        **{"app_ids": [PydanticObjectId("000000000000000000000004")]}
    )
