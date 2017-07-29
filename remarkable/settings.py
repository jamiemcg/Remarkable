import collections
import os

class Settings(collections.MutableMapping):
    """The Remarkable Settings class"""

    def __init__(self, *args, **kwargs):
        self.homeDir = os.environ['HOME']
        self.path = os.path.join(self.homeDir, ".remarkable/")
        self.settings_path = os.path.join(self.path, "remarkable.settings")

        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys
        self.load_from_file()

    def load_from_file(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if os.path.isfile(self.settings_path):
            settings_file = open(self.settings_path)
            s = eval(settings_file.read())
            self.store.update(s)
            settings_file.close()

    def write(self):
            settings_file = open(self.settings_path, 'w')
            settings_file.write(str(self.store))
            settings_file.close()

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key


_settings = Settings({ 'css': '',
                   'font': "Sans 10",
                   'line-numbers': True,
                   'live-preview': True,
                   'nightmode': False,
                   'statusbar': True,
                   'style': "github",
                   'toolbar': True,
                   'vertical': False,
                   'word-wrap': True,
                   })

def get_settings():
    return _settings
