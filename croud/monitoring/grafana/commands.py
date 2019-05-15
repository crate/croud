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

from argparse import Namespace

from croud.rest import Client
from croud.session import RequestMethod


def set_grafana(enable: bool, args: Namespace) -> None:
    method = RequestMethod.POST if enable else RequestMethod.DELETE

    client = Client(env=args.env, region=args.region, output_fmt=args.output_fmt)
    client.send(
        method, "/api/v2/monitoring/grafana/", body={"project_id": args.project_id}
    )
    client.print()
