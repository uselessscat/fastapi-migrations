import shutil
from os import listdir
from os.path import isdir, isfile, join

from tests.fixtures import dirs

from fastapi_migrations import Migrations, MigrationsConfig


def test_migrations_dirs_not_exist(dirs):
    assert not isdir(dirs.DEFAULT)
    assert not isdir(dirs.TEST)


def test_init_creates_folders(dirs):
    m = Migrations()

    assert not isdir(dirs.DEFAULT)

    m.init()
    assert isdir(dirs.DEFAULT)

    shutil.rmtree(dirs.DEFAULT)


def test_init_creates_files(dirs):
    m = Migrations()

    assert not isdir(dirs.DEFAULT)

    m.init()
    assert isdir(dirs.DEFAULT)

    # created files
    assert isfile(join(dirs.DEFAULT, 'alembic.ini'))
    assert isfile(join(dirs.DEFAULT, 'env.py'))
    assert isfile(join(dirs.DEFAULT, 'README'))
    assert isfile(join(dirs.DEFAULT, 'script.py.mako'))
    assert isdir(join(dirs.DEFAULT, 'versions'))
    assert len(listdir(join(dirs.DEFAULT, 'versions'))) == 0

    shutil.rmtree(dirs.DEFAULT)


def test_init_creates_files_specified_folder(dirs):
    c = MigrationsConfig(directory=dirs.TEST)
    m = Migrations(c)

    assert not isdir(dirs.TEST)

    m.init()
    assert isdir(dirs.TEST)

    # created files
    assert isfile(join(dirs.TEST, 'alembic.ini'))
    assert isfile(join(dirs.TEST, 'env.py'))
    assert isfile(join(dirs.TEST, 'README'))
    assert isfile(join(dirs.TEST, 'script.py.mako'))
    assert isdir(join(dirs.TEST, 'versions'))
    assert len(listdir(join(dirs.TEST, 'versions'))) == 0

    shutil.rmtree(dirs.TEST)
