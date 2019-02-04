from globus_sdk.transfer.response.base import TransferResponse


class IterableTransferResponse(TransferResponse):
    """
    Response class for non-paged list oriented resources. Allows top level
    fields to be accessed normally via standard item access, and also
    provides a convenient way to iterate over the sub-item list in the
    specified ``iter_key``:

    >>> print("Path:", r["path"])
    >>> # Equivalent to: for item in r[iter_key]
    >>> for item in r:
    >>>     print(item["name"], item["type"])
    """

    def __init__(self, http_response, iter_key="DATA", client=None):
        TransferResponse.__init__(self, http_response, client=client)
        self.iter_key = iter_key

    def __iter__(self):
        return iter(self[self.iter_key])
