import shutil
from os.path import join

from tests.fixtures import dirs, TestDirectories

from fastapi_migrations.cli import MigrationsCli
from fastapi_migrations import Migrations, MigrationsConfig


def test_create_migrations(dirs: TestDirectories) -> None:
    m = Migrations()

    assert m
    assert m.configuration
    assert m.configuration.migrations_directory == dirs.DEFAULT


def test_create_migrations_cli(dirs: TestDirectories) -> None:
    m = MigrationsCli()

    assert m
    assert m.migrations
    assert m.migrations.configuration
    assert m.migrations.configuration.migrations_directory == dirs.DEFAULT


def test_create_migrations_config(dirs: TestDirectories) -> None:
    c = MigrationsConfig(migrations_directory=dirs.TEST)
    m = Migrations(c)

    assert m.configuration
    assert m.configuration.migrations_directory == dirs.TEST


def test_create_migrations_cli_config(dirs: TestDirectories) -> None:
    c = MigrationsConfig(migrations_directory=dirs.TEST)
    m = MigrationsCli(c)

    assert m.migrations.configuration
    assert m.migrations.configuration.migrations_directory == dirs.TEST


def test_get_ini_config(dirs: TestDirectories) -> None:
    from alembic.config import Config as aconf

    m = Migrations()
    m.init()

    c = aconf(join(dirs.DEFAULT, 'alembic.ini'))

    print("ASDASDAS", c.file_config.sections)

    shutil.rmtree(dirs.DEFAULT)
