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

import sys
from argparse import Namespace

from croud.config import CONFIG, get_output_format
from croud.config.configuration import InvalidProfile
from croud.config.util import clean_dict
from croud.printer import print_error, print_format, print_info


def config_add_profile(args: Namespace) -> None:
    kwargs = {}
    if args.format:
        kwargs["format"] = args.format
    if args.region:
        kwargs["region"] = args.region
    try:
        CONFIG.add_profile(args.profile, endpoint=args.endpoint, **kwargs)
    except InvalidProfile:
        print_error(f"Failed to add profile '{args.profile}'.")
        sys.exit(1)
    else:
        print_info(f"Added profile '{args.profile}'.")


def config_current_profile(args: Namespace) -> None:
    result = {
        "name": CONFIG.name,
        "endpoint": CONFIG.endpoint,
        "format": CONFIG.format,
    }
    print_format(result, get_output_format(args))


def config_remove_profile(args: Namespace) -> None:
    try:
        CONFIG.remove_profile(args.profile)
    except InvalidProfile:
        print_error(f"Failed to remove profile '{args.profile}'.")
        print_info("Make sure the profile exists and it is not the current profile.")
        sys.exit(1)
    else:
        print_info(f"Removed profile '{args.profile}'.")


def config_set_profile(args: Namespace) -> None:
    try:
        CONFIG.use_profile(args.profile)
    except InvalidProfile:
        print_error(f"Failed to switch to profile '{args.profile}'.")
        print_info("Make sure the profile exists.")
        sys.exit(1)
    else:
        print_info(f"Switched to profile '{args.profile}'.")


def config_show(args: Namespace) -> None:
    print_info(f"Configuration file {CONFIG._file_path}")
    print_format(clean_dict(CONFIG.config), "yaml")
