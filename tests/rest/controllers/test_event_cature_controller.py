import json
from base64 import b64encode

import pytest


def test_capture_click_stream(client_init, datasource_service, clickstream_service):
    payload = {
        "event": "$pageview",
        "properties": {
            "token": "000000000000000000000003",
            "distinct_id": "synthetic-test-user",
            "$current_url": "https://example.com/test-page",
        },
        "timestamp": "2024-01-01T00:00:00Z",
    }
    encoded = b64encode(json.dumps(payload).encode()).decode()
    response = client_init.post(
        "/events/capture/e/?ip=127.0.0.1&_=1&ver=test",
        data={"data": encoded},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}
    clickstream_service.update_events.assert_awaited_once_with(
        datasource_id=payload["properties"]["token"],
        events=[payload],
        app_id=datasource_service.get_datasources_for_platform.return_value.result()[0].app_id,
    )


@pytest.mark.parametrize("path", [
    "/events/capture/static/array.js",
    "/events/capture/static/array.js.map",
])
def test_omitted_browser_sdk_returns_not_found(client_init, path):
    response = client_init.get(path)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_capture_decide_remains_available(client_init):
    response = client_init.post(
        "/events/capture/decide/?v=test&ip=127.0.0.1&_=1&ver=test"
    )
    assert response.status_code == 200
    assert response.json() == {
        "config": {"enable_collect_everything": True},
        "sessionRecording": False,
    }
