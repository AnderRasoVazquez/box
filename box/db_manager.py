"""Database manager."""

import sqlite3
import re

from .config import ConfigManager


def regexp(expr, item):
    """For using REGEXP in sqlite."""
    reg = re.compile(expr)
    return reg.search(item) is not None


class Borg:
    """Borg singleton pattern."""
    _shared_state = {}

    def __init__(self):
        """Constructor."""
        self.__dict__ = self._shared_state


class DatabaseManager(Borg):
    """This class manages an Sqlite database."""

    def __init__(self):
        """Constructor."""
        Borg.__init__(self)
        self._db = None
        self._config = ConfigManager()
        self._db_path = self._config.database_path

    def __enter__(self):
        """Connect to database."""
        self.connect(self._db_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close connection to database."""
        self.close()

    def connect(self, path):
        """Connect to database."""
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.create_function("REGEXP", 2, regexp)
        self._db.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Commit and close connection."""
        if self._db:
            self._db.commit()
            self._db.close()

    def execute(self, sql, args=None):
        """Execute sql statement"""
        if not args:
            return self._db.execute(sql)
        else:
            return self._db.execute(sql, args)

    def executemany(self, sql, args):
        """Execute multiple sql statements"""
        self._db.executemany(sql, args)

    def _setup(self):
        self._db.execute("""
            CREATE TABLE if not exists categories (
                name TEXT PRIMARY KEY NOT NULL
            );
        """)
        self._db.execute("""
            CREATE TABLE if not exists tags (
                name TEXT PRIMARY KEY NOT NULL
            );
        """)
        self._db.execute("""
            CREATE TABLE if not exists files (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT NOT NULL,
                desc TEXT,
                category_name TEXT NOT NULL,
                
                FOREIGN KEY(category_name)
                    REFERENCES categories(name)
            );
        """)
        self._db.execute("""
            CREATE TABLE if not exists file_tags (
                file_id INTEGER NOT NULL,
                tag_name TEXT NOT NULL,
                
                PRIMARY KEY(file_id, tag_name),
                
                FOREIGN KEY(file_id)
                    REFERENCES files(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(tag_name)
                    REFERENCES tags(name)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );
        """)

    def _reset_db(self):
        self._db.execute("DROP TABLE if exists file_tags")
        self._db.execute("DROP TABLE if exists files")
        self._db.execute("DROP TABLE if exists categories")
        self._db.execute("DROP TABLE if exists tags")
        self._setup()

    def dump(self):
        """Return a string with database contents."""
        result = ""
        for line in self._db.iterdump():
            result += line + "\n"
        return result


