# Fastapi Migrations

![PyPI](https://img.shields.io/pypi/v/fastapi-migrations)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-migrations)
![PyPI - License](https://img.shields.io/pypi/l/fastapi-migrations)

![GitHub last commit](https://img.shields.io/github/last-commit/uselessscat/fastapi-migrations)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/uselessscat/fastapi-migrations)
![GitHub issues](https://img.shields.io/github/issues/uselessscat/fastapi-migrations)
![GitHub pull requests](https://img.shields.io/github/issues-pr/uselessscat/fastapi-migrations)

This library provides a small wrapper for alembic.

### Notice

**Under inital development. This can not be ready-for-production library.**

This can means:

- Breaking changes may be introduced
- Poor documentation and changeslogs
- Not totally tested
- Be forced to navigate through the source code to find out how it works

Wait to a version > 0.1.0 for usage in production environments.

## Installation

You can install this library with:

    pip3 install fastapi-migrations

## Usage

You can use both programatically and by CLI (command line interface).

Imagine your project folders

    app/
        cli/
            __init__.py
            action.py
        db/
            __init__.py
            base.py
        models/
            __init__.py
            my_model.py
        endpoints/
            __init__.py
            my_endpoint.py
        __init__.py
        config.py
        main.py

This is an example of `main.py`:

    from fastapi import FastAPI
    from fastapi_sqlalchemy import DBSessionMiddleware

    # Load configs and endpoints
    from app.config import settings
    from app.endpoints import router

    app: FastAPI = FastAPI(title=settings.project_name)

    # register routes
    app.include_router(router)

    # add middlewares
    app.add_middleware(DBSessionMiddleware, db_url=settings.database_uri)

    if __name__ == '__main__':
        # Load cli commands
        from app.cli import app as cli

        cli()

Then your `app/cli/__init__.py` can be like:

    import typer

    from fastapi_migrations.cli import MigrationsCli
    import app.cli.action as action

    # main cli app
    app: typer.Typer = typer.Typer()

    # these are our cli actions
    app.add_typer(action.app, name='action', help='Common actions the app do')

    # this line adds the fastapi-migrations cli commands to our app
    app.add_typer(MigrationsCli())

Now you can call your app from the command line and use `fastapi-migrations` like:

    py app/main.py db show

If you want to use this library programatically, this is an example:

The file `app/cli/action.py` can be like:

    import typer
    from fastapi_migrations import MigrationsConfig, Migrations

    app: typer.Typer = typer.Typer()

    @app.command()
    def show() -> None:
        config = MigrationsConfig()

        migrations = Migrations(config)

        migrations.show()

You can add this lines where you wish in your proyect. Here we ar adding it to a command line so we can call our app like:

    py app/main.py action show


# Async

You can pass `sqlalchemy_async` parameter to config. It generates alembic async env template with usage `fastapi-async-sqlalchemy` package instead of `fastapi-sqlalchemy`.

    config = MigrationsConfig()
    config.sqlalchemy_async = True


# Metadata

You can pass `metadata_package` and `metadata_class` parameters to config for use autogenerate feature.
If you have structure described in this readme you should pass these options:

    config = MigrationsConfig()
    config.metadata_package = 'app.db.base'
    config.metadata_class = 'Base'

# License

This software is distributed under [MIT license](LICENSE).
