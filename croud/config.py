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

from croud.printer import (
    PRINTERS,
    print_error,
    print_format,
    print_info,
    print_success,
    print_warning,
)

DEFAULT_CONFIG: dict = {
    "current-profile": "prod",
    "global": {"region": "", "output-format": "table", "organization": ""},
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


class ConfigError(ValueError):
    pass


class InvalidProfile(ConfigError):
    pass


class InvalidConfigOption(ConfigError):
    pass


class InvalidConfigValue(ConfigError):
    pass


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

    @property
    def current_profile(self) -> str:
        return self._config["current-profile"] or "prod"

    @current_profile.setter
    def current_profile(self, value):
        if value not in DEFAULT_CONFIG["profile"]:
            allowed = ", ".join(DEFAULT_CONFIG["profile"])
            raise InvalidProfile(
                f"'{value}' is not a valid configuration profile. "
                f"Allowed profiles are {allowed}."
            )

        self._config["current-profile"] = value

    def get_global(self, key) -> str:
        if key not in DEFAULT_CONFIG["global"]:
            allowed = ", ".join(DEFAULT_CONFIG["global"])
            raise InvalidConfigOption(
                f"'{key}' is not a valid global configuration option. "
                f"Allowed values are {allowed}."
            )

        return self._config["global"].get(key)

    def set_global(self, key, value):
        if key not in DEFAULT_CONFIG["global"]:
            allowed = ", ".join(DEFAULT_CONFIG["global"])
            raise InvalidConfigOption(
                f"'{key}' is not a valid global configuration option. "
                f"Allowed values are {allowed}."
            )

        if key == "output-format" and value not in PRINTERS:
            allowed = ", ".join(PRINTERS)
            raise InvalidConfigValue(
                f"'{value}' is not a valid configuration value for 'output-format'. "
                f"Allowed values are {allowed}."
            )

        self._config["global"][key] = value

    def get_profile(self, key, profile=None) -> str:
        if profile is None:
            profile = self.current_profile

        if profile not in DEFAULT_CONFIG["profile"]:
            allowed = ", ".join(DEFAULT_CONFIG["profile"])
            raise InvalidProfile(
                f"'{profile}' is not a valid configuration profile. "
                f"Allowed profiles are {allowed}."
            )

        if key not in DEFAULT_CONFIG["profile"][profile]:
            allowed = ", ".join(DEFAULT_CONFIG["profile"][profile])
            raise InvalidConfigOption(
                f"'{key}' is not a valid configuration option for profile '{profile}'. "
                f"Allowed values are {allowed}."
            )

        return self._config["profile"][profile].get(key) or self.get_global(key)

    def set_profile(self, key, value, profile=None):
        if profile is None:
            profile = self.current_profile

        if profile not in DEFAULT_CONFIG["profile"]:
            allowed = ", ".join(DEFAULT_CONFIG["profile"])
            raise InvalidProfile(
                f"'{profile}' is not a valid configuration profile. "
                f"Allowed profiles are {allowed}."
            )

        if key not in DEFAULT_CONFIG["profile"][profile]:
            allowed = ", ".join(DEFAULT_CONFIG["profile"][profile])
            raise InvalidConfigOption(
                f"'{key}' is not a valid configuration option for profile '{profile}'. "
                f"Allowed values are {allowed}."
            )

        if key == "output-format" and value not in PRINTERS:
            allowed = ", ".join(PRINTERS)
            raise InvalidConfigValue(
                f"'{value}' is not a valid configuration value for 'output-format'. "
                f"Allowed values are {allowed}."
            )

        self._config["profile"][profile][key] = value


def config_current_profile(args: Namespace, config: Configuration):
    """Set or switches the default profile."""
    key = "current_profile"
    print_format([{key: config.current_profile}], config.get_global("output-format"))


def config_use_profile(args: Namespace, config: Configuration):
    """Print the default profile."""
    try:
        config.current_profile = args.use_profile
    except ConfigError as e:
        print_error(str(e))
    else:
        config.save()
        print_success(f"Default profile switched to '{args.use_profile}'.")


def config_get_global(args: Namespace, config: Configuration):
    try:
        data = [
            {"option": option, "value": config.get_global(option)}
            for option in args.options
        ]
    except ConfigError as e:
        print_error(str(e))
    else:
        print_format(data, config.get_profile("output-format"))


def config_set_global(args: Namespace, config: Configuration):
    options = {}
    for option in args.options:
        param = option.split("=", 1)
        if len(param) == 1:
            print_error(f"Invalid option '{option}'")
        else:
            options[param[0]] = param[1]

    try:
        queued_messages = []
        for option, value in options.items():
            config.set_global(option, value)
            queued_messages.append(f"Set '{option}' to '{value}'")
    except ConfigError as e:
        print_error(str(e))
    else:
        for m in queued_messages:
            print_info(m)
        config.save()


def config_get_profile(args: Namespace, config: Configuration):
    try:
        data = [
            {
                "option": option,
                "value": config.get_profile(option, profile=args.profile),
            }
            for option in args.options
        ]
    except ConfigError as e:
        print_error(str(e))
    else:
        print_format(data, config.get_profile("output-format"))


def config_set_profile(args: Namespace, config: Configuration):
    options = {}
    for option in args.options:
        param = option.split("=", 1)
        if len(param) == 1:
            print_error(f"Invalid option '{option}'")
        else:
            options[param[0]] = param[1]

    try:
        queued_messages = []
        for option, value in options.items():
            config.set_profile(option, value, profile=args.profile)
            queued_messages.append(f"Set '{option}' to '{value}'")
    except ConfigError as e:
        print_error(str(e))
    else:
        for m in queued_messages:
            print_info(m)
        config.save()


def config_get(args: Namespace, config: Configuration):
    """
    Gets a default configuration setting
    """
    print_warning(
        "This command is deprecated. Please use `croud config get-profile` "
        "or `croud config get-global` instead."
    )

    fmt = args.output_fmt or config.get_profile("output-format")
    key = args.get
    if key == "output-fmt":
        print_warning(
            "The configuration setting 'output-fmt' was renamed to 'output-format'."
        )
        value = config.get_profile("output-format")
    elif key == "env":
        print_warning(
            "Environments (envs) were renamed to profiles. To get the current "
            "environment use `croud config current-profile`."
        )
        value = config.current_profile
    else:
        value = config.get_profile(key)

    print_format([{key: value}], args.output_fmt or fmt)


def config_set(args: Namespace, parser, config: Configuration):
    """
    Sets a default configuration setting
    """
    print_warning(
        "This command is deprecated. Please use `croud config set-profile` "
        "or `croud config set-global` instead."
    )

    if parser and all(val is None for val in vars(args).values()):
        parser.print_help()
        return

    for key in vars(args):
        setting = getattr(args, key)

        if setting is not None:
            if key == "env":
                print_warning(
                    "Environments (envs) were renamed to profiles. To set or change "
                    "the default profile use `croud config use-profile`."
                )
                config.current_profile = setting
                print_info(f"Environment switched to {setting}")
            elif key == "output-fmt":
                print_warning(
                    "The configuration setting 'output-fmt' was renamed to "
                    "'output-format'."
                )
                config.set_profile("output-format", setting)
                config.set_global("output-format", setting)
            else:
                config.set_profile(key, setting)
                config.set_global(key, setting)
                print_info(f"output-fmt switched to {setting}")

    config.save()
