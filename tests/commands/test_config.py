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
import yaml

import croud.config
from croud.config.configuration import Configuration
from croud.config.util import clean_dict
from tests.util import call_command


def test_config_add_profile(config, capsys):
    call_command(
        "croud",
        "config",
        "profiles",
        "add",
        "new-profile",
        "--endpoint",
        "http://localhost:8000",
        "--region",
        "new-region",
    )
    assert "format" not in config.profiles["new-profile"]
    assert config.profiles["new-profile"]["region"] == "new-region"

    _, err = capsys.readouterr()
    assert "Added profile 'new-profile'" in err

    call_command(
        "croud",
        "config",
        "profiles",
        "add",
        "newer-profile",
        "--endpoint",
        "http://localhost:8000",
        "--format",
        "json",
    )
    assert config.profiles["newer-profile"]["format"] == "json"
    assert "region" not in config.profiles["newer-profile"]

    _, err = capsys.readouterr()
    assert "Added profile 'newer-profile'" in err


def test_config_add_duplicate_profile(config, capsys):
    with pytest.raises(SystemExit) as exc_info:
        call_command(
            "croud",
            "config",
            "profiles",
            "add",
            "cratedb.cloud",
            "--endpoint",
            "http://localhost:8000",
        )
    assert exc_info.value.code == 1
    _, err = capsys.readouterr()
    assert "Failed to add profile 'cratedb.cloud'" in err


def test_config_current_profile(config, capsys):
    call_command("croud", "config", "profiles", "current")
    out, _ = capsys.readouterr()
    assert config.name in out


def test_config_remove_profile(config, capsys):
    call_command("croud", "config", "profiles", "remove", "cratedb.cloud")
    assert "cratedb.cloud" not in config.profiles

    _, err = capsys.readouterr()
    assert "Removed profile 'cratedb.cloud'" in err


def test_config_remove_current_profile(config, capsys):
    with pytest.raises(SystemExit) as exc_info:
        call_command("croud", "config", "profiles", "remove", config.name)
    assert exc_info.value.code == 1
    assert config.name in config.profiles

    _, err = capsys.readouterr()
    assert f"Failed to remove profile '{config.name}'" in err


def test_config_set_profile(config, capsys):
    call_command(
        "croud",
        "config",
        "profiles",
        "add",
        "new-profile",
        "--endpoint",
        "http://localhost:8000",
    )
    assert config.name != "new-profile"
    call_command("croud", "config", "profiles", "use", "new-profile")
    assert config.name == "new-profile"

    _, err = capsys.readouterr()
    assert "Switched to profile 'new-profile'" in err


def test_config_set_profile_does_not_exist(config, capsys):
    with pytest.raises(SystemExit) as exc_info:
        call_command("croud", "config", "profiles", "use", "invalid")
    assert exc_info.value.code == 1

    _, err = capsys.readouterr()
    assert "Failed to switch to profile 'invalid'" in err
    assert "Make sure the profile exists." in err


def test_config_show(config, capsys):
    call_command("croud", "config", "show")
    out, err = capsys.readouterr()

    assert out == yaml.safe_dump(clean_dict(config.config)) + "\n"
    assert "Configuration file" in err


def test_invalid_config(capsys, tmp_path):
    with open(tmp_path / "invalid.yaml", "w") as fp:
        # Write a legacy format config
        fp.write(
            """\
auth:
  contexts:
    dev:
      organization_id: ''
      token: ''
    local:
      organization_id: ''
      token: ''
    prod:
      organization_id: ''
      token: ''
  current_context: prod
output_fmt: table
region: bregenz.a1
"""
        )

    invalid_config = Configuration("invalid.yaml", tmp_path)

    with mock.patch.object(croud.config, "_CONFIG", invalid_config):
        with pytest.raises(SystemExit) as exc_info:
            call_command("croud", "me")
    assert exc_info.value.code == 1

    _, err = capsys.readouterr()
    assert (
        "Your configuration file is incompatible with the current version of croud."
        in err
    )
    assert (
        f"Please delete the file '{invalid_config._file_path}' or update it manually."
        in err
    )
