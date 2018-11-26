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


class Configuration:
    USER_CONFIG_DIR: str = user_config_dir("Crate")
    FILENAME: str = "croud.yaml"
    FILEPATH: str = f"{USER_CONFIG_DIR}/{FILENAME}"

    @staticmethod
    def create() -> None:
        if not os.path.exists(Configuration.USER_CONFIG_DIR):
            os.makedirs(Configuration.USER_CONFIG_DIR)

        if not os.path.isfile(Configuration.FILEPATH):
            write_config({"env": "prod", "token": ""})

    @staticmethod
    def get_env() -> str:
        return load_config().get("env") or "prod"

    @staticmethod
    def set_env(env: str) -> None:
        set_property("env", env)

    @staticmethod
    def get_token() -> str:
        return load_config().get("token") or ""

    @staticmethod
    def set_token(token: str) -> None:
        set_property("token", token)


def load_config() -> dict:
    with open(Configuration.FILEPATH, "r") as f:
        return yaml.load(f) or {}


def write_config(config: dict) -> None:
    with open(Configuration.FILEPATH, "w", encoding="utf8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def set_property(property: str, value: str):
    config = load_config()
    config[property] = value
    write_config(config)
