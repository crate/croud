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

import re
from argparse import Namespace
from functools import partial

from croud.config.configuration import (  # mark for IDEs as "private"
    Configuration as _Configuration,
)

SENSITIVE_KEYS = re.compile("pass|secret|token", flags=re.IGNORECASE)
_CONFIG = None


def _get_config(filename: str) -> _Configuration:
    """
    Lazily instantiate and return the module level ``_CONFIG`` object.

    This method is used as a getter, to make sure there is only a single
    instance of the globally used configuration.
    """
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _Configuration(filename)
    return _CONFIG


class WeakConfigProxy:
    """
    A proxy class for the global Configuration instance.

    By providing a getter method for the proxied object, the proxied object may
    be replaced without the proxy knowing it, due to the nature of the weak
    coupling.
    """

    def __init__(self, getter, *args, **kwargs):
        super().__setattr__("_get", partial(getter, *args, **kwargs))

    def __repr__(self):
        return repr(self._get())

    def __getattr__(self, name):
        return getattr(self._get(), name)

    def __setattr__(self, name, value):
        raise AttributeError("Cannot set attributes on proxy object")


# The global Configuration object
CONFIG = WeakConfigProxy(_get_config, "croud.yaml")


# This method should rather be in the `croud.config.util` module,
# however, because it depends on `CONFIG`, an import of `CONFIG`
# inside the `util` module would sooner or later result in a circular
# import.
def get_output_format(args: Namespace) -> str:
    """
    Get the output format for the response.

    The fallback chain is as follows:

    1. --output-fmt FORMAT
    2. format of current profile
    3. default format
    """
    return args.output_fmt if args.output_fmt is not None else CONFIG.format
