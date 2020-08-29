import pytest


class Dirs:
    DEFAULT = 'migrations'
    TEST = 'migrations_test'


@pytest.fixture
def dirs() -> Dirs:
    return Dirs
