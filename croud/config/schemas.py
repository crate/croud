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

from marshmallow import Schema, fields, post_load
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf

OUTPUT_FORMATS = ("table", "wide", "json", "yaml")  # we want to keep them sorted!


class ProfileSchema(Schema):
    """
    Schema for profile entries
    """

    auth_token = fields.String(
        attribute="auth-token", data_key="auth-token", required=False, allow_none=True
    )
    key = fields.String(
        attribute="key", data_key="key", required=False, allow_none=True
    )
    secret = fields.String(
        attribute="secret", data_key="secret", required=False, allow_none=True
    )
    endpoint = fields.String(required=True)
    format = fields.String(validate=OneOf(choices=OUTPUT_FORMATS))
    organization_id = fields.String(
        attribute="organization-id", data_key="organization-id", allow_none=True
    )
    region = fields.String(required=False)
    gc_endpoint = fields.String(required=False)
    gc_jwt_token = fields.String(
        attribute="gc_jwt_token",
        data_key="gc_jwt_token",
        required=False,
        allow_none=True,
    )
    gc_jwt_token_expiry = fields.String(
        attribute="gc_jwt_token_expiry",
        data_key="gc_jwt_token_expiry",
        required=False,
        allow_none=True,
    )
    gc_cluster_id = fields.String(
        attribute="gc_cluster_id",
        data_key="gc_cluster_id",
        required=False,
        allow_none=True,
    )


class ConfigSchema(Schema):
    """
    Schema for configuration file
    """

    default_format = fields.String(
        attribute="default-format", data_key="default-format", required=True
    )
    current_profile = fields.String(
        attribute="current-profile", data_key="current-profile", required=True
    )
    profiles = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(ProfileSchema()),
        required=True,
    )

    @post_load
    def validate_current_profile(self, data, **kwargs):
        if data["current-profile"] not in data["profiles"]:
            raise ValidationError("The 'current-profile' does not exist in 'profiles'.")
        return data
