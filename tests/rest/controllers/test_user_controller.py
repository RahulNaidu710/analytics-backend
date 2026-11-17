def test_get_user(client_init, user_data):
    response = client_init.get("/user/property", params=user_data)
    assert response.status_code == 200
    assert response.json() == {
        "userId": "user_id",
        "datasourceId": "datasource_id",
        "property": {
            "$insert_id": "00000000-0000-4000-8000-00000000001a",
            "$insert_key": "00000000000000000000000000000003e9#832",
            "$schema": 13,
            "amplitude_id": 502527487487,
            "app": 281811,
            "city": "Example Location 1",
        },
    }


def test_get_dropped_user(client_init, dropped_user_data):
    response = client_init.get("/user/property", params=dropped_user_data)
    assert response.status_code == 200
    assert response.json() == {
        "userId": "user_id",
        "datasourceId": "datasource_id",
        "property": {
            "$insert_id": "00000000-0000-4000-8000-00000000001a",
            "$insert_key": "00000000000000000000000000000003e9#832",
            "$schema": 13,
            "amplitude_id": 502527487487,
            "app": 281811,
            "city": "Example Location 1",
        },
    }
