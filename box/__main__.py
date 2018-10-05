"""Main module."""

from command_ui import CommandUI


if __name__ == '__main__':
    com = CommandUI()
    com.parse_args()
