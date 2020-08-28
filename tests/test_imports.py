def test_import_alembic():
    import alembic


def test_import_typer():
    import typer


def test_import_pydantic():
    import pydantic


def test_import_classes():
    from fastapi_migrations import Migrations, MigrationsConfig
    from fastapi_migrations.cli import MigrationsCli
