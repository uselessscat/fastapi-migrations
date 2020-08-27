import sys
import os
import logging
from functools import wraps
import argparse

from alembic.util import CommandError
from alembic import command
from alembic.config import Config as AlembicConfig
from alembic import __version__ as __alembic_version__

from pydantic import BaseSettings


def catch_errors(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except (CommandError, RuntimeError) as exc:
            log.error('Error: ' + str(exc))

    return wrapped


# TODO: DELETE THIS
class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')


class MigrationsConfig(BaseSettings):
    directory = 'migrations'


class Migrations():
    def __init__(self, config: MigrationsConfig):
        self.configuration = config

    @catch_errors
    def init(self, directory=None, multidb=False):
        if directory is None:
            directory = self.configuration.directory

        config = Config()
        config.set_main_option('script_location', directory)

        config.config_file_name = os.path.join(directory, 'alembic.ini')

        # config = current_app.extensions['migrate'].\
        #    migrate.call_configure_callbacks(config)
        if multidb:
            command.init(config, directory, 'multidb')
        else:
            command.init(config, directory, 'default')

    @catch_errors
    def revision(self, directory=None, message=None, autogenerate=False, sql=False,
                 head='head', splice=False, branch_label=None, version_path=None,
                 rev_id=None):
        config = self.__get_config(directory)
        command.revision(config, message, autogenerate=autogenerate, sql=sql,
                         head=head, splice=splice, branch_label=branch_label,
                         version_path=version_path, rev_id=rev_id)

    @catch_errors
    def migrate(self, directory=None, message=None, sql=False, head='head', splice=False,
                branch_label=None, version_path=None, rev_id=None, x_arg=None):
        config = self.__get_config(
            directory, opts=['autogenerate'], x_arg=x_arg)

        command.revision(config, message, autogenerate=True, sql=sql,
                         head=head, splice=splice, branch_label=branch_label,
                         version_path=version_path, rev_id=rev_id)

    @catch_errors
    def upgrade(self, directory=None, revision='head', sql=False, tag=None, x_arg=None):
        config = self.__get_config(directory, x_arg=x_arg)

        command.upgrade(config, revision, sql=sql, tag=tag)

    @catch_errors
    def downgrade(self, directory=None, revision='-1', sql=False, tag=None, x_arg=None):
        config = self.__get_config(directory, x_arg=x_arg)
        if sql and revision == '-1':
            revision = 'head:-1'
        command.downgrade(config, revision, sql=sql, tag=tag)

    @catch_errors
    def edit(self, directory=None, revision='current'):
        if alembic_version >= (0, 8, 0):
            config = self.__get_config(directory)
            command.edit(config, revision)
        else:
            raise RuntimeError('Alembic 0.8.0 or greater is required')

    @catch_errors
    def merge(self, directory=None, revisions='', message=None, branch_label=None,
              rev_id=None):
        config = self.__get_config(directory)
        command.merge(config, revisions, message=message,
                      branch_label=branch_label, rev_id=rev_id)

    @catch_errors
    def show(self, directory=None, revision='head'):
        config = self.__get_config(directory)
        command.show(config, revision)

    @catch_errors
    def history(self, directory=None, rev_range=None, verbose=False, indicate_current=False):
        config = self.__get_config(directory)
        if alembic_version >= (0, 9, 9):
            command.history(config, rev_range, verbose=verbose,
                            indicate_current=indicate_current)
        else:
            command.history(config, rev_range, verbose=verbose)

    @catch_errors
    def heads(self, directory=None, verbose=False, resolve_dependencies=False):
        config = self.__get_config(directory)
        command.heads(config, verbose=verbose,
                      resolve_dependencies=resolve_dependencies)

    @catch_errors
    def branches(self, directory=None, verbose=False):
        config = self.__get_config(directory)
        command.branches(config, verbose=verbose)

    @catch_errors
    def current(self, directory=None, verbose=False, head_only=False):
        config = self.__get_config(directory)
        command.current(config, verbose=verbose, head_only=head_only)

    @catch_errors
    def stamp(self, directory=None, revision='head', sql=False, tag=None):
        config = self.__get_config(directory)
        command.stamp(config, revision, sql=sql, tag=tag)

    def __get_config(self, directory=None, x_arg=None, opts=None):
        if directory is None:
            directory = self.configuration.directory
        directory = str(directory)

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
        # return self.call_configure_callbacks(config)
        return config


alembic_version = tuple([int(v) for v in __alembic_version__.split('.')[0:3]])
log = logging.getLogger()


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
