from globus_sdk.transfer.response.base import TransferResponse


class IterableTransferResponse(TransferResponse):
    """
    Response class for non-paged list oriented resources. Allows top level
    fields to be accessed normally via standard item access, and also
    provides a convenient way to iterate over the sub-item list in the
    ``DATA`` key:

    >>> print("Path:", r["path"])
    >>> # Equivalent to: for item in r["DATA"]
    >>> for item in r:
    >>>     print(item["name"], item["type"])
    """

    iterable_data_key = "DATA"

    def __iter__(self):
        return iter(self[self.iterable_data_key])


class SharedEndpointListResponse(IterableTransferResponse):
    """
    A customized iterable response for the `shared_endpoint_list` API, which uses
    the key ``shared_endpoints`` for iterable data rather than ``DATA``.
    """

    iterable_data_key = "shared_endpoints"
