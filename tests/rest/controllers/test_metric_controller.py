import json
from unittest.mock import ANY

import pytest

from domain.common.filter_models import FilterDataType, FilterOperatorsString
from domain.metrics.models import (
    MetricBasicAggregation,
    SegmentsAndEvents,
    SegmentsAndEventsAggregations,
    SegmentsAndEventsType,
)
from domain.segments.models import SegmentFilterConditions, WhereSegmentFilter


def test_compute_metric(
    client_init, compute_metric_request, computed_metric_response, metric_service
):
    """
    Test compute_metric
    """

    response = client_init.post(
        "/metrics/compute", data=json.dumps(compute_metric_request)
    )
    assert response.status_code == 200
    assert response.json() == computed_metric_response
    metric_service.compute_metric.assert_called_once_with(
        **{
            "aggregates": [
                SegmentsAndEvents(
                    variable="A",
                    variant=SegmentsAndEventsType.EVENT,
                    aggregations=SegmentsAndEventsAggregations(
                        functions=MetricBasicAggregation.COUNT,
                        property="Video_Seen",
                    ),
                    reference_id="Video_Seen",
                    filters=[
                        WhereSegmentFilter(
                            operator=FilterOperatorsString.IS,
                            operand="properties.$city",
                            values=["Bengaluru"],
                            all=False,
                            type=SegmentFilterConditions.WHERE,
                            condition=SegmentFilterConditions.WHERE,
                            datatype=FilterDataType.STRING,
                        )
                    ],
                    conditions=["where"],
                )
            ],
            "breakdown": [],
            "datasource_id": "000000000000000000000019",
            "app_id": "000000000000000000000003",
            "date_filter": None,
            "segment_filter": None,
            "function": "A",
        }
    )


def test_get_metrics(client_init, metric_service):
    response = client_init.get("/metrics?datasource_id=000000000000000000000004")

    assert response.status_code == 200
    assert response.json() == [
        {
            "_id": "000000000000000000000016",
            "aggregates": [
                {
                    "aggregations": {"functions": "count", "property": "Video_Seen"},
                    "filters": [],
                    "reference_id": "Video_Seen",
                    "variable": "A",
                    "variant": "event",
                },
                {
                    "aggregations": {"functions": "count", "property": "Video_Open"},
                    "filters": [],
                    "reference_id": "Video_Open",
                    "variable": "B",
                    "variant": "event",
                },
            ],
            "appId": "00000000000000000000000a",
            "breakdown": [],
            "createdAt": ANY,
            "datasourceId": "000000000000000000000008",
            "function": "A/B",
            "name": "Video Metric",
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
            "userId": "000000000000000000000009",
            "dateFilter": None,
            "enabled": True,
            "segmentFilter": None,
        }
    ]
    metric_service.get_metrics_for_datasource_id.assert_called_once_with(
        **{"datasource_id": "000000000000000000000004"}
    )


def test_validate_metric_formula(client_init, metric_service):
    response = client_init.post(
        "/metrics/validate_formula",
        data=json.dumps({"formula": "A,  B", "variableList": ["A", "B"]}),
    )
    assert response.status_code == 200
    assert response.json() == True
    metric_service.validate_formula.assert_called_with(
        **{"formula": "A,  B", "variable_list": ["A", "B"]}
    )


def test_update_metric(
    client_init, metric_data, metric_service, datasource_service, notification_service
):
    response = client_init.put(
        "/metrics/000000000000000000000006", data=json.dumps(metric_data)
    )
    assert response.status_code == 200
    assert response.json() == {
        "_id": "000000000000000000000016",
        "aggregates": [
            {
                "aggregations": {"functions": "count", "property": "Video_Seen"},
                "filters": [],
                "reference_id": "Video_Seen",
                "variable": "A",
                "variant": "event",
            },
            {
                "aggregations": {"functions": "count", "property": "Video_Open"},
                "filters": [],
                "reference_id": "Video_Open",
                "variable": "B",
                "variant": "event",
            },
        ],
        "appId": "00000000000000000000000a",
        "breakdown": [],
        "createdAt": ANY,
        "datasourceId": "000000000000000000000008",
        "function": "A/B",
        "name": "Video Metric",
        "revisionId": ANY,
        "updatedAt": None,
        "userId": "000000000000000000000009",
        "dateFilter": None,
        "segmentFilter": None,
        "enabled": True,
    }

    datasource_service.get_datasource.assert_called_with(
        "000000000000000000000003",
    )

    notification_service.fetch_and_delete_notification.assert_called_once_with(
        **{
            "reference_id": "000000000000000000000006",
            "datasource_id": "000000000000000000000003",
        }
    )


def test_delete_metric(client_init, metric_service, notification_service):
    response = client_init.delete(
        "/metrics/00000000000000000000001b?datasource_id=00000000000000000000001b"
    )
    assert response.status_code == 200

    metric_service.delete_metric.assert_called_once_with(
        **{
            "metric_id": "00000000000000000000001b",
        }
    )
    notification_service.fetch_and_delete_notification.assert_called_with(
        **{
            "reference_id": "00000000000000000000001b",
            "datasource_id": "00000000000000000000001b",
        }
    )


@pytest.mark.asyncio
async def test_get_saved_metrics_for_app(client_init, metric_service):
    response = client_init.get("/metrics?app_id=000000000000000000000008")

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
            "name": "Video Metric",
            "function": "A/B",
            "aggregates": [
                {
                    "variable": "A",
                    "variant": "event",
                    "aggregations": {"functions": "count", "property": "Video_Seen"},
                    "reference_id": "Video_Seen",
                    "filters": [],
                },
                {
                    "variable": "B",
                    "variant": "event",
                    "aggregations": {"functions": "count", "property": "Video_Open"},
                    "reference_id": "Video_Open",
                    "filters": [],
                },
            ],
            "breakdown": [],
            "dateFilter": None,
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
    metric_service.get_metrics_by_app_id.assert_called_once_with(
        **{"app_id": "000000000000000000000008"}
    )
