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

import pytest
import yaml
from marshmallow.exceptions import ValidationError

from croud.config.configuration import ConfigSchema, ProfileSchema


@pytest.mark.parametrize(
    "data",
    [
        """\
    auth-token: NULL
    endpoint: http://localhost:8000
    """,
        """\
    auth-token: NULL
    endpoint: http://localhost:8000
    format: json
    """,
        """\
    auth-token: NULL
    endpoint: http://localhost:8000
    organization-id: 804f1f14-0a5e-46b4-ab37-6d046b1fa07b
    """,
    ],
)
def test_load_profile_schema_valid(data):
    schema = ProfileSchema()
    schema.load(yaml.safe_load(data))


@pytest.mark.parametrize(
    "data,errors",
    [
        (
            """\
    auth-token: NULL
    endpoint: http://localhost:8000
    invalid: true
    """,
            {"invalid": ["Unknown field."]},
        ),
        (
            """\
    format: json
    organization-id: 804f1f14-0a5e-46b4-ab37-6d046b1fa07b
    """,
            {
                "endpoint": ["Missing data for required field."],
            },
        ),
        (
            """\
    auth-token: NULL
    endpoint: http://localhost:8000
    format: invalid
    """,
            {"format": ["Must be one of: table, wide, json, yaml."]},
        ),
    ],
)
def test_load_profile_schema_invalid(data, errors):
    schema = ProfileSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load(yaml.safe_load(data))
    assert exc_info.value.messages == errors


@pytest.mark.parametrize(
    "data",
    [
        """\
    current-profile: local
    default-format: table
    profiles:
      local:
        endpoint: https://localhost:8000
        auth-token: NULL
    """,
    ],
)
def test_load_config_schema_valid(data):
    schema = ConfigSchema()
    schema.load(yaml.safe_load(data))


@pytest.mark.parametrize(
    "data,errors",
    [
        (
            """\
    current-profile: local
    default-format: table
    profiles: {}
    """,
            {"_schema": ["The 'current-profile' does not exist in 'profiles'."]},
        ),
        (
            """\
    {}
    """,
            {
                "current-profile": ["Missing data for required field."],
                "default-format": ["Missing data for required field."],
                "profiles": ["Missing data for required field."],
            },
        ),
    ],
)
def test_load_config_schema_invalid(data, errors):
    schema = ConfigSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load(yaml.safe_load(data))
    assert exc_info.value.messages == errors
