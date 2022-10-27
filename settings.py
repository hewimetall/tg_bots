from configparser import ConfigParser
from pathlib import PurePath

class IniConfigParser(ConfigParser):
    def __getattr__(self, item):
        return self[item]

def parser_ini(filename)->ConfigParser:
    cp = IniConfigParser()
    cp.read(filename)
    return cp

class Setting(object):
    """
    Класс для загрузки настроек из ini файлов
    """

    # Возвращяем путь до директории
    @property
    def path(self) -> str:
        return "/".join(__file__.split('/')[:-1]) + "/conf"

    def _get_setting(self):
        for name, re_path in self.conf.defaults().items():
            # В случае если указаны абсолютные пути
            path = PurePath(self.path, re_path)
            self.config[name] = parser_ini(path)

    @property
    def keyboard(self) -> ConfigParser:
        return self.config['keyboards']

    @property
    def commands(self) -> ConfigParser:
        return self.config['cmd']

    def __init__(self, filename = None):
        if not filename:
            filename = self.path + '/settings.ini'
        self.conf = parser_ini(filename)
        self.filename = filename
        self.config = {}
        self._get_setting()
