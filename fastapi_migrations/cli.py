import typing as t

from typer import Typer
from fastapi_migrations import Migrations, MigrationsConfig


class MigrationsCli(Typer):
    def __init__(
        self,
        config: t.Optional[MigrationsConfig] = None,
        *,
        name: t.Optional[str] = 'db',
        help: t.Optional[str] = 'Database tools',
        **kwargs: t.Any
    ):
        super().__init__(name=name, help=help, **kwargs)

        self.migrations = Migrations(config or MigrationsConfig())
        self.__register_commands()

    def __register_commands(self) -> None:
        self.command('init')(self.migrations.init)
        self.command('revision')(self.migrations.revision)
        self.command('autogenerate')(self.migrations.autogenerate)
        self.command('upgrade')(self.migrations.upgrade)
        self.command('downgrade')(self.migrations.downgrade)
        self.command('edit')(self.migrations.edit)
        self.command('merge')(self.migrations.merge)
        self.command('show')(self.migrations.show)
        self.command('history')(self.migrations.history)
        self.command('heads')(self.migrations.heads)
        self.command('branches')(self.migrations.branches)
        self.command('current')(self.migrations.current)
        self.command('stamp')(self.migrations.stamp)
