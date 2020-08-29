def test_import_alembic() -> None:
    import alembic

    assert alembic


def test_import_typer() -> None:
    import typer

    assert typer


def test_import_pydantic() -> None:
    import pydantic

    assert pydantic


def test_import_classes() -> None:
    from fastapi_migrations import Migrations, MigrationsConfig
    from fastapi_migrations.cli import MigrationsCli

    assert Migrations
    assert MigrationsCli
    assert MigrationsConfig
