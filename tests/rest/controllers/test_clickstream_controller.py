import json


def test_get_clickstream_events(client_init, datasource_service, clickstream_service):
    response = client_init.get(
        "/clickstream/000000000000000000000012",
    )

    assert response.status_code == 200
    assert response.json() == {
        "count": 2,
        "data": [
            {
                "event": "$pageview",
                "timestamp": "2023-02-09T04:50:47",
                "uid": "1862a9e52121a37-0b39b9498d8c54-16525635-16a7f0-1862a9e521328fa",
                "url": "http://localhost:3000/analytics/app/create",
                "source": "web",
            },
            {
                "event": "$pageview",
                "timestamp": "2023-02-07T08:45:13",
                "uid": "1862a9e52121a37-0b39b9498d8c54-16525635-16a7f0-1862a9e521328fa",
                "url": "http://localhost:3000/analytics/funnel/list/000000000000000000000012",
                "source": "web",
            },
        ],
    }
    clickstream_service.get_data_by_id.assert_called_once_with(
        dsId="000000000000000000000012", app_id="000000000000000000000003"
    )
