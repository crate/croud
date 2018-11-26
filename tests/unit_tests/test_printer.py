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


from croud.printer import FormatPrinter


class TestFormatPrinter(object):
    printer = FormatPrinter()

    def test_json_format(self, capsys):
        sample = {"a": "foo", "b": 1, "c": True}
        self.printer.print_rows(sample, format="json")
        out, err = capsys.readouterr()
        assert out == """{\n  "a": "foo",\n  "b": 1,\n  "c": true\n}\n"""

    def test_tabular_format_dict(self, capsys):
        sample = {"a": "foo", "b": 1, "c": True}
        self.printer.print_rows(sample, format="table")
        out, err = capsys.readouterr()
        assert (
            out
            == """+-----+-----+------+
| a   |   b | c    |
|-----+-----+------|
| foo |   1 | TRUE |
+-----+-----+------+
"""
        )

    def test_tabular_format_multi_row(self, capsys):
        sample = [
            {"a": "foo", "b": 1, "c": True},
            {"b": 2, "c": False, "a": {"bar": [{"value": 0}, {"value": 1}]}},
        ]
        self.printer.print_rows(sample, format="table")
        out, err = capsys.readouterr()
        assert (
            out
            == """+---------------------------------------+-----+-------+
| a                                     |   b | c     |
|---------------------------------------+-----+-------|
| foo                                   |   1 | TRUE  |
| {"bar": [{"value": 0}, {"value": 1}]} |   2 | FALSE |
+---------------------------------------+-----+-------+
"""
        )
