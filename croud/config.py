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

import os
from argparse import Namespace

import yaml
from appdirs import user_config_dir
from schema import Schema, SchemaError

from croud.printer import print_error, print_format, print_info


class IncompatibleConfigException(Exception):
    pass


class Configuration:
    USER_CONFIG_DIR: str = user_config_dir("Crate")
    FILENAME: str = "croud.yaml"
    FILEPATH: str = f"{USER_CONFIG_DIR}/{FILENAME}"
    DEFAULT_CONFIG: dict = {
        "auth": {
            "current_context": "prod",
            "contexts": {
                "prod": {"token": ""},
                "dev": {"token": ""},
                "local": {"token": ""},
            },
        },
        "region": "bregenz.a1",
        "output_fmt": "table",
    }
    CONFIG_NAMES: dict = {
        "env": "Environment",
        "output_fmt": "Output format",
        "region": "Region",
    }

    @staticmethod
    def validate(config: dict) -> dict:
        schema = Schema(
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
        try:
            return schema.validate(config)
        except SchemaError:
            os.remove(Configuration.FILEPATH)
            create_default_config()

            return schema.validate(Configuration.DEFAULT_CONFIG)

    @staticmethod
    def create() -> None:
        if not os.path.exists(Configuration.USER_CONFIG_DIR):
            os.makedirs(Configuration.USER_CONFIG_DIR)

        if not os.path.isfile(Configuration.FILEPATH):
            create_default_config()
        else:
            load_config()

    @staticmethod
    def get_setting(setting: str) -> str:
        setting = setting.replace("-", "_")
        if setting == "env":
            return Configuration.get_env()
        return load_config()[setting]

    @staticmethod
    def get_env() -> str:
        config = load_config()
        return config["auth"]["current_context"]

    @staticmethod
    def set_context(env: str) -> None:
        config = load_config()
        config["auth"]["current_context"] = env
        write_config(config)

    @staticmethod
    def get_token(env: str) -> str:
        config = load_config()
        return config["auth"]["contexts"][env].get("token", "")

    @staticmethod
    def set_token(token: str, env: str) -> None:
        config = load_config()
        config["auth"]["contexts"][env]["token"] = token
        write_config(config)


def create_default_config() -> None:
    write_config(Configuration.DEFAULT_CONFIG)
    os.chmod(Configuration.FILEPATH, 0o600)


def load_config() -> dict:
    with open(Configuration.FILEPATH, "r") as f:
        config = yaml.safe_load(f)

    try:
        return Configuration.validate(config)
    except IncompatibleConfigException as e:
        print_error(str(e))
        exit(1)


def set_property(property: str, value: str):
    config = load_config()
    config[property] = value
    write_config(config)


def write_config(config: dict) -> None:
    with open(Configuration.FILEPATH, "w", encoding="utf8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def config_get(args: Namespace):
    """
    Gets a default configuration setting
    """

    fmt = Configuration.get_setting("output_fmt")
    value = Configuration.get_setting(args.get)
    print_format([{args.get: value}], args.output_fmt or fmt)


def config_set(args: Namespace, parser=None):
    """
    Sets a default configuration setting
    """
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
