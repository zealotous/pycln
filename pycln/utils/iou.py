"""Pycln file IO utility."""
import os
import tokenize
from pathlib import Path
from typing import Union, Tuple, List

from ._exceptions import (
    ReadPermissionError,
    WritePermissionError,
    UnparsableFile,
)


def safe_read(
    path: Union[Path, str], permissions: tuple = (os.R_OK, os.W_OK)
) -> Tuple[str, str]:
    """Read file content with encode detecting support.

    :param path: `.py` file path.
    :returns: decoded source code and file encoding.
    :raises ReadPermissionError: when `os.R_OK` in permissions
        and the source does not have read permission.
    :raises WritePermissionError: when `os.W_OK` in permissions
        and the source does not have write permission.
    :raises UnparsableFile: If both a BOM and a cookie are present, but disagree.
    """
    # Check these permissions before openinig the file.
    for permission in permissions:
        if not os.access(path, permission):
            if permission is os.R_OK:
                raise ReadPermissionError(13, "Permission denied [READ]", path)
            elif permission is os.W_OK:
                raise WritePermissionError(13, "Permission denied [WRITE]", path)
    try:
        with tokenize.open(path) as stream:
            source_code = stream.read()
            encoding = stream.encoding
        return source_code, encoding
    except SyntaxError as err:
        raise UnparsableFile(path, err)


def safe_write(path: Union[Path, str], fixed_lines: List[str], encoding: str) -> None:
    """Write file content based on given `encoding`.

    :param path: `.py` file path.
    :param encoding: file encoding.
    :param fixed_lines: fixed source code lines.
    :raises WritePermissionError: when `os.W_OK` in permissions
        and the source does not have write permission.
    """
    if not os.access(path, os.W_OK):
        raise WritePermissionError(13, "Permission denied [WRITE]", path)
    with open(path, mode="w", encoding=encoding) as destination:
        destination.writelines(fixed_lines)
