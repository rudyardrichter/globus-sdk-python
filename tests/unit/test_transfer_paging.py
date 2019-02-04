import json

import pytest
import requests
import six

from globus_sdk.transfer.paging import PaginatedResource
from globus_sdk.transfer.response import IterableTransferResponse

N = 25


class PagingSimulator(object):
    def __init__(self, n):
        self.n = n  # the number of simulated items

    def simulate_get(
        self,
        path,
        params=None,
        headers=None,
        response_class=None,
        response_kwargs=None,
        retry_401=True,
    ):
        """
        Simulates a paginated response from a Globus API get supporting limit,
        offset, and has next page
        """
        offset = params["offset"]
        limit = params["limit"]
        data = {}  # dict that will be treated as the json data of a response
        data["offset"] = offset
        data["limit"] = limit
        # fill data field
        data["DATA"] = []
        for i in range(offset, min(self.n, offset + limit)):
            data["DATA"].append({"value": i})
        # fill has_next_page field
        data["has_next_page"] = (offset + limit) < self.n

        # make the simulated response
        response = requests.Response()
        response._content = six.b(json.dumps(data))
        response.headers["Content-Type"] = "application/json"
        return IterableTransferResponse(response)

    def simulate_get_shared_endpoint_list(
        self,
        path,
        params=None,
        headers=None,
        response_class=None,
        response_kwargs=None,
        retry_401=True,
    ):
        """
        Simulates a paginated response from GET shared_endpoint_list
        which uses a different paging style and a non DATA key

        Uses simplified next_token logic where next_token is the first int
        to return on the next page
        """
        data = {}
        next_token = params.get("next_token") or 0
        max_results = 10  # limited for ease of testing

        # if we are capped by n
        if next_token + max_results >= self.n:
            shared_endpoints = [{"id": i} for i in range(next_token, self.n)]
            next_token = None

        # if we are capped by max results
        else:
            shared_endpoints = [
                {"id": i} for i in range(next_token, next_token + max_results)
            ]
            next_token = next_token + max_results

        # make the simulated response
        data = {"shared_endpoints": shared_endpoints, "next_token": next_token}
        response = requests.Response()
        response._content = six.b(json.dumps(data))
        response.headers["Content-Type"] = "application/json"
        return IterableTransferResponse(response, **(response_kwargs or {}))


@pytest.fixture
def paging_simulator():
    return PagingSimulator(N)


def test_data(paging_simulator):
    """
    Gets data from PaginatedResource objects based on paging_simulator,
    confirms data is the expected range of numbers
    tests num_results < n, num_results > n, num_results = None,
    """
    # num_results < n
    less_results = N - 7
    pr_less = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=less_results,
    )
    # confirm results
    for item, expected in zip(pr_less.data, range(less_results)):
        assert item["value"] == expected

    assert pr_less.num_results_fetched == less_results

    # num_results > n
    more_results = N + 7
    pr_more = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=more_results,
    )
    # confirm results
    for item, expected in zip(pr_more.data, range(N)):
        assert item["value"] == expected
    assert pr_more.num_results_fetched == N

    # num_results = None (fetch all)
    pr_none = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=None,
    )
    # confirm results
    for item, expected in zip(pr_none.data, range(N)):
        assert item["value"] == expected
    assert pr_none.num_results_fetched == N


def test_iterable_func(paging_simulator):
    """
    Gets the generator from a PaginatedResource's iterable_func,
    sanity checks usage
    """
    pr = PaginatedResource(
        paging_simulator.simulate_get,
        "path",
        {"params": {}},
        max_results_per_call=10,
        num_results=None,
    )

    generator = pr.iterable_func()
    for i in range(N):
        assert six.next(generator)["value"] == i

    with pytest.raises(StopIteration):
        six.next(generator)


def test_shared_endpoint_iteration(paging_simulator):
    """
    Confirms PaginatedResource handles the non standard
    formatting of the shared_endpoint_list response
    """
    # num_results < n
    less_results = N - 7
    pr_less = PaginatedResource(
        paging_simulator.simulate_get_shared_endpoint_list,
        "path",
        {"params": {}},
        paging_style=PaginatedResource.PAGING_STYLE_TOKEN,
        iter_key="shared_endpoints",
        num_results=less_results,
    )
    # confirm results
    for item, expected in zip(pr_less.data, range(less_results)):
        assert item["id"] == expected

    assert pr_less.num_results_fetched == less_results

    # num_results > n
    more_results = N + 7
    pr_more = PaginatedResource(
        paging_simulator.simulate_get_shared_endpoint_list,
        "path",
        {"params": {}},
        paging_style=PaginatedResource.PAGING_STYLE_TOKEN,
        iter_key="shared_endpoints",
        num_results=more_results,
    )
    # confirm results
    for item, expected in zip(pr_more.data, range(N)):
        assert item["id"] == expected
    assert pr_more.num_results_fetched == N

    # num_results = None (fetch all)
    pr_none = PaginatedResource(
        paging_simulator.simulate_get_shared_endpoint_list,
        "path",
        {"params": {}},
        paging_style=PaginatedResource.PAGING_STYLE_TOKEN,
        iter_key="shared_endpoints",
        num_results=None,
    )
    # confirm results
    for item, expected in zip(pr_none.data, range(N)):
        assert item["id"] == expected
    assert pr_none.num_results_fetched == N
