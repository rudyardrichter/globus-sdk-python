class PaginatorCollection(object):
    def __init__(self, paginator_spec):
        self.paginator_map = {}

        for paginator_class, spec in paginator_spec.items():
            for bound_method, paginator_args in spec.items():
                self._add_binding(paginator_class, paginator_args, bound_method)

    # This needs to be a separate callable to work correctly as a closure over loop
    # variables
    #
    # If you try to dynamically define functions in __init__ without wrapping them like
    # this, then you run into trouble with the fact that the resulting functions will
    # point at <locals> which aren't resolved until call time
    def _add_binding(self, paginator_class, paginator_args, bound_method):
        methodname = bound_method.__name__

        def paginated_method(*args, **kwargs):
            return paginator_class(
                bound_method, client_args=args, client_kwargs=kwargs, **paginator_args
            )

        self.paginator_map[methodname] = paginated_method

    def __getattr__(self, attrname):
        try:
            return self.paginator_map[attrname]
        except KeyError:
            pass
        raise AttributeError("No known paginator named '{}'".format(attrname))


class _LimitOffsetBasedPaginator(object):
    def __init__(
        self,
        method,
        get_page_size,
        max_total_results,
        page_size,
        client_args,
        client_kwargs,
    ):
        self.method = method
        self.get_page_size = get_page_size
        self.client_args = client_args
        self.client_kwargs = client_kwargs

        self.max_total_results = max_total_results
        self.limit = page_size
        self.offset = 0

    def _update_limit(self):
        if (
            self.max_total_results is not None
            and self.offset + self.limit > self.max_total_results
        ):
            self.limit = self.max_total_results - self.offset
        self.client_kwargs["limit"] = self.limit

    def _update_and_check_offset(self, current_page):
        self.offset += self.get_page_size(current_page)
        self.client_kwargs["offset"] = self.offset
        return (
            self.max_total_results is not None and self.offset >= self.max_total_results
        )


class HasNextPaginator(_LimitOffsetBasedPaginator):
    def __iter__(self):
        has_next_page = True
        while has_next_page:
            self._update_limit()
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            if self._update_and_check_offset(current_page):
                return
            has_next_page = current_page["has_next_page"]


class LimitOffsetTotalPaginator(_LimitOffsetBasedPaginator):
    def __iter__(self):
        has_next_page = True
        while has_next_page:
            self._update_limit()
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            if self._update_and_check_offset(current_page):
                return
            has_next_page = self.offset < current_page["total"]


class LastKeyPaginator(object):
    def __init__(self, method, client_args, client_kwargs):
        self.method = method
        self.last_key = None
        self.client_args = client_args
        self.client_kwargs = client_kwargs

    def __iter__(self):
        has_next_page = True
        while has_next_page:
            if self.last_key:
                self.client_kwargs["last_key"] = self.last_key
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.last_key = current_page.get("last_key")
            has_next_page = current_page["has_next_page"]


class MarkerPaginator(object):
    def __init__(self, method, client_args, client_kwargs):
        self.method = method
        self.marker = None
        self.client_args = client_args
        self.client_kwargs = client_kwargs

    def __iter__(self):
        has_next_page = True
        while has_next_page:
            if self.marker:
                self.client_kwargs["marker"] = self.last_key
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.marker = current_page.get("next_marker")
            has_next_page = bool(self.marker)
