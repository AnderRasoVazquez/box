"""Facade design pattern."""

import json

from os.path import isfile

from .db_manager import DatabaseManager
from .file_manager import FileManager
from .config import ConfigManager
from .utilities import mkdir_if_not_exists


class Borg:
    """Borg singleton pattern."""
    _shared_state = {}

    def __init__(self):
        """Constructor."""
        self.__dict__ = self._shared_state


class Facade(Borg):
    """Facade design pattern."""

    def __init__(self):
        """Constructor."""
        Borg.__init__(self)
        self.file_manager = FileManager()
        self._config = ConfigManager()

    def add_file(self, name, category_name, desc=None, tags=None):
        """Add a new file."""
        self._exit_if_not_db()
        self.file_manager.add_file(name, category_name, desc, tags)

    def rm_file(self, file_id):
        """Remove a file."""
        self._exit_if_not_db()
        self.file_manager.rm_file(file_id)

    def mod_file(self, file_id, name, category, description, tags):
        """Modify file."""
        self._exit_if_not_db()
        self.file_manager.mod_file(file_id, name, category, description, tags)

    def execute(self, sql, select):
        """Execute query."""
        self._exit_if_not_db()
        with DatabaseManager() as db:
            cursor = db.execute(sql)
            if select:
                dict_list = []
                for row in cursor.fetchall():
                    dict_list.append(dict(row))

                return json.dumps(dict_list, indent=2)
            return None

    def find_file(self, name, category, description, tags):
        """Find files."""
        self._exit_if_not_db()
        return self.file_manager.find_file(name, category, description, tags)

    def init(self):
        """Initialize database"""
        if not isfile(self._config.database_path):
            mkdir_if_not_exists(self._config.database_folder)
            with DatabaseManager() as db:
                db._setup()
            return True
        return False

    def dump_database(self):
        """Dump database contents."""
        with DatabaseManager() as db:
            return db.dump()

    def _exit_if_not_db(self):
        """Exit if not DB."""
        if not isfile(self._config.database_path):
            exit("Database not found, try to use the command: \n$ box init")

    def get_info(self, file_id):
        """Find files."""
        return self.file_manager.get_info(file_id)

