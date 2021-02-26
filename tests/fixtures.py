from typing import Type, Callable, Any, Generator, Dict, Optional 

import shutil
from os.path import isdir

import pytest

from fastapi_migrations import Migrations, MigrationsConfig


class TestDirectories:
    DEFAULT: str = 'migrations'
    TEST: str = 'migrations_test'


@pytest.fixture
def dirs() -> Type[TestDirectories]:
    return TestDirectories


def init_migrate():
    mig_list = []

    def instance_migrations(**kwargs) -> Type[Migrations]:
        c = MigrationsConfig(**kwargs)
        m = Migrations(c)
        mig_list.append(m)

        # check directory doesn't exists
        assert not isdir(m.configuration.script_location)

        m.init()

        return m

    yield instance_migrations

    for mig in mig_list:
        shutil.rmtree(mig.configuration.script_location)

        # check directory was erased
        assert not isdir(mig.configuration.script_location)
