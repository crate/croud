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
from pathlib import Path

from appdirs import user_config_dir


class Configuration:

    USER_CONFIG_DIR: Path = Path(user_config_dir("Crate"))
    CONFIG_FILE_NAME: str = "cloud_token"
    CONFIG_PATH: Path = USER_CONFIG_DIR / CONFIG_FILE_NAME

    @staticmethod
    def write_token(token: str) -> None:
        os.makedirs(os.path.dirname(Configuration.CONFIG_PATH), exist_ok=True)
        with open(Configuration.CONFIG_PATH, "w") as f:
            f.write(token)

    @staticmethod
    def read_token() -> str:
        if Configuration.CONFIG_PATH.exists():
            with open(Configuration.CONFIG_PATH) as f:
                return f.readline()
        else:
            return ""
