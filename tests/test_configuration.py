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

from unittest import mock

import pytest

from croud.config import WeakConfigProxy
from croud.config.configuration import Configuration
from croud.config.exceptions import InvalidConfiguration, InvalidProfile
from croud.config.util import clean_dict


@pytest.mark.parametrize(
    "source,cleaned",
    [
        ({"auth-token": "secret"}, {"auth-token": "xxxxxxxxxx"}),
        ({"auth-token": None}, {"auth-token": "xxxxxxxxxx"}),
        (
            {"profiles": [{"password": "secret"}]},
            {"profiles": [{"password": "xxxxxxxxxx"}]},
        ),
        (
            {"profiles": {"profile": {"secret": "secret"}}},
            {"profiles": {"profile": {"secret": "xxxxxxxxxx"}}},
        ),
    ],
)
def test_clean_dict(source, cleaned):
    assert clean_dict(source) == cleaned


def test_config_proxy_calls_ref_with_args_kwargs():
    getter = mock.Mock()

    proxy = WeakConfigProxy(getter, "arg", kw="kwarg")
    getter.assert_not_called()

    _ = proxy.data
    getter.assert_called_once_with("arg", kw="kwarg")


def test_config_proxy_gets_ref_attributes():
    m = mock.Mock()

    def getter():
        return m

    proxy = WeakConfigProxy(getter)
    assert proxy.data == m.data


def test_config_proxy_cannot_set_attribute():
    m = mock.Mock()

    def getter():
        return m

    proxy = WeakConfigProxy(getter)
    with pytest.raises(AttributeError, match="Cannot set attribute"):
        proxy.custom_attribute = "croud"


def test_default_configuration_instance(tmp_path):
    with mock.patch(
        "croud.config.configuration.user_config_dir", return_value=str(tmp_path)
    ):
        config = Configuration("test.yaml")
        assert config._file_path == tmp_path / "test.yaml"
        assert "bregenz.a1" in config.profiles
        assert "eastus2.azure" in config.profiles
        assert "westeurope.azure" in config.profiles
        assert config.name == "bregenz.a1"
        assert config.token is None
        assert config.endpoint == "https://bregenz.a1.cratedb.cloud"
        assert config.format == "table"
        assert config.organization is None


def test_load_dump_configuration(tmp_path):
    with mock.patch(
        "croud.config.configuration.user_config_dir", return_value=str(tmp_path)
    ):
        config = Configuration("test.yaml")
        # as long as we don't modify or dump the config, it's not written to disk
        assert config._file_path.exists() is False
        config.dump()
        assert config._file_path.exists() is True
        assert config.config == config.load()


def test_load_invalid_configuration(tmp_path):
    with mock.patch(
        "croud.config.configuration.user_config_dir", return_value=str(tmp_path)
    ):
        with open(tmp_path / "test.yaml", "w") as fp:
            fp.write(
                """\
current-profile: foo
default-format: table
"""
            )
        config = Configuration("test.yaml")
        with pytest.raises(InvalidConfiguration, match="is not a valid configuration"):
            _ = config.config


def test_use_profile(config):
    config.use_profile("westeurope.azure")
    assert config.name == config.config["current-profile"] == "westeurope.azure"


def test_add_profile(config):
    config.add_profile("test", endpoint="http://localhost:8000", format="json")
    assert "test" in config.config["profiles"]
    assert config.config["profiles"]["test"] == {
        "auth-token": None,
        "endpoint": "http://localhost:8000",
        "format": "json",
    }


def test_add_profile_duplicate(config):
    with pytest.raises(InvalidProfile):
        config.add_profile("bregenz.a1", endpoint="http://localhost:8000")


def test_remove_profile(config):
    config.remove_profile("eastus2.azure")
    assert "eastus2.azure" not in config.config["profiles"]


def test_remove_profile_does_not_exist(config):
    with pytest.raises(InvalidProfile):
        config.remove_profile("foo")


def test_remove_profile_current(config):
    with pytest.raises(InvalidProfile):
        config.remove_profile(config.config["current-profile"])


def test_set_profile_options(config):
    profile = "test"
    config.add_profile(profile, endpoint="http://localhost:8000", format="table")

    config.set_auth_token(profile, "token")
    config.set_format(profile, "json")
    config.set_organization_id(profile, "53b70feb-1745-453a-b3f0-d0ac6ea5d55b")

    config.use_profile(profile)
    assert config.profile == {
        "endpoint": config.endpoint,
        "auth-token": config.token,
        "organization-id": config.organization,
        "format": config.format,
    }


def test_default_format(config):
    profile = "test"
    config.add_profile(profile, endpoint="http://localhost:8000")
    config.use_profile(profile)
    assert "format" not in config.profile
    assert config.format == config.config["default-format"]