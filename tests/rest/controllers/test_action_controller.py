import json
from unittest.mock import ANY

from beanie import PydanticObjectId

from domain.actions.models import ActionGroup, ActionGroupCondition, CaptureEvent
from tests.utils import filter_response


def test_create_action(client_init, action_data, action_service):
    response = client_init.post("/actions", data=json.dumps(action_data))
    assert response.status_code == 200
    assert filter_response(response.json()) == {
        "_id": None,
        "appId": "000000000000000000000013",
        "datasourceId": "000000000000000000000013",
        "groups": [
            {
                "condition": "or",
                "event": "$autocapture",
                "href": None,
                "selector": "#__next > div > div.css-3h169z > div.css-8xl60i > "
                "button",
                "tag_name": None,
                "text": None,
                "url": None,
                "url_matching": None,
            }
        ],
        "eventType": CaptureEvent.AUTOCAPTURE,
        "name": "clicked on settings",
        "processedTill": None,
        "userId": "000000000000000000000013",
        "enabled": True,
    }

    action_service.build_action.assert_called_once_with(
        **{
            "appId": PydanticObjectId("000000000000000000000003"),
            "datasourceId": PydanticObjectId("000000000000000000000003"),
            "groups": [
                ActionGroup(
                    tag_name=None,
                    text=None,
                    href=None,
                    selector="#__next > div > div.css-3h169z > div.css-8xl60i > button",
                    url=None,
                    url_matching=None,
                    event="$autocapture",
                    condition=ActionGroupCondition.OR,
                )
            ],
            "name": "clicked on settings",
            "userId": "mock-user-id",
        }
    )
    action_service.add_action.assert_called_once()
    assert action_service.add_action.call_args.kwargs["action"].dict() == {
        "app_id": PydanticObjectId("000000000000000000000013"),
        "created_at": ANY,
        "datasource_id": PydanticObjectId("000000000000000000000013"),
        "groups": [
            {
                "condition": ActionGroupCondition.OR,
                "event": CaptureEvent.AUTOCAPTURE,
                "href": None,
                "selector": "#__next > div > div.css-3h169z > div.css-8xl60i > "
                "button",
                "tag_name": None,
                "text": None,
                "url": None,
                "url_matching": None,
            }
        ],
        "id": None,
        "name": "clicked on settings",
        "event_type": CaptureEvent.AUTOCAPTURE,
        "processed_till": None,
        "revision_id": ANY,
        "updated_at": None,
        "user_id": PydanticObjectId("000000000000000000000013"),
        "enabled": True,
    }
    action_service.update_events_for_action.assert_called_once()


def test_create_action_with_error(client_init, action_data, action_service):
    response = client_init.post("/actions", data=json.dumps(action_data))
    assert response.status_code == 400
    assert response.json() == {"detail": "Action name should be unique"}


def test_get_actions(client_init, action_service):
    response = client_init.get("/actions?datasource_id=000000000000000000000013")
    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": None,
            "appId": "000000000000000000000013",
            "createdAt": ANY,
            "datasourceId": "000000000000000000000013",
            "groups": [
                {
                    "condition": "or",
                    "event": "$autocapture",
                    "href": None,
                    "selector": "#__next > div > div.css-3h169z > div.css-8xl60i > "
                    "button",
                    "tag_name": None,
                    "text": None,
                    "url": None,
                    "url_matching": None,
                }
            ],
            "name": "clicked on settings",
            "eventType": "$autocapture",
            "processedTill": None,
            "revisionId": ANY,
            "updatedAt": None,
            "user": {
                "id": "000000000000000000000006",
                "email": "user011@example.com",
                "firstName": "Test",
                "lastName": "User",
                "picture": "https://images.example.com/avatar-1.png",
                "slackChannel": "#alerts",
                "hasVisitedSheets": False,
            },
            "userId": "000000000000000000000013",
            "enabled": True,
        }
    ]
    action_service.get_actions_for_datasource_id.assert_called_once_with(
        **{"datasource_id": "000000000000000000000013"}
    )


def test_update_action(client_init, action_data, action_service):
    response = client_init.put(
        "/actions/000000000000000000000014", data=json.dumps(action_data)
    )
    assert response.status_code == 200
    assert filter_response(response.json()) == {
        "_id": None,
        "appId": "000000000000000000000013",
        "datasourceId": "000000000000000000000013",
        "groups": [
            {
                "condition": "or",
                "event": "$autocapture",
                "href": None,
                "selector": "#__next > div > div.css-3h169z > div.css-8xl60i > "
                "button",
                "tag_name": None,
                "text": None,
                "url": None,
                "url_matching": None,
            }
        ],
        "name": "clicked on settings",
        "eventType": CaptureEvent.AUTOCAPTURE,
        "processedTill": None,
        "userId": "000000000000000000000013",
        "enabled": True,
    }
    action_service.update_action.assert_called_once()
    assert action_service.update_action.call_args.kwargs["action"].dict() == {
        "app_id": PydanticObjectId("000000000000000000000013"),
        "created_at": ANY,
        "datasource_id": PydanticObjectId("000000000000000000000013"),
        "groups": [
            {
                "condition": ActionGroupCondition.OR,
                "event": "$autocapture",
                "href": None,
                "selector": "#__next > div > div.css-3h169z > div.css-8xl60i > "
                "button",
                "tag_name": None,
                "text": None,
                "url": None,
                "url_matching": None,
            }
        ],
        "id": None,
        "name": "clicked on settings",
        "event_type": CaptureEvent.AUTOCAPTURE,
        "processed_till": None,
        "revision_id": ANY,
        "updated_at": None,
        "user_id": PydanticObjectId("000000000000000000000013"),
        "enabled": True,
    }


def test_get_actions_by_id(client_init, action_service):
    response = client_init.get("/actions/00000000000000000000001d")
    assert response.status_code == 200
    assert response.json() == {
        "_id": None,
        "appId": "000000000000000000000013",
        "createdAt": ANY,
        "datasourceId": "000000000000000000000013",
        "groups": [
            {
                "condition": "or",
                "event": CaptureEvent.AUTOCAPTURE,
                "href": None,
                "selector": "#__next > div > div.css-3h169z > div.css-8xl60i > "
                "button",
                "tag_name": None,
                "text": None,
                "url": None,
                "url_matching": None,
            }
        ],
        "name": "clicked on settings",
        "eventType": CaptureEvent.AUTOCAPTURE,
        "processedTill": None,
        "revisionId": ANY,
        "updatedAt": None,
        "userId": "000000000000000000000013",
        "enabled": True,
    }
    action_service.get_action.assert_called_once_with(
        **{"id": "00000000000000000000001d"}
    )


def test_transient_action(client_init, action_service, transient_action_data):
    response = client_init.post(
        "/actions/transient", data=json.dumps(transient_action_data)
    )
    assert response.status_code == 200
    assert response.json() == {
        "count": 1,
        "data": [
            {
                "event": "$autocapture",
                "source": "web",
                "timestamp": "2023-02-09T10:26:22",
                "uid": "18635b641091067-0b29b2c45f4c5d-16525635-16a7f0-18635b6410a285c",
                "url": "http://localhost:3000/analytics/explore/000000000000000000000014",
            }
        ],
    }
    action_service.compute_action.assert_called_once_with(
        **{
            "datasource_id": "000000000000000000000013",
            "app_id": PydanticObjectId("000000000000000000000003"),
            "groups": [
                {
                    "condition": "or",
                    "event": "$autocapture",
                    "href": None,
                    "selector": "#__next > div > div.css-3h169z > div.css-8xl60i > "
                    "button",
                    "tag_name": None,
                    "text": None,
                    "url": None,
                    "url_matching": None,
                }
            ],
            "date_filter": {"filter": {"days": 7}, "type": "last"},
        }
    )


def test_delete_action(client_init, action_service):
    response = client_init.delete("/actions/00000000000000000000001e")
    assert response.status_code == 200
    action_service.delete_action.assert_called_once_with(
        id=PydanticObjectId("00000000000000000000001e")
    )
