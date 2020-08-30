import shutil
from os import listdir
from os.path import isdir, isfile, join

from tests.fixtures import dirs, init_migrate, TestDirectories

from fastapi_migrations import Migrations, MigrationsConfig


def exclude_non_revision(dir_list: list) -> set:
    return set(dir_list) - set(['__pycache__'])


def test_migrations_dirs_not_exist(dirs: TestDirectories) -> None:
    assert not isdir(dirs.DEFAULT)
    assert not isdir(dirs.TEST)


def test_init_creates_folders(dirs: TestDirectories) -> None:
    m = Migrations()

    assert not isdir(dirs.DEFAULT)

    m.init()
    assert isdir(dirs.DEFAULT)

    shutil.rmtree(dirs.DEFAULT)


def test_init_fixture(dirs: TestDirectories, init_migrate) -> None:
    init_migrate()

    assert isdir(dirs.DEFAULT)


def test_init_creates_files(dirs: TestDirectories, init_migrate) -> None:
    init_migrate(script_location=dirs.DEFAULT)

    assert isfile(join(dirs.DEFAULT, 'alembic.ini'))
    assert isfile(join(dirs.DEFAULT, 'env.py'))
    assert isfile(join(dirs.DEFAULT, 'README'))
    assert isfile(join(dirs.DEFAULT, 'script.py.mako'))
    assert isdir(join(dirs.DEFAULT, 'versions'))
    assert len(listdir(join(dirs.DEFAULT, 'versions'))) == 0


def test_init_creates_files_specified_folder(
    dirs: TestDirectories,
    init_migrate
) -> None:
    init_migrate(script_location=dirs.TEST)

    assert isdir(dirs.TEST)
    assert isfile(join(dirs.TEST, 'alembic.ini'))
    assert isfile(join(dirs.TEST, 'env.py'))
    assert isfile(join(dirs.TEST, 'README'))
    assert isfile(join(dirs.TEST, 'script.py.mako'))
    assert isdir(join(dirs.TEST, 'versions'))
    assert len(listdir(join(dirs.TEST, 'versions'))) == 0


def test_init_creates_different_ini_file(
    dirs: TestDirectories,
    init_migrate: init_migrate
) -> None:
    init_migrate(script_location=dirs.TEST,
                 config_file_name='different.ini')

    assert isdir(dirs.TEST)
    assert isfile(join(dirs.TEST, 'different.ini'))


def test_revision_create(
    dirs: TestDirectories,
    init_migrate: init_migrate
) -> None:
    m = init_migrate(script_location=dirs.DEFAULT)

    assert len(listdir(join(dirs.DEFAULT, 'versions'))) == 0

    script = m.revision('revision_one')

    dir_list = listdir(join(m.configuration.script_location, 'versions'))
    assert len(exclude_non_revision(dir_list)) == 1

    assert script.doc == 'revision_one'
    assert isfile(script.path)
    assert isfile(join(dirs.DEFAULT, 'versions', script.revision + '.py'))

    script2 = m.revision('revision_two')

    dir_list = listdir(join(m.configuration.script_location, 'versions'))
    assert len(exclude_non_revision(dir_list)) == 2

    assert script2.doc == 'revision_two'
    assert isfile(script2.path)
    assert isfile(join(dirs.DEFAULT, 'versions', script2.revision + '.py'))


def test_revision_create_auto(
    dirs: TestDirectories,
    init_migrate: init_migrate
) -> None:
    m = init_migrate(script_location=dirs.DEFAULT)

    # TODO: Update this
    # m.revision('revision_one', autogenerate=True)
