#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/saneyaml/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import io
import json
import os
import re
from unittest.case import TestCase

import saneyaml

try:
    unicode
except NameError:
    unicode = str  # NOQA


test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def get_test_loc(test_path, exists=True, test_data_dir=test_data_dir):
    """
    Given a `test_path` relative to the `test_data_dir` directory, return the
    location to a test file or directory for this path.
    """
    if not os.path.exists(test_data_dir):
        raise IOError(
            "[Errno 2] No such directory: test_data_dir not found:"
            " '%(test_data_dir)s'" % locals())

    test_loc = os.path.abspath(os.path.join(test_data_dir, test_path))

    if exists and not os.path.exists(test_loc):
        raise IOError(
            "[Errno 2] No such file or directory: test_path not found: "
            "'%(test_loc)s'" % locals())

    return test_loc


class TestSaneyaml(TestCase):

    def test_load_with_and_without_ruby_tags(self):
        test_file_with_tag = get_test_loc('ruby_tags/metadata1')
        test_file_without_tag = get_test_loc('ruby_tags/metadata1.notag')
        with_tags = saneyaml.load(open(test_file_with_tag, 'rb').read())
        without_tags = saneyaml.load(open(test_file_without_tag, 'rb').read())
        assert with_tags == without_tags

    def test_load_optionally_raise_exception_on_dupe(self):
        test = '''
a: 12
b: 23
a: 45
'''
        try:
            saneyaml.load(test, allow_duplicate_keys=False)
            self.fail('Exception not raised')
        except saneyaml.UnsupportedYamlFeatureError as e:
            assert 'Duplicate key in YAML source: a' == str(e)

    def test_load_optionally_raise_exception_on_dupe_in_nested_mappings(self):
        test = '''
2:
    3: 4
    4: 5
    5:
        6: 9
        8: 9
        6: 8
'''
        try:
            saneyaml.load(test, allow_duplicate_keys=False)
            self.fail('Exception not raised')
        except saneyaml.UnsupportedYamlFeatureError:
            pass

    def test_load_does_not_raise_exception_on_dupe_by_default(self):
        test = '''
a: 12
b: 23
a: 45
'''
        saneyaml.load(test)

    def test_dump_does_handles_numbers_and_booleans_correctly(self):
        test = [
            None,
            OrderedDict([
                (1, None),
                (123.34, 'tha')
            ])
        ]
        expected = (
            "-\n"
            "- 1:\n"
            "  '123.34': tha\n")
        assert expected == saneyaml.dump(test)

    def test_dump_increases_indents_correctly(self):
        test = {
        'a': [
            1, [
                2,
                3, [
                    4,
                    5
                    ]
                ]
            ]
        }
        expected = 'a:\n  - 1\n  - - 2\n    - 3\n    - - 4\n      - 5\n'
        assert expected == saneyaml.dump(test)

    def test_dump_converts_bytes_to_unicode_correctly(self):
        test = {b'a': b'foo'}
        expected = 'a: foo\n'
        assert expected == saneyaml.dump(test)

    def test_load_ignore_aliases(self):
        test = '''
x: !!int 5
&environ:
    - this
    - null
    - 2012-03-12

that: *environ
'''
        result = saneyaml.load(test)
        expected = OrderedDict([
            ('x', '5'),
            ('', ['this', 'null', '2012-03-12']),
            ('that', '')
        ])
        assert  expected == result


safe_chars = re.compile(r'[\W_]', re.MULTILINE)


def python_safe(s, python2=False):
    """Return a name safe to use as a python function name"""
    s = s.strip().lower()
    s = [x for x in safe_chars.split(s) if x]
    s = '_'.join(s)
    if saneyaml.python2:
        s = s.encode('utf-8')
    return s


def get_yaml_test_method(test_file, expected_load_file, expected_dump_file, regen=False):
    """
    Build and return a test function closing on tests arguments and the function
    name.
    """

    def closure_test_function(self):
        with io.open(test_file, encoding='utf-8') as inp:
            test_load = saneyaml.load(inp.read())
            test_dump = saneyaml.dump(test_load)

        if regen:
            with io.open(expected_load_file, 'w', encoding='utf-8') as out:
                json.dump(test_load, out, indent=2)

            with io.open(expected_dump_file, 'w', encoding='utf-8') as out:
                out.write(test_dump)

        with io.open(expected_load_file, encoding='utf-8') as inp:
            expected_load = json.load(inp, object_pairs_hook=OrderedDict)

        with io.open(expected_dump_file, encoding='utf-8') as inp:
            expected_dump = inp.read()

        assert expected_load == test_load
        assert expected_dump == test_dump


    tfn = test_file.replace(test_data_dir, '').strip('/\\')
    test_name = 'test_{}'.format(tfn)
    test_name = python_safe(test_name)
    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function, test_name


def build_tests(cls, test_subdir='yamls', test_data_dir=test_data_dir, regen=False):
    """
    Dynamically build test methods from a YAML test files and expected JSON
    files. Attach these methods to the cls test class.
    Collect tests from test and expected files in `test_data_dir/test_subdir`.
    """
    for top, _, files in os.walk(os.path.join(test_data_dir, test_subdir)):
        for yfile in files:
            if yfile.endswith('.yml'):
                test_file = os.path.abspath(os.path.join(top, yfile))
                expected_load_file = test_file + '.expected.load.json'
                expected_dump_file = test_file + '.expected.yaml.dump'
                method, name = get_yaml_test_method(
                    test_file, expected_load_file, expected_dump_file, regen)
                # attach that method to our test class
                setattr(cls, name, method)


class TestDataDriven(TestCase):
    """
    This test case consist of loading and dumping several YAML files and check
    the results using data files.
    """
    # test functions are attached to this class at module import time
    pass


build_tests(cls=TestDataDriven, test_subdir='yamls', regen=False)
