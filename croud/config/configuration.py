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
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from appdirs import user_config_dir
from marshmallow import ValidationError

from croud.config.exceptions import InvalidConfiguration, InvalidProfile
from croud.config.schemas import ConfigSchema, ProfileSchema
from croud.config.types import ConfigurationType, ProfileType

DEFAULT_CONFIGURATION = """\
default-format: table
current-profile: cratedb.cloud
profiles:
  cratedb.cloud:
    auth-token: NULL
    key: NULL
    secret: NULL
    endpoint: https://console.cratedb.cloud
    region: _any_
"""


class Configuration:
    """
    The state representation class of the configuration file.

    There should only be a single instance of this class (representing the
    ``croud.yaml`` configuration file in the user's configuration directory,
    however for testing purposes, the name and path of the configuration file
    are configurable.

    When using the configuration, please use the :ref:`croud.config.CONFIG`
    instead.

    The configuration loads the contents of the configuration file lazily upon
    first access of the ``config`` property.

    The configuration is written to disk only whenever modifications are made
    to the in-memory state using the "public" methods.

    If there is no configuration file on disk, the state will be populated with
    the default configuration.
    """

    def __init__(self, name: str, path: Optional[Path] = None):
        self._config_dir = path or Path(user_config_dir("Crate"))
        self._file_path = self._config_dir / name
        self._config: Optional[ConfigurationType] = None
        self._schema = ConfigSchema()

    @property
    def config(self) -> ConfigurationType:
        if not self._config:
            self._config = self.load()
        return self._config

    @property
    def name(self) -> str:
        return self.config["current-profile"]  # type: ignore

    @property
    def endpoint(self) -> str:
        return self.profile["endpoint"]  # type: ignore

    @property
    def format(self) -> str:
        return self.profile.get("format", self.config["default-format"])  # type: ignore

    @property
    def token(self) -> Optional[str]:
        return self.profile.get("auth-token")

    @property
    def key(self) -> Optional[str]:
        return self.profile.get("key")

    @property
    def secret(self) -> Optional[str]:
        return self.profile.get("secret")

    @property
    def region(self) -> Optional[str]:
        return self.profile.get("region", None)  # type: ignore

    @property
    def organization(self) -> Optional[str]:
        return self.profile.get("organization-id")  # type: ignore

    @property
    def gc_jwt_token(self) -> Optional[str]:
        return self.profile.get("gc_jwt_token")

    @property
    def gc_jwt_token_expiry(self) -> Optional[str]:
        return self.profile.get("gc_jwt_token_expiry")

    @property
    def gc_cluster_id(self) -> Optional[str]:
        return self.profile.get("gc_cluster_id")

    @property
    def profile(self) -> ProfileType:
        return self.profiles[self.name]  # type: ignore

    @property
    def profiles(self) -> Dict[str, ProfileType]:
        return self.config["profiles"]  # type: ignore

    def load(self) -> ConfigurationType:
        if not self._file_path.exists():
            data = yaml.safe_load(DEFAULT_CONFIGURATION)
        else:
            with open(self._file_path, "r") as fp:
                data = yaml.safe_load(fp)
        # self._schema.load() will evaluate the correctness of the
        # configuration
        try:
            return self._schema.load(data)
        except ValidationError:
            raise InvalidConfiguration(
                f"{self._file_path} is not a valid configuration."
            ) from None
            exit(1)

    def is_valid(self):
        try:
            self.config
        except InvalidConfiguration:
            return False
        else:
            return True

    def dump(self) -> None:
        # make sure the config is in memory before we open the file for writing
        data = self.config
        self._config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        with open(self._file_path, "w") as fp:
            yaml.safe_dump(data, fp)

    def _set_profile_option(self, profile: str, attr: str, value: Any) -> None:
        if profile not in self.profiles:
            raise InvalidProfile(profile)
        data = self.profiles[profile]
        data[attr] = value
        self.update_profile(profile, data)

    def set_organization_id(self, profile: str, value: str) -> None:
        self._set_profile_option(profile, "organization-id", value)

    def set_current_organization_id(self, value: str) -> None:
        self.set_organization_id(self.name, value)

    def set_auth_token(self, profile: str, value: str) -> None:
        self._set_profile_option(profile, "auth-token", value)

    def set_current_auth_token(self, value: str) -> None:
        self.set_auth_token(self.name, value)

    def set_gc_jwt_token(self, profile: str, value: str) -> None:
        self._set_profile_option(profile, "gc_jwt_token", value)

    def set_current_gc_jwt_token(self, value: str) -> None:
        self.set_gc_jwt_token(self.name, value)

    def set_gc_jwt_token_expiry(self, profile: str, value: str) -> None:
        self._set_profile_option(profile, "gc_jwt_token_expiry", value)

    def set_current_gc_jwt_token_expiry(self, value: str) -> None:
        self.set_gc_jwt_token_expiry(self.name, value)

    def set_gc_cluster_id(self, profile: str, value: str) -> None:
        self._set_profile_option(profile, "gc_cluster_id", value)

    def set_current_gc_cluster_id(self, value: str) -> None:
        self.set_gc_cluster_id(self.name, value)

    def set_format(self, profile: str, value: str) -> None:
        self._set_profile_option(profile, "format", value)

    def set_current_format(self, value: str) -> None:
        self.set_format(self.name, value)

    def add_profile(self, profile: str, *, endpoint: str, **kwargs) -> None:
        if profile in self.profiles:
            raise InvalidProfile(profile)
        data = {"auth-token": None, "endpoint": endpoint}  # required fields
        data.update(kwargs)  # optional fields
        self.update_profile(profile, data)

    def update_profile(self, profile: str, data: Dict) -> None:
        profile_schema = ProfileSchema()
        self.profiles[profile] = profile_schema.dump(data)
        self.dump()

    def remove_profile(self, profile: str) -> None:
        if profile not in self.profiles or profile == self.name:
            raise InvalidProfile(profile)
        del self.profiles[profile]
        self.dump()

    def use_profile(self, profile: str) -> None:
        if profile not in self.profiles:
            raise InvalidProfile(profile)
        self._config["current-profile"] = profile  # type: ignore
        self.dump()
