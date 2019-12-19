# Licensed to CRATE Technology GmbH ("Crate") under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  Crate licenses
# this file to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
# However, if you have executed another commercial license agreement
# with Crate these terms will supersede the license and you may use the
# software solely pursuant to the terms of the relevant commercial agreement.

import copy
import difflib
import re
import uuid
from doctest import _ellipsis_match  # type: ignore
from functools import partial
from typing import Dict

from croud.__main__ import get_parser
from croud.api import RequestMethod

normalize = partial(re.sub, r"\s+", "")

UNDEFINED = object()


def ndiff(actual: str, expected: str) -> str:
    engine = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
    diff = list(engine.compare(expected.splitlines(True), actual.splitlines(True)))
    return "\n".join(line.rstrip() for line in diff)


def assert_ellipsis_match(actual: str, expected: str) -> None:
    diff = ndiff(expected.strip(), actual.strip())
    equality = _ellipsis_match(normalize(expected.strip()), normalize(actual.strip()))
    assert equality, diff


class MockConfig:
    """
    A mocked configuration which emulates reading and writing file from/to disk.
    """

    def __init__(self, config: Dict) -> None:
        self.conf = copy.deepcopy(config)

    def read_config(self) -> Dict:
        return self.conf

    def write_config(self, config) -> None:
        self.conf = config


def call_command(*argv):
    parser = get_parser()
    args = parser.parse_args(argv[1:])
    if "resolver" in args:
        fn = args.resolver
        del args.resolver
        fn(args)
    else:
        parser.print_help()


def assert_rest(
    mock_request, method: RequestMethod, endpoint, *, params=None, body=None
):
    args = [method, endpoint]
    kwargs = {}
    if method != RequestMethod.GET and body is not UNDEFINED:
        kwargs["body"] = body
    if params is not UNDEFINED:
        kwargs["params"] = params

    mock_request.assert_called_once_with(*args, **kwargs)


def gen_uuid():
    return str(uuid.uuid4())
