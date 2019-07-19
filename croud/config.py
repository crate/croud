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
from argparse import Namespace
from pathlib import Path
from typing import Optional

import yaml
from appdirs import user_config_dir
from schema import Schema, SchemaError

from croud.printer import print_format, print_info, print_warning

DEFAULT_CONFIG = {
    "current-profile": "prod",
    "global": {"region": "", "output-format": "", "organization": ""},
    "profile": {
        "prod": {"token": "", "region": "", "output-format": "", "organization": ""},
        "dev": {"token": "", "region": "", "output-format": "", "organization": ""},
        "local": {"token": "", "region": "", "output-format": "", "organization": ""},
    },
}
DEFAULT_CONFIG_SCHEMA = Schema(
    {
        "current-profile": str,
        "global": {"region": str, "output-format": str, "organization": str},
        "profile": {
            "prod": {
                "token": str,
                "region": str,
                "output-format": str,
                "organization": str,
            },
            "dev": {
                "token": str,
                "region": str,
                "output-format": str,
                "organization": str,
            },
            "local": {
                "token": str,
                "region": str,
                "output-format": str,
                "organization": str,
            },
        },
    }
)
OLD_CONFIG_SCHEMA = Schema(
    {
        "auth": {
            "current_context": str,
            "contexts": {
                "prod": {"token": str},
                "dev": {"token": str},
                "local": {"token": str},
            },
        },
        "region": str,
        "output_fmt": str,
    }
)


class Configuration:
    CONFIG_NAMES: dict = {
        "env": "Environment",
        "output_fmt": "Output format",
        "region": "Region",
    }

    _path: Path
    _config: dict

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = Path(user_config_dir("Crate")) / "croud.yaml"
        self._path = path

    def load(self):
        if self._path.exists:
            with self._path.open("r") as f:
                self._config = yaml.safe_load(f)
            self._validate()
        else:
            self._config = copy.deepcopy(DEFAULT_CONFIG)
        return self

    def save(self) -> None:
        self._path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with self._path.open("w") as f:
            self._path.chmod(0o600)
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def _validate(self):
        try:
            DEFAULT_CONFIG_SCHEMA.validate(self._config)
        except SchemaError:
            try:
                self._config = self._load_old_config(self._config)
            except SchemaError:
                self._config = copy.deepcopy(DEFAULT_CONFIG)
            self.save()

    def _load_old_config(self, config: dict):
        OLD_CONFIG_SCHEMA.validate(config)
        new_config: dict = copy.deepcopy(DEFAULT_CONFIG)
        # fmt: off
        new_config["current-profile"] = config["auth"]["current_context"]
        new_config["global"]["region"] = config["region"]
        new_config["global"]["output-format"] = config["output_fmt"]
        new_config["profile"]["prod"]["token"] = config["auth"]["contexts"]["prod"]["token"]  # noqa
        new_config["profile"]["dev"]["token"] = config["auth"]["contexts"]["dev"]["token"]  # noqa
        new_config["profile"]["local"]["token"] = config["auth"]["contexts"]["local"]["token"]  # noqa
        # fmt: on
        return new_config

    def get_current_profile(self) -> str:
        return self._config["current-profile"]

    def set_current_profile(self, value):
        self._config["current-profile"] = value

    def get_global(self, key) -> str:
        return self._config["global"].get(key)

    def set_global(self, key, value):
        self._config["global"][key] = value

    def get_profile(self, profile, key) -> str:
        if profile not in self._config:
            self._config[profile] = {}
        return self._config[profile].get(key) or self.get_global(key)

    def set_profile(self, profile, key, value):
        if profile not in self._config:
            self._config[profile] = {}
        self._config[profile][key] = value


def config_get(args: Namespace, config: Configuration):
    """
    Gets a default configuration setting
    """
    print_warning(
        "This command is deprecated. Please use `croud config get-profile` "
        "or `croud config get-global` instead."
    )

    context

    fmt = Configuration.get_setting("output_fmt")
    value = Configuration.get_setting(args.get)
    print_format([{args.get: value}], args.output_fmt or fmt)


def config_set(args: Namespace, parser=None):
    """
    Sets a default configuration setting
    """
    print_warning(
        "This command is deprecated. Please use `croud config get-profile` "
        "or `croud config get-global` instead."
    )

    if parser and all(val is None for val in vars(args).values()):
        parser.print_help()
        return

    for key in vars(args):
        setting = getattr(args, key)

        if setting is not None:
            if key == "env":
                Configuration.set_context(setting)
                print_info(f"Environment switched to {setting}")
            else:
                set_property(key, setting)
                print_info(f"{Configuration.CONFIG_NAMES[key]} switched to {setting}")
