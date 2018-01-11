"""Command line user interface."""

import argparse
import json

from .facade import Facade
from .utilities import format_dict_list
from .config import ConfigManager


class CommandUI(object):
    """Handles commands."""

    def __init__(self):
        """Constructor."""
        self._parser = self._build_parser()
        self._facade = Facade()
        self._config = ConfigManager()

    @staticmethod
    def _build_parser():
        """Build parser."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help='commands', dest='command')

        parser_add = subparsers.add_parser('add', help='add a new file')
        parser_add.add_argument('name',
                                nargs='+',
                                help='file name')
        parser_add.add_argument('-c', '--category',
                                type=str,
                                required=True,
                                help='file\'s category')
        parser_add.add_argument('-d', '--description',
                                nargs='+',
                                help='file\'s extended description')
        parser_add.add_argument('-t', '--tags',
                                type=str,
                                nargs='+',
                                help='file\'s tags')

        parser_rm = subparsers.add_parser('rm', help='rm a file')
        parser_rm.add_argument('file_id',
                               type=int,
                               help='file id')

        parser_mod = subparsers.add_parser('mod', help='modify a file')
        parser_mod.add_argument('file_id',
                                type=int,
                                help='file id')
        parser_mod.add_argument('-n', '--name',
                                nargs='+',
                                help='file name')
        parser_mod.add_argument('-c', '--category',
                                type=str,
                                help='file\'s category')
        parser_mod.add_argument('-d', '--description',
                                nargs='+',
                                help='file\'s extended description')
        parser_mod.add_argument('-t', '--tags',
                                type=str,
                                nargs='+',
                                help='file\'s tags')

        parser_sql = subparsers.add_parser('sql', help='type custom sql')
        parser_sql.add_argument('sql',
                                type=str,
                                help='sql query')
        parser_sql.add_argument('-s', '--select',
                                action="store_true",
                                help='is a select query')

        parser_find = subparsers.add_parser('find', help='find files')
        parser_find.add_argument('-n', '--name',
                                 nargs='+',
                                 help='file name')
        parser_find.add_argument('-c', '--category',
                                 type=str,
                                 help='file\'s category')
        parser_find.add_argument('-d', '--description',
                                 nargs='+',
                                 help='file\'s extended description')
        parser_find.add_argument('-t', '--tags',
                                 type=str,
                                 nargs='+',
                                 help='file\'s tags')
        parser_find.add_argument('-j', '--json',
                                 action="store_true",
                                 help='export json')

        subparsers.add_parser('init', help='initial db setup')

        parser_show = subparsers.add_parser('show', help='show file info')
        parser_show.add_argument('file_id',
                                 type=int,
                                 help='file id')

        return parser

    def test_parser(self, test_args=None):
        """Test parser."""
        args = self._control(self._parser.parse_args(args=test_args))
        return args

    def parse_args(self):
        """Call Facades function based on args.."""
        args = self._control(self._parser.parse_args())
        if args.command == "add":
            self._facade.add_file(args.name, args.category,
                                  args.description, args.tags)
        elif args.command == "rm":
            self._facade.rm_file(args.file_id)
        elif args.command == "mod":
            optional_args = [args.name, args.category,
                             args.description, args.tags]
            if all(v is None for v in optional_args):
                exit("ERROR: provide at least one argument to modify.")
            else:
                self._facade.mod_file(args.file_id, args.name,
                                      args.category, args.description,
                                      args.tags)
        elif args.command == "sql":
            result = self._facade.execute(args.sql, args.select)
            if result:
                rst_json = json.loads(result)
                print(format_dict_list(rst_json))
        elif args.command == "find":
            result = self._facade.find_file(args.name, args.category,
                                            args.description, args.tags)
            if args.json:
                print(result)
            else:
                rst_json = json.loads(result)
                if rst_json:
                    print(format_dict_list(rst_json))
                else:
                    exit("No results.")
        elif args.command == "init":
            if self._facade.init():
                print("Database created in: " + self._config.database_path)
            else:
                exit("Database already exists in: " +
                     self._config.database_path)
        elif args.command == "show":
            result = self._facade.get_info(args.file_id)
            rst_json = json.loads(result)
            if rst_json:
                for key in rst_json:
                    print("{}: {}".format(key, rst_json[key]))
            else:
                exit("File with id {} doesn't exist.".format(args.file_id))

    def _control(self, args):
        """Parse lists to strings.

        With this we don't have to surround arguments in quotes.
        This:
        box add file long name -c something -d this is a description
        Instead of:
        box add "long name" -c something -d "this is a description"
        """
        if args.command in ["add", "mod", "find"]:
            if args.name:
                args.name = " ".join(args.name)
            if args.description:
                args.description = " ".join(args.description)
        return args
