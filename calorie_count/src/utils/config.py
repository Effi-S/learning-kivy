"""Implementation details for accessing and updating config.ini file."""
import atexit
import configparser
import os
import uuid
from pathlib import Path

CONFIG = next(Path().glob('**/config.ini'), None)
if not CONFIG:
    CONFIG = Path('config.ini')
THEME_HEADER = 'THEME'
DB_PATH_HEADER, DB_PATH_SECTION = "DB_PATH", 'path'


def set_theme(theme_style: str,
              accent_palette: str,
              primary_palette: str,
              config_path: str = CONFIG) -> None:
    """ Set the theme info in config.ini """
    parser = configparser.ConfigParser()
    parser.read(config_path)
    parser[THEME_HEADER] = {
        'theme_style': theme_style,
        'primary_palette': primary_palette,
        'accent_palette': accent_palette,
    }
    with open(CONFIG, 'w+') as fl:
        parser.write(fl)


def get_theme(config_path: str = CONFIG) -> tuple[str, str, str]:
    """Returns the theme info saved in config.ini"""
    parser = configparser.ConfigParser()
    parser.read(config_path)
    return parser.get(THEME_HEADER, 'theme_style', fallback="Dark"), \
        parser.get(THEME_HEADER, 'accent_palette', fallback="Teal"), \
        parser.get(THEME_HEADER, 'primary_palette', fallback="BlueGray")


def get_db_path(config_path: str = CONFIG) -> str:
    parser = configparser.ConfigParser()
    parser.read(config_path)
    return parser.get(DB_PATH_HEADER, DB_PATH_SECTION, fallback="Dark")


def _set_db_path(path: str = 'calorie_app.db', config_path: str = CONFIG):
    parser = configparser.ConfigParser()
    parser[DB_PATH_HEADER] = {DB_PATH_SECTION: path}
    with open(config_path, 'w+') as fl:
        parser.write(fl)


def set_db_path_test(config_path: str = CONFIG) -> str:
    """Change the config.ini to have a test database path"""
    parser = configparser.ConfigParser()
    parser.read(config_path)
    path = f'test_{uuid.uuid4()}.db'
    _set_db_path(path)

    # --2-- registering the removal of the test database at the end of run
    def _at_exit(_path=path):
        os.remove(_path)
        _set_db_path(config_path=config_path)  # Set to default

    atexit.register(_at_exit)

    return path
