import json
from unittest.mock import ANY

from beanie import PydanticObjectId
import pytest

from domain.notifications.models import (
    NotificationType,
    NotificationMetric,
    NotificationFrequency,
    NotificationChannel,
    NotificationVariant,
)
from tests.utils import filter_response


def test_get_notification_by_reference(
    client_init, notification_service, notification_response
):
    response = client_init.get(
        "/notifications?reference=/p/partner/job&datasource_id=000000000000000000000004"
    )
    assert response.status_code == 200
    assert response.json() == notification_response

    notification_service.get_notification_by_reference.assert_called_once_with(
        **{"datasource_id": "000000000000000000000004", "reference": "/p/partner/job"}
    )


def test_add_notification(
    client_init, notification_data, notification_service, notification_response
):
    response = client_init.post("/notifications", data=json.dumps(notification_data))
    assert response.status_code == 200
    assert response.json().keys() == notification_response.keys()
    assert filter_response(response.json()) == filter_response(notification_response)
    notification_service.build_notification.assert_called()
    notification_service.add_notification.assert_called_once()
    assert notification_service.build_notification.call_args.kwargs == {
        "absoluteThresholdActive": False,
        "absoluteThresholdValues": None,
        "appId": PydanticObjectId("000000000000000000000003"),
        "platformManaged": True,
        "datasourceId": PydanticObjectId("000000000000000000000003"),
        "formula": "",
        "frequency": NotificationFrequency.DAILY,
        "metric": NotificationMetric.HITS,
        "multiNode": True,
        "name": "name",
        "notificationActive": False,
        "notificationType": {NotificationType.UPDATE},
        "pctThresholdActive": False,
        "pctThresholdValues": None,
        "preferredChannels": [NotificationChannel.SLACK],
        "preferredHourGMT": 5,
        "userId": ANY,
        "variableMap": {},
        "reference": "/p/partner/job",
        "variant": NotificationVariant.NODE,
    }
    assert notification_service.add_notification.call_args.kwargs[
        "notification"
    ].dict() == {
        "absolute_threshold_active": False,
        "absolute_threshold_values": None,
        "app_id": PydanticObjectId("000000000000000000000004"),
        "platform_managed": True,
        "created_at": ANY,
        "datasource_id": PydanticObjectId("000000000000000000000004"),
        "formula": "",
        "frequency": NotificationFrequency.DAILY,
        "id": PydanticObjectId("000000000000000000000006"),
        "metric": NotificationMetric.HITS,
        "multi_node": True,
        "name": "name",
        "notification_active": False,
        "notification_type": {NotificationType.UPDATE},
        "pct_threshold_active": False,
        "pct_threshold_values": None,
        "preferred_channels": [NotificationChannel.SLACK],
        "preferred_hour_gmt": 5,
        "revision_id": ANY,
        "updated_at": None,
        "user_id": PydanticObjectId("000000000000000000000005"),
        "variable_map": {},
        "reference": "/p/partner/job",
        "variant": NotificationVariant.NODE,
        "enabled": True,
    }


def test_update_notification(
    client_init, notification_data, notification_service, notification_response
):
    response = client_init.put(
        "/notifications/000000000000000000000006", data=json.dumps(notification_data)
    )
    assert response.status_code == 200
    assert response.json().keys() == notification_response.keys()
    assert filter_response(response.json()) == filter_response(notification_response)
    notification_service.build_notification.assert_called()
    notification_service.update_notification.assert_called_once()
    assert notification_service.build_notification.call_args.kwargs == {
        "absoluteThresholdActive": False,
        "absoluteThresholdValues": None,
        "appId": PydanticObjectId("000000000000000000000003"),
        "platformManaged": True,
        "metric": "hits",
        "multiNode": True,
        "datasourceId": PydanticObjectId("000000000000000000000003"),
        "formula": "",
        "frequency": NotificationFrequency.DAILY,
        "name": "name",
        "notificationActive": False,
        "notificationType": {NotificationType.UPDATE},
        "pctThresholdActive": False,
        "pctThresholdValues": None,
        "preferredChannels": [NotificationChannel.SLACK],
        "preferredHourGMT": 5,
        "userId": ANY,
        "variableMap": {},
        "reference": "/p/partner/job",
        "variant": "node",
    }

    assert notification_service.update_notification.call_args.kwargs[
        "new_notification"
    ].dict() == {
        "absolute_threshold_active": False,
        "absolute_threshold_values": None,
        "app_id": PydanticObjectId("000000000000000000000004"),
        "platform_managed": True,
        "created_at": ANY,
        "datasource_id": PydanticObjectId("000000000000000000000004"),
        "formula": "",
        "frequency": NotificationFrequency.DAILY,
        "id": PydanticObjectId("000000000000000000000006"),
        "metric": NotificationMetric.HITS,
        "multi_node": True,
        "name": "name",
        "notification_active": False,
        "notification_type": {NotificationType.UPDATE},
        "pct_threshold_active": False,
        "pct_threshold_values": None,
        "preferred_channels": [NotificationChannel.SLACK],
        "preferred_hour_gmt": 5,
        "revision_id": ANY,
        "updated_at": None,
        "user_id": PydanticObjectId("000000000000000000000005"),
        "variable_map": {},
        "reference": "/p/partner/job",
        "variant": NotificationVariant.NODE,
        "enabled": True,
    }
    assert (
        notification_service.update_notification.call_args.kwargs["notification_id"]
        == "000000000000000000000006"
    )


def test_get_notifications(client_init, notification_service):
    response = client_init.get("/notifications?datasource_id=000000000000000000000004")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000006",
            "absoluteThresholdActive": False,
            "absoluteThresholdValues": None,
            "appId": "000000000000000000000004",
            "platformManaged": True,
            "createdAt": ANY,
            "datasourceId": "000000000000000000000004",
            "formula": "",
            "frequency": "daily",
            "metric": "hits",
            "multiNode": True,
            "name": "name",
            "notificationActive": False,
            "notificationType": [NotificationType.UPDATE],
            "pctThresholdActive": False,
            "pctThresholdValues": None,
            "preferredChannels": ["slack"],
            "preferredHourGmt": 5,
            "reference": "/p/partner/job",
            "revisionId": ANY,
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
            "variableMap": {},
            "variant": "node",
            "enabled": True,
        }
    ]
    notification_service.get_notifications_for_datasource_id.assert_called_once_with(
        **{"datasource_id": "000000000000000000000004"}
    )


def test_delete_notification(
    client_init,
    notification_service,
):
    response = client_init.delete("/notifications/00000000000000000000001b")
    assert response.status_code == 200

    notification_service.delete_notification.assert_called_once_with(
        **{
            "notification_id": "00000000000000000000001b",
        }
    )


@pytest.mark.asyncio
async def test_get_saved_retention_for_app(client_init, notification_service):
    response = client_init.get("/notifications?app_id=000000000000000000000008")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000006",
            "revisionId": None,
            "createdAt": ANY,
            "updatedAt": None,
            "datasourceId": "000000000000000000000004",
            "userId": "000000000000000000000005",
            "appId": "000000000000000000000004",
            "name": "name",
            "notificationType": ["update"],
            "metric": "hits",
            "multiNode": True,
            "platformManaged": True,
            "pctThresholdActive": False,
            "pctThresholdValues": None,
            "absoluteThresholdActive": False,
            "absoluteThresholdValues": None,
            "formula": "",
            "variableMap": {},
            "preferredHourGmt": 5,
            "frequency": "daily",
            "preferredChannels": ["slack"],
            "notificationActive": False,
            "variant": "node",
            "reference": "/p/partner/job",
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
    notification_service.get_notifications_for_apps.assert_called_once_with(
        **{"app_id": "000000000000000000000008"}
    )
