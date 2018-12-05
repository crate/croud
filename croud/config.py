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

import yaml
from appdirs import user_config_dir
from schema import Schema, SchemaError

from croud.printer import print_error


class IncompatibleConfigException(Exception):
    pass


class Configuration:
    USER_CONFIG_DIR: str = user_config_dir("Crate")
    FILENAME: str = "croud.yaml"
    FILEPATH: str = f"{USER_CONFIG_DIR}/{FILENAME}"
    DEFAULT_CONFIG: dict = {
        "auth": {
            "current_context": "prod",
            "contexts": {"prod": {"token": ""}, "dev": {"token": ""}},
        }
    }

    current_context: str = ""

    @staticmethod
    def validate(config: dict) -> dict:
        schema = Schema(
            {
                "auth": {
                    "current_context": str,
                    "contexts": {"prod": {"token": str}, "dev": {"token": str}},
                }
            }
        )
        try:
            return schema.validate(config)
        except SchemaError as e:
            raise IncompatibleConfigException(
                f"Incompatible storage format in {Configuration.FILEPATH}. "
                "Please remove the config and try again."
            ) from e

    @staticmethod
    def create() -> None:
        if not os.path.exists(Configuration.USER_CONFIG_DIR):
            os.makedirs(Configuration.USER_CONFIG_DIR)

        if not os.path.isfile(Configuration.FILEPATH):
            # create a config template with user r+w permissions

            write_config(Configuration.DEFAULT_CONFIG)
            os.chmod(Configuration.FILEPATH, 0o600)

    @staticmethod
    def get_env() -> str:
        if Configuration.current_context:
            return Configuration.current_context

        config = load_config()
        return config["auth"]["current_context"]

    @staticmethod
    def set_context(env: str) -> None:
        config = load_config()
        config["auth"]["current_context"] = env

        write_config(config)

    @staticmethod
    def get_token() -> str:
        return get_auth_context().get("token", "")

    @staticmethod
    def set_token(token: str) -> None:
        config = load_config()

        context = Configuration.current_context
        if not context:
            context = config["auth"]["current_context"]

        config["auth"]["contexts"][context]["token"] = token

        write_config(config)

    @staticmethod
    def override_context(env: str) -> None:
        Configuration.current_context = env


def load_config() -> dict:
    config: dict = {}
    with open(Configuration.FILEPATH, "r") as f:
        config = yaml.load(f)

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


def get_auth_context() -> dict:
    config = load_config()

    context = Configuration.current_context
    if not context:
        context = config["auth"]["current_context"]

    return config["auth"]["contexts"][context]
