# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2019-2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import enum
import json
import linecache
import re
import urllib.parse
import sys
from flask import current_app as app


def to_pretty_json(value):
    """
    Convert a Python data structure to a formatted JSON string.
    Args:
        value: Any valid Python data structure to be converted to JSON.
    Returns:
        str: A pretty-printed JSON string.
    """
    return json.dumps(value, sort_keys=True, indent=4, separators=(",", ": "))


def enum_to_string(obj):
    """
    Convert an Enum member to its string representation (name).
    Args:
        obj: An object that may be an Enum member or any other type.
    Returns:
        str or obj: If `obj` is an Enum member, its name (a string) is returned.
                    If `obj` is not an Enum member, `obj` is returned unchanged.
    """
    if isinstance(obj, enum.Enum):
        return obj.name
    return obj


def str2bool(s):
    """
    Convert a string representation of a boolean to a boolean value.
    Args:
        s (str): A string representing a boolean value.
    Returns:
        bool: True if 's' represents a truthy value, False otherwise.
    """
    return s.lower() in ["yes", "1", "true"]


def python_eval(obj):
    """
    Safely evaluate a Python expression from a string.
    Args:
        obj: A string containing a Python expression to be evaluated.
    Returns:
        Any: If `obj` is a valid Python expression, the result of the evaluation is
             returned. If there is an error during evaluation, `obj` is returned
             unchanged.
    Example:
        result = python_eval("3 + 4")
        print(result)  # Output: 7

        invalid_expr = "3 / 0"
        result = python_eval(invalid_expr)
        print(result)  # Output: "3 / 0" (no division by zero error)
    """
    if isinstance(obj, str):
        try:
            return eval(obj)
        except Exception as e:
            app.logger.warn("Error calling python_eval(): {}".format(e))
    return obj


def intersect(a, b):
    """
    Compute the intersection of two iterables.
    Args:
        a (iterable): The first iterable.
        b (iterable): The second iterable.
    Returns:
        set: A set containing elements that are present in both 'a' and 'b'.
    """
    return set(a).intersection(b)


def xstr(s):
    """
    Convert a value to a string or return an empty string if the value is None.
    Args:
        s: Any value that can be converted to a string.
    Returns:
        str: A string representation of 's' if 's' is not None, or an empty string.
    """
    return "" if s is None else str(s)


def nnstr(s):
    """
    Convert a value to a string or return an empty string if the value is None or empty.
    Args:
        s: Any value that can be converted to a string.
    Returns:
        str: A string representation of 's' if 's' is not None and not an empty string,
             or an empty string.
    """
    return "" if (s is None or s == "") else str(s)


def logexception(err):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    app.logger.error(
        '{} at ({}, LINE {} "{}"): {}'.format(err, filename, lineno, line.strip(), exc_obj)
    )


def url_path_join(
        base_url,
        *paths
):
    """
       Parse and join url parts into a well-formed URL.
       Args:
           base_url (str): The base URL to join.
           *paths (str,): Parts of the path to join.
       Returns:
           str: A well-formed URL.
    """
    parsed_url = urllib.parse.urlsplit(base_url)
    base_path = re.sub('/+', '/', parsed_url.path)
    if paths:
        if len(base_path) and base_path[-1] != '/':
            base_path += '/'
        for path in paths[:-1]:
            path = re.sub('/+', '/', path).lstrip('/') + '/'
            base_path = urllib.parse.urljoin(base_path, path)
        path = paths[-1]
        path = re.sub('/+', '/', path).lstrip('/')
        base_path = urllib.parse.urljoin(base_path, path)
    return urllib.parse.urlunsplit(parsed_url._replace(path=base_path))
