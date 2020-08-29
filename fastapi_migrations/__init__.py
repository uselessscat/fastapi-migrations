import os
import sys
import logging
import argparse
import typing as t
from functools import wraps
from os.path import join, abspath, dirname

from pydantic import BaseSettings, Extra

from alembic import command
from alembic import __version__ as __alembic_version__
from alembic.util import CommandError
from alembic.config import Config as AlembicConfig


alembic_version = tuple([int(v) for v in __alembic_version__.split('.')[0:3]])


def catch_errors(f):  # type: ignore
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except (CommandError, RuntimeError) as exc:
            logging.error('Error: ' + str(exc))

    return wrapped


class MigrationsConfig(BaseSettings):
    migrations_directory: str = 'migrations'
    migrations_ini_file: str = 'alembic.ini'

    migrations_default_template: str = 'default'
    migrations_multidb_template: str = 'multidb'
    migrations_template_directory: str = join(
        abspath(dirname(__file__)), 'templates'
    )

    @classmethod
    def from_alembic_config(cls) -> 'MigrationsConfig':
        # TODO: implement
        return cls()

    def to_alembic_config(self) -> AlembicConfig:
        def get_template_directory() -> str:
            return self.migrations_template_directory

        alembic = AlembicConfig(
            join(self.migrations_directory, self.migrations_ini_file)
        )

        alembic.get_template_directory = get_template_directory
        alembic.set_main_option('script_location', self.migrations_directory)
        # alembic.print_stdout(sys.stdout)
        # alembic.config_file_name = join(self.directory, 'alembic.ini')

        return alembic

    class Config:
        extra = Extra.allow


class Migrations():
    def __init__(self, config: t.Optional[MigrationsConfig] = None):
        self.configuration = config or MigrationsConfig()

    def init(self, multidb: bool = False) -> None:
        directory: str = self.configuration.migrations_directory

        # config = current_app.extensions['migrate'].\
        #    migrate.call_configure_callbacks(config)
        config: AlembicConfig = self.configuration.to_alembic_config()

        template_name: str = self.configuration.migrations_multidb_template \
            if multidb \
            else self.configuration.migrations_default_template

        return command.init(config, directory, template_name)

    def revision(
            self,
            message: t.Optional[str] = None,
            autogenerate: bool = False,
            sql: bool = False,
            head: str = 'head',
            splice: bool = False,
            branch_label: bool = None,
            version_path=None,
            rev_id=None
    ) -> None:
        config = self.configuration.to_alembic_config()

        return command.revision(
            config,
            message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id
        )

    def migrate(self, message=None, sql=False, head='head', splice=False,
                branch_label=None, version_path=None, rev_id=None, x_arg=None) -> None:
        config = self.__get_config(opts=['autogenerate'], x_arg=x_arg)

        return command.revision(config, message, autogenerate=True, sql=sql,
                                head=head, splice=splice, branch_label=branch_label,
                                version_path=version_path, rev_id=rev_id)

    def upgrade(self, revision='head', sql=False, tag=None, x_arg=None) -> None:
        config = self.__get_config(x_arg=x_arg)

        return command.upgrade(config, revision, sql=sql, tag=tag)

    def downgrade(self, revision='-1', sql=False, tag=None, x_arg=None) -> None:
        config = self.__get_config(x_arg=x_arg)
        if sql and revision == '-1':
            revision = 'head:-1'
        return command.downgrade(config, revision, sql=sql, tag=tag)

    def edit(self, revision='current') -> None:
        if alembic_version >= (0, 8, 0):
            config = self.__get_config()
            return command.edit(config, revision)
        else:
            raise RuntimeError('Alembic 0.8.0 or greater is required')

    def merge(self, revisions='', message=None, branch_label=None,
              rev_id=None) -> None:
        config = self.__get_config()
        return command.merge(config, revisions, message=message,
                             branch_label=branch_label, rev_id=rev_id)

    def show(self, revision: str = 'head') -> None:
        config = self.configuration.to_alembic_config()
        return command.show(config, revision)

    def history(self, rev_range=None, verbose=False, indicate_current=False) -> None:
        config = self.__get_config()
        if alembic_version >= (0, 9, 9):
            return command.history(config, rev_range, verbose=verbose,
                                   indicate_current=indicate_current)
        else:
            return command.history(config, rev_range, verbose=verbose)

    def heads(self, verbose=False, resolve_dependencies=False) -> None:
        config = self.__get_config()
        return command.heads(config, verbose=verbose,
                             resolve_dependencies=resolve_dependencies)

    def branches(self, verbose=False) -> None:
        config = self.__get_config()
        return command.branches(config, verbose=verbose)

    def current(self, verbose=False, head_only=False) -> None:
        config = self.__get_config()
        return command.current(config, verbose=verbose, head_only=head_only)

    def stamp(self, revision='head', sql=False, tag=None) -> None:
        config = self.__get_config()
        return command.stamp(config, revision, sql=sql, tag=tag)

    def __get_config(self, x_arg=None, opts=None):
        directory = self.configuration.directory

        config = Config(os.path.join(directory, 'alembic.ini'))
        config.set_main_option('script_location', directory)

        if config.cmd_opts is None:
            config.cmd_opts = argparse.Namespace()

        for opt in opts or []:
            setattr(config.cmd_opts, opt, True)

        if not hasattr(config.cmd_opts, 'x'):
            if x_arg is not None:
                setattr(config.cmd_opts, 'x', [])
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                setattr(config.cmd_opts, 'x', None)

        return config


class _MigrateConfig(object):
    def __init__(self, migrate, db, **kwargs):
        self.migrate = migrate
        self.db = db
        self.directory = migrate.directory
        self.configure_args = kwargs

    @property
    def metadata(self):
        return self.db.metadata


class Migrate(object):
    def __init__(self, app=None, db=None, directory='migrations', **kwargs):
        self.configure_callbacks = []
        self.db = db
        self.directory = str(directory)
        self.alembic_ctx_kwargs = kwargs
        if app is not None and db is not None:
            self.init_app(app, db, directory)

    def init_app(self, app, db=None, directory=None, **kwargs):
        self.db = db or self.db
        self.directory = str(directory or self.directory)
        self.alembic_ctx_kwargs.update(kwargs)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['migrate'] = _MigrateConfig(self, self.db,
                                                   **self.alembic_ctx_kwargs)

    def configure(self, f):
        self.configure_callbacks.append(f)
        return f

    def call_configure_callbacks(self, config):
        for f in self.configure_callbacks:
            config = f(config)
        return config
