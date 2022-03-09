from typing import Optional, Any, Tuple

import logging

from functools import wraps
from os.path import join, abspath, dirname

from pydantic import BaseSettings, Extra

from alembic import command
from alembic import __version__ as __alembic_version__
from alembic.util import CommandError
from alembic.config import Config as AlembicConfig

alembic_version: Tuple[int, ...] = tuple(
    [
        int(v)
        for v in __alembic_version__.split('.')[0:3]
    ]
)


# TODO: FIX
def catch_errors(f):  # type: ignore
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except (CommandError, RuntimeError) as exc:
            logging.error('Error: ' + str(exc))

    return wrapped


class MigrationsConfig(BaseSettings):
    sqlalchemy_url: Optional[str]
    sqlalchemy_async: bool = False

    script_location: str = 'migrations'
    config_file_name: str = 'alembic.ini'

    default_template_dir: str = 'default'
    default_async_template_dir: str = 'default_async'
    multidb_template_dir: str = 'multidb'
    template_directory: str = join(
        abspath(dirname(__file__)), 'templates'
    )

    metadata_package: Optional[str]
    metadata_class: Optional[str]

    file_template: str = '%%(rev)s'
    truncate_slug_length: str = '40'

    @classmethod
    def from_alembic_config(cls) -> 'MigrationsConfig':
        # TODO: implement
        return cls()

    def to_alembic_config(self) -> AlembicConfig:
        def get_template_directory() -> str:
            return self.template_directory

        alembic = AlembicConfig(
            join(self.script_location, self.config_file_name)
        )

        # set the template directory getter
        alembic.get_template_directory = get_template_directory

        # default alembic confs
        if self.sqlalchemy_url:
            alembic.set_main_option('sqlalchemy.url', self.sqlalchemy_url)

        alembic.set_main_option('script_location', self.script_location)
        alembic.set_main_option('file_template', self.file_template)
        alembic.set_main_option(
            'truncate_slug_length',
            self.truncate_slug_length
        )

        alembic.set_main_option('metadata_package', self.metadata_package or '')
        alembic.set_main_option('metadata_class', self.metadata_class or '')

        return alembic

    class Config:
        extra = Extra.allow


class Migrations():
    def __init__(
        self,
        config: Optional[MigrationsConfig] = None
    ):
        self.configuration = config or MigrationsConfig()

    def init(
        self,
        multidb: bool = False
    ) -> Any:
        config: AlembicConfig = self.configuration.to_alembic_config()

        if multidb:
            template = self.configuration.multidb_template_dir
        else:
            if self.configuration.sqlalchemy_async:
                template = self.configuration.default_async_template_dir
            else:
                template = self.configuration.default_template_dir

        return command.init(
            config,
            directory=self.configuration.script_location,
            template=template,
            package=False
        )

    def revision(
            self,
            message: Optional[str] = None,
            autogenerate: bool = False,
            sql: bool = False,
            head: str = 'head',
            splice: bool = False,
            branch_label: Optional[str] = None,
            version_path: Optional[str] = None,
            rev_id: Optional[str] = None
    ) -> Any:
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

    def autogenerate(
        self,
        message: Optional[str] = None,
        sql: bool = False,
        head: str = 'head',
        splice: bool = False,
        branch_label: Optional[str] = None,
        version_path: Optional[str] = None,
        rev_id: Optional[str] = None
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.revision(
            config,
            message,
            autogenerate=True,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id
        )

    def upgrade(
        self,
        revision: str = 'head',
        sql: bool = False,
        tag: Optional[str] = None
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.upgrade(
            config,
            revision,
            sql=sql,
            tag=tag
        )

    def downgrade(
        self,
        revision: str = '-1',
        sql: bool = False,
        tag: Optional[str] = None
    ) -> Any:
        config = self.configuration.to_alembic_config()

        if sql and revision == '-1':
            revision = 'head:-1'

        return command.downgrade(
            config,
            revision,
            sql=sql,
            tag=tag
        )

    def edit(
        self,
        revision: str = 'current'
    ) -> Any:
        if alembic_version >= (0, 8, 0):
            config = self.configuration.to_alembic_config()

            return command.edit(config, revision)
        else:
            raise RuntimeError('Alembic 0.8.0 or greater is required')

    def merge(
        self,
        revisions: str = '',
        message: Optional[str] = None,
        branch_label: Optional[str] = None,
        rev_id: Optional[str] = None
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.merge(
            config,
            revisions,
            message=message,
            branch_label=branch_label,
            rev_id=rev_id
        )

    def show(
        self,
        revision: str = 'head'
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.show(config, revision)

    def history(
        self,
        rev_range: Optional[str] = None,
        verbose: bool = False,
        indicate_current: bool = False
    ) -> Any:
        config = self.configuration.to_alembic_config()

        if alembic_version >= (0, 9, 9):
            return command.history(
                config,
                rev_range,
                verbose=verbose,
                indicate_current=indicate_current
            )
        else:
            return command.history(
                config,
                rev_range,
                verbose=verbose
            )

    def heads(
        self,
        verbose: bool = False,
        resolve_dependencies: bool = False
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.heads(
            config,
            verbose=verbose,
            resolve_dependencies=resolve_dependencies
        )

    def branches(
        self,
        verbose: bool = False
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.branches(config, verbose=verbose)

    def current(
        self,
        verbose: bool = False,
        head_only: bool = False
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.current(
            config,
            verbose=verbose,
            head_only=head_only
        )

    def stamp(
        self,
        revision: str = 'head',
        sql: bool = False,
        tag: Optional[str] = None
    ) -> Any:
        config = self.configuration.to_alembic_config()

        return command.stamp(
            config,
            revision,
            sql=sql,
            tag=tag
        )
