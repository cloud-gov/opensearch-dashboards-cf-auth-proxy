from kibana_cf_auth_proxy.headers import list_to_ext_header
import pytest


def test_spaces_to_header():
    header = list_to_ext_header(["foo"])
    assert header == r'"foo"'

    header = list_to_ext_header(["foo", "bar"])
    assert header == r'"foo", "bar"'
