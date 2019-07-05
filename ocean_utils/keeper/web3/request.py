"""
This is copied from Web3 python library to control the `requests`
session and make it use the same behaviour as the rest of ocean_utils
components.
"""

import lru

from web3.utils.caching import (
    generate_cache_key,
)

from ocean_utils.http_requests.requests_session import get_requests_session


def _remove_session(key, session):
    session.close()


_session_cache = lru.LRU(8, callback=_remove_session)


def _get_session(*args, **kwargs):
    cache_key = generate_cache_key((args, kwargs))
    if cache_key not in _session_cache:
        # This is the main change from original Web3 `_get_session`
        _session_cache[cache_key] = get_requests_session()
    return _session_cache[cache_key]


def make_post_request(endpoint_uri, data, *args, **kwargs):
    kwargs.setdefault('timeout', 10)
    session = _get_session(endpoint_uri)
    response = session.post(endpoint_uri, data=data, *args, **kwargs)
    response.raise_for_status()

    return response.content
