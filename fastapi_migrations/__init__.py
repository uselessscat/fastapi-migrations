from importlib.metadata import PackageNotFoundError, version
from typing import List

from .lib import Migrations, MigrationsConfig
from .cli import MigrationsCli

try:
    __version__ = version('fastapi-migrations')
except PackageNotFoundError:
    __version__ = '0.0.0+dev'

__all__: List[str] = [
    'Migrations',
    'MigrationsConfig',
    'MigrationsCli',
]
