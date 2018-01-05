"""Utility functions."""

from os import makedirs
from os.path import isdir


def col_max_len(d_list, k):
    """Return max len of a column of a """
    len_list = [len(str(d[k])) for d in d_list]
    len_list.append(len(str(k)))
    return max(len_list)


def format_dict_list(d_list, padding=4, separator=True, separator_char="-"):
    """Create a table from a list of dictionaries."""
    max_len = {k: col_max_len(d_list, k) for k in d_list[0].keys()}

    title = ""
    for key in d_list[0].keys():
        title += "{key:{v_len}s}".format(key=key, v_len=max_len[key] + padding)
    title += "\n"

    separator = (separator_char * len(title)) + "\n"

    body = ""
    for d in d_list:
        for key in d.keys():
            body += "{value:{v_len}s}".format(value=str(d[key]), v_len=max_len[key] + padding)
        body += "\n"

    if separator:
        result = title + separator + body
    else:
        result = title + body

    return result


def mkdir_if_not_exists(folder, verbose_mode=False):
    """Create a folder if not exists."""
    if not isdir(folder):
        makedirs(folder)
        if verbose_mode:
            print("Created {}".format(folder))
