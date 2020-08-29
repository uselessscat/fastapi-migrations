import typing as t
import shutil
from os.path import isdir

import pytest

from fastapi_migrations import Migrations, MigrationsConfig


class TestDirectories:
    DEFAULT: str = 'migrations'
    TEST: str = 'migrations_test'


@pytest.fixture
def dirs() -> t.Type[TestDirectories]:
    return TestDirectories


@pytest.fixture
def init_migrate():
    mig_list = []

    def instance_migrations(**kwargs):
        c = MigrationsConfig(**kwargs)
        m = Migrations(c)
        mig_list.append(m)

        # check directory doesnt exists
        assert not isdir(m.configuration.migrations_directory)

        m.init()

        return m

    yield instance_migrations

    for mig in mig_list:
        shutil.rmtree(mig.configuration.migrations_directory)

        # check directory was erased
        assert not isdir(mig.configuration.migrations_directory)
