#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
#
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

import argh
import colorama
import pkg_resources

from croud import __version__
from croud.config import Configuration


def main():
    Configuration.create()
    colorama.init()

    p = argh.ArghParser(prog="CROUD")
    p.add_argument("--version", action="version", version="%(prog)s " + __version__)
    commands = [
        entry_point.load()
        for entry_point in pkg_resources.iter_entry_points("croud_commands")
    ]
    p.add_commands(commands)
    p.dispatch()


if __name__ == "__main__":
    main()
