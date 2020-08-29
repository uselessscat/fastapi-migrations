import shutil
from os.path import join

from tests.fixtures import dirs

from fastapi_migrations.cli import MigrationsCli
from fastapi_migrations import Migrations, MigrationsConfig


def test_create_migrations(dirs):
    m = Migrations()

    assert m
    assert m.configuration
    assert m.configuration.directory == dirs.DEFAULT


def test_create_migrations_cli(dirs):
    m = MigrationsCli()

    assert m
    assert m.migrations
    assert m.migrations.configuration
    assert m.migrations.configuration.directory == dirs.DEFAULT


def test_create_migrations_config(dirs):
    c = MigrationsConfig(directory=dirs.TEST)
    m = Migrations(c)

    assert m.configuration
    assert m.configuration.directory == dirs.TEST


def test_create_migrations_cli_config(dirs):
    c = MigrationsConfig(directory=dirs.TEST)
    m = MigrationsCli(c)

    assert m.migrations.configuration
    assert m.migrations.configuration.directory == dirs.TEST
