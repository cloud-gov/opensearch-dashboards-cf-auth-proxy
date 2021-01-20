import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "focus: Only run this test.")
