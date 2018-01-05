"""Manages Files."""

from .db_manager import DatabaseManager
import json


class Borg:
    """Borg singleton pattern."""
    _shared_state = {}

    def __init__(self):
        """Constructor."""
        self.__dict__ = self._shared_state


class FileManager(Borg):
    """Facade design pattern."""

    def __init__(self):
        """Constructor."""
        Borg.__init__(self)

    def add_file(self, name, category_name, desc="", tags=None):
        """Add new file."""
        with DatabaseManager() as db:
            db._setup()
            # insert or ignore if exists
            db.execute("INSERT OR IGNORE INTO categories(name) values(?)", (category_name,))

            cursor = db.execute("INSERT INTO files(name, category_name, desc) values(?, ?, ?)",
                                      (name, category_name, desc))
            letter_tag = category_name[0].lower()
            if tags:
                tags.append(letter_tag)
            else:
                tags = [letter_tag]
            self.insert_tags(db, tags, cursor.lastrowid)

    def rm_file(self, file_id):
        """Remove file."""
        with DatabaseManager() as db:
            db.execute("DELETE FROM files where id=?", (file_id,))

    def mod_file(self, file_id, name, category, description, tags):
        """Modify file."""
        with DatabaseManager() as db:
            cursor = db.execute("SELECT * FROM files where id=?", (file_id,))
            result = cursor.fetchone()

            if not name:
                name = result["name"]
            if not category:
                category = result["category_name"]
            if not description:
                description = result["desc"]
            if not tags:
                cur = db.execute("SELECT tag_name FROM file_tags WHERE file_id=?", (file_id,))
                tags = [t["tag_name"] for t in cur.fetchall()]
            letter_tag = category[0].lower()
            tags.append(letter_tag)

            sql_args = (name, category, description, file_id)

            db.execute("")
            # insert or ignore if exists
            db.execute("INSERT OR IGNORE INTO categories(name) values(?)", (category,))

            db.execute("UPDATE files SET name = ?, category_name = ?, desc = ? WHERE id = ?", sql_args)

            db.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))

            if tags:
                self.insert_tags(db, tags, file_id)

    @staticmethod
    def insert_tags(db, tags, file_id):
        """Handle new tag insertion."""
        tags_tuple_list = [(tag,) for tag in tags]
        # insert or ignore if exists
        db.executemany("INSERT OR IGNORE INTO tags values(?)", tags_tuple_list)

        for tag in tags:
            db.execute("INSERT INTO file_tags(file_id, tag_name) values(?, ?)", (file_id, tag.lower()))

    def find_file(self, name, category, description, tags):
        """Find files."""
        sql = """
            SELECT files.id, files.name, files.desc, files.category_name FROM files
            JOIN file_tags
                ON files.id=file_tags.file_id
        """
        args = []

        if name or category or tags or description:
            sql += " WHERE "
            multiple = False
            if name:
                if multiple:
                    sql += "AND "
                sql += "name LIKE ? "
                name = self.surround(name)
                args.append(name)
                multiple = True
            if description:
                if multiple:
                    sql += "AND "
                sql += "desc LIKE ? "
                description = self.surround(description)
                args.append(description)
                multiple = True
            if category:
                if multiple:
                    sql += "AND "
                sql += "category_name LIKE ? "
                category = self.surround(category)
                args.append(category)
                multiple = True
            if tags:
                if multiple:
                    sql += "AND "
                sql += "file_tags.tag_name REGEXP ? "
                tags = [tag.lower() for tag in tags]
                tags = '|'.join(tags)
                args.append(tags)

        sql += "GROUP BY files.id "

        dict_list = []
        with DatabaseManager() as db:
            cursor = db.execute(sql, tuple(args))
            for row in cursor.fetchall():
                dict_list.append(dict(row))

        return json.dumps(dict_list, indent=2)

    @staticmethod
    def surround(string, surround_text='%'):
        """Surround string with text."""
        return surround_text + string + surround_text

