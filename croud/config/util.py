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

import re
from typing import Any, Dict

SENSITIVE_KEYS = re.compile("pass|secret|token", flags=re.IGNORECASE)


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean "secrets" from a dict.

    This is solely used for masking the "auth-token" value of the configuration
    dictionary when printing it to the console.

    It can only handle "pure" dicts with strings as keys and dicts, lists and
    simple types as values.
    """

    def clean(k, v):
        if SENSITIVE_KEYS.search(k):
            return "x" * 10
        elif isinstance(v, list):
            cleaned_list = []
            for item in v:
                if isinstance(item, dict):
                    cleaned_list.append(clean_dict(item))
                else:
                    cleaned_list.append(item)
            return cleaned_list
        elif isinstance(v, dict):
            return clean_dict(v)
        return v

    return {k: clean(k, v) for k, v in data.items()}
