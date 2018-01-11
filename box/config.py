"""Config related class."""

import configparser


class Borg:
    """Borg singleton pattern."""
    _shared_state = {}

    def __init__(self):
        """Constructor."""
        self.__dict__ = self._shared_state


class ConfigManager(Borg):
    """Manages app configuration."""

    def __init__(self):
        """Constructor."""
        Borg.__init__(self)
        self._parser = configparser.ConfigParser()
        # TODO recoger bien la BD, con un try catch
        self._parser.read("/home/ander/.boxrc")
        self.database_folder = self._load_db_folder()
        self.database_name = self._load_db_name()
        self.database_path = self.database_folder + self.database_name

    def _load_db_folder(self):
        """Load database path."""
        return self._parser["DEFAULT"]["database_folder"]

    def _load_db_name(self):
        """Load database path."""
        return self._parser["DEFAULT"]["database_name"]
