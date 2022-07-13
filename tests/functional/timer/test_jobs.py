import json
from datetime import datetime, timedelta

import pytest

from globus_sdk import TimerClient, TimerJob, TransferClient, TransferData
from globus_sdk._testing import get_last_request, load_response
from globus_sdk.config import get_service_url
from globus_sdk.utils import slash_join
from tests.common import GO_EP1_ID, GO_EP2_ID


@pytest.fixture
def timer_client():
    return TimerClient()


def test_list_jobs(timer_client):
    meta = load_response(timer_client.list_jobs).metadata
    response = timer_client.list_jobs()
    assert response.http_status == 200
    assert set(meta["job_ids"]) == {job["job_id"] for job in response.data["jobs"]}


def test_get_job(timer_client):
    meta = load_response(timer_client.get_job).metadata
    response = timer_client.get_job(meta["job_id"])
    assert response.http_status == 200
    assert response.data.get("job_id") == meta["job_id"]


@pytest.mark.parametrize("start", [datetime.utcnow(), "2022-04-05T06:00:00"])
@pytest.mark.parametrize(
    "interval", [timedelta(days=1), timedelta(minutes=60), 600, None]
)
@pytest.mark.parametrize("convert_to_dict", [True, False])
def test_create_job(timer_client, start, interval, convert_to_dict):
    meta = load_response(timer_client.create_job).metadata
    transfer_client = TransferClient()
    transfer_client.get_submission_id = lambda *_0, **_1: {  # type: ignore
        "value": "mock"
    }
    transfer_data = TransferData(transfer_client, GO_EP1_ID, GO_EP2_ID)
    if convert_to_dict:
        data = dict(transfer_data)
    else:
        data = transfer_data
    timer_job = TimerJob.from_transfer_data(data, start, interval)
    response = timer_client.create_job(timer_job)
    assert response.http_status == 201
    assert response.data["job_id"] == meta["job_id"]
    req_body = json.loads(get_last_request().body)  # type: ignore
    # Check that particular fields do/not exist in the request if we use
    # `from_transfer_data`
    assert "source_endpoint_id" in req_body["callback_body"]["body"]
    assert "DATA" not in req_body["callback_body"]["body"]
    assert response.http_status == 201
    assert response.data["job_id"] == meta["job_id"]
    if isinstance(start, datetime):
        assert req_body["start"] == start.isoformat()
    else:
        assert req_body["start"] == start
    if isinstance(interval, timedelta):
        assert req_body["interval"] == interval.total_seconds()
    else:
        assert req_body["interval"] == interval
    assert req_body["callback_url"] == slash_join(
        get_service_url("actions"), "/transfer/transfer/run"
    )


def test_update_job(timer_client):
    meta = load_response(timer_client.update_job).metadata
    response = timer_client.update_job(meta["job_id"], {"name": meta["name"]})
    assert response.http_status == 200
    assert response.data["job_id"] == meta["job_id"]
    assert response.data["name"] == meta["name"]


def test_delete_job(timer_client):
    meta = load_response(timer_client.delete_job).metadata
    response = timer_client.delete_job(meta["job_id"])
    assert response.http_status == 200
    assert response.data["job_id"] == meta["job_id"]
