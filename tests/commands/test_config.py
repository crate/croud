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

import textwrap
from unittest import mock

import pytest

from croud.config import Configuration
from tests.util import MockConfig, call_command


def test_config_get_no_args(capsys):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)
    cfg.conf["auth"]["current_context"] = "the environment"

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        with pytest.raises(SystemExit):
            call_command("croud", "config", "get")

    out, _ = capsys.readouterr()
    assert "Available Commands:\n  {env,region,output-fmt}" in out


def test_config_get_env(capsys):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)
    cfg.conf["auth"]["current_context"] = "the environment"

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        call_command("croud", "config", "get", "env")

    out, err = capsys.readouterr()
    assert (
        out
        == textwrap.dedent(
            """
            +-----------------+
            | env             |
            |-----------------|
            | the environment |
            +-----------------+
            """
        ).lstrip()
    )


def test_config_get_region(capsys):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)
    cfg.conf["region"] = "some region"

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        call_command("croud", "config", "get", "region")

    out, err = capsys.readouterr()
    assert (
        out
        == textwrap.dedent(
            """
            +-------------+
            | region      |
            |-------------|
            | some region |
            +-------------+
            """
        ).lstrip()
    )


def test_config_get_output_fmt(capsys):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)
    cfg.conf["output_fmt"] = "table"

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        call_command("croud", "config", "get", "output-fmt")

    out, err = capsys.readouterr()
    assert (
        out
        == textwrap.dedent(
            """
            +--------------+
            | output-fmt   |
            |--------------|
            | table        |
            +--------------+
            """
        ).lstrip()
    )


def test_config_set_no_args(capsys):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        with mock.patch("croud.config.write_config", side_effect=cfg.write_config):
            call_command("croud", "config", "set")

    out, err = capsys.readouterr()
    assert "Usage: croud config set" in out


def test_config_set_env(capsys):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        with mock.patch("croud.config.write_config", side_effect=cfg.write_config):
            call_command("croud", "config", "set", "--env", "dev")

    out, err = capsys.readouterr()
    assert err == "\x1b[36m==> Info: \x1b[0mEnvironment switched to dev\n"
    assert cfg.conf["auth"]["current_context"] == "dev"


def test_config_set_multiple(capsys):
    cfg = MockConfig(Configuration.DEFAULT_CONFIG)

    with mock.patch("croud.config.load_config", side_effect=cfg.read_config):
        with mock.patch("croud.config.write_config", side_effect=cfg.write_config):
            call_command(
                "croud",
                "config",
                "set",
                "--region",
                "eastus.azure",
                "--output-fmt",
                "json",
            )

    out, err = capsys.readouterr()
    assert "\x1b[36m==> Info: \x1b[0mRegion switched to eastus.azure\n" in err
    assert "\x1b[36m==> Info: \x1b[0mOutput format switched to json\n" in err

    assert cfg.conf["region"] == "eastus.azure"
    assert cfg.conf["output_fmt"] == "json"
