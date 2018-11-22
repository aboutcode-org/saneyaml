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


from functools import partial
import sys

import yaml
from yaml.error import YAMLError
from pip._vendor.distlib.compat import OrderedDict
from yaml.emitter import Emitter
from yaml.resolver import Resolver
from yaml.representer import SafeRepresenter
from yaml.serializer import Serializer

try:  # pragma: nocover
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: nocover
    from yaml import SafeLoader

try:  # pragma: nocover
    # Python 2
    unicode
except NameError:  # pragma: nocover
    # Python 3
    unicode = str  # NOQA

# Python 2 to 3.5
python2 = sys.version_info[0] < 3
python3old = sys.version_info[0] == 3 and sys.version_info[1] < 6
OLD_PY = python2 or python3old

if OLD_PY:  # pragma: nocover
    from collections import OrderedDict as odict
else:
    # CPython 3.6 and up dict is ordered by default. And this is the Python spec
    # in 3.7 and up.
    odict = dict

"""
A wrapper around PyYAML to provide sane defaults ensuring that dump/load does
not damage content, keeps ordering and ordered mappings, use always block-style
and use two spaces indents to get the most readable YAML and quotes or folds
texts in a sane way.

Use the `load` function to get a primitive type from a YAML string and the
`dump` function to get a YAML string from a primitive type.
Optionally check that there are no duplicated map keys when loading.

Load and dump rely on subclasses of SafeLoader and SafeDumper respectively
doing all the dirty bidding to get PyYAML straight.

Note that since PyYAML does not have a consistent dump indent behaviou accross
versions and Python vs C/libyaml, the tests may behave differently in some cases
and fail.
"""


###############################################################################
# Loading
###############################################################################

def load(s, allow_duplicate_keys=True):
    """
    Return an object safely loaded from a YAML string `s`. `s` must be unicode
    or a string that converts to unicode without errors using an `utf-8` codec.

    If `allow_duplicate_keys` is False, a DuplicateYamlMappingKeyError Exception
    is raised if a mapping contains duplicated keys.
    """
    if allow_duplicate_keys:
        loader = SaneLoader
    else:
        loader = DupeKeySaneLoader
    return yaml.load(s, Loader=loader)


class UnsupportedYamlFeatureError(YAMLError):
    pass


class BaseSaneLoader(SafeLoader):
    """
    A base safe loader configured with many sane defaults.
    """

    def string_loader(loader, node):  # NOQA
        """
        Ensure that a scalar type (a value) is returned as a plain unicode string.
        """
        return loader.construct_scalar(node)

    def ordered_loader(self, node, check_dupe=False):
        """
        Ensure that YAML maps order is preserved and loaded in an ordered mapping.
        """
        assert isinstance(node, yaml.MappingNode)
        omap = odict()
        yield omap
        for key, value in node.value:
            key = self.construct_object(key)
            value = self.construct_object(value)
            if check_dupe and key in omap:
                raise UnsupportedYamlFeatureError(
                    'Duplicate key in YAML source: {}'.format(key))
            omap[key] = value

# Load most types as strings : nulls, ints, (such as in version 01) floats (such
# as version 2.20) and timestamps conversion (in versions too), booleans are all
# loaded as plain strings.
# This avoid unwanted type conversions for unquoted strings and the resulting
# content damaging. This overrides the implicit resolvers. Callers must handle
# type conversion explicitly from unicode to other types in the loaded objects.

BaseSaneLoader.add_constructor('tag:yaml.org,2002:str', BaseSaneLoader.string_loader)
BaseSaneLoader.add_constructor('tag:yaml.org,2002:null', BaseSaneLoader.string_loader)
BaseSaneLoader.add_constructor('tag:yaml.org,2002:boolean', BaseSaneLoader.string_loader)
BaseSaneLoader.add_constructor('tag:yaml.org,2002:timestamp', BaseSaneLoader.string_loader)
BaseSaneLoader.add_constructor('tag:yaml.org,2002:float', BaseSaneLoader.string_loader)
BaseSaneLoader.add_constructor('tag:yaml.org,2002:int', BaseSaneLoader.string_loader)
BaseSaneLoader.add_constructor('tag:yaml.org,2002:null', BaseSaneLoader.string_loader)
# Fall back to mapping for anything else, e.g. ignore tags such as
# !!Python, ruby and other dangerous mappings: treat them as a mapping
BaseSaneLoader.add_constructor(None, BaseSaneLoader.ordered_loader)


class SaneLoader(BaseSaneLoader):
    pass

# Always load mapping as ordered mappings
SaneLoader.add_constructor('tag:yaml.org,2002:map', BaseSaneLoader.ordered_loader)
SaneLoader.add_constructor('tag:yaml.org,2002:omap', BaseSaneLoader.ordered_loader)


class DupeKeySaneLoader(BaseSaneLoader):
    """
    A variant that check that maps do not contain duplicate keys.
    Raise DuplicateYamlMappingKeyError on duplicate.
    """
    pass


# Always load mapping as ordered mappings
dupe_checkding_ordered_loader = partial(BaseSaneLoader.ordered_loader, check_dupe=True)
DupeKeySaneLoader.add_constructor('tag:yaml.org,2002:map', dupe_checkding_ordered_loader)
DupeKeySaneLoader.add_constructor('tag:yaml.org,2002:omap', dupe_checkding_ordered_loader)


###############################################################################
# Dumping
###############################################################################

def dump(obj, indent=2, encoding=None):
    """
    Return a safe and sane YAML string representation from `obj`.
    This is a unicode string if `encoding` is None.
    Otherwise this is a byte string using the provided encoding.
    The preferred encoding should be UTF-8 for bytes.
    """
    return yaml.dump(
        data=obj,
        Dumper=SaneDumper,
        # no flow, only block and minimal styling
        default_flow_style=False,
        default_style=None,
        # this would include the type tags if True
        canonical=False,
        # all unicode
        allow_unicode=True,
        encoding=encoding,
        # anything above 2 will yield weird vertical indents on lists and maps
        indent=indent,
        # make this 80ish
        width=90,
        # posix LF
        line_break='\n',
        # no --- and ...
        explicit_start=False,
        explicit_end=False,
    )


class IndentingEmitter(Emitter):
    def increase_indent(self, flow=False, indentless=False):
        """
        Ensure that lists items are always indented.
        """
        return super(IndentingEmitter, self).increase_indent(
            flow=False, indentless=False)


class SaneDumper(IndentingEmitter, Serializer, SafeRepresenter, Resolver):

    def __init__(self, stream,
            default_style=None, default_flow_style=None,
            canonical=None, indent=None, width=None,
            allow_unicode=None, line_break=None,
            encoding=None, explicit_start=None, explicit_end=None,
            version=None, tags=None):
        IndentingEmitter.__init__(self, stream, canonical=canonical,
                indent=indent, width=width,
                allow_unicode=allow_unicode, line_break=line_break)
        Serializer.__init__(self, encoding=encoding,
                explicit_start=explicit_start, explicit_end=explicit_end,
                version=version, tags=tags)
        SafeRepresenter.__init__(self, default_style=default_style,
                default_flow_style=default_flow_style)
        Resolver.__init__(self)

    def determine_block_hints(self, text):
        """
        Avoid extra hint in blocks such as `|-` for literals.
        """
        return ''

    def ignore_aliases(self, data):
        """
        Avoid having aliases created from re-used Python objects or else.
        """
        return True

    def ordered_dumper(self, data):
        """
        Ensure that maps are always dumped in the items order.
        """
        return self.represent_mapping('tag:yaml.org,2002:map', data.items(), flow_style=False)

    def null_dumper(self, value):  # NOQA
        """
        Always dump nulls as empty string.
        """
        return self.represent_scalar('tag:yaml.org,2002:null', '')

    def string_dumper(self, value):
        """
        Ensure that all scalars are dumped as UTF-8 unicode, folded and quoted
        in the sanest and most readable way.
        """
        tag = 'tag:yaml.org,2002:str'
        style = None
        if isinstance(value, float):
            style = "'"

        if isinstance(value, bytes):
            value = value.decode('utf-8')
        elif not isinstance(value, unicode):
            value = repr(value)

        # do not quote integer strings
        if value.isdigit() and unicode(int(value)) == value:
            style = None
            tag = 'tag:yaml.org,2002:int'

        if '\n' in value:
            # literal_style for multilines
            style = '|'

        return self.represent_scalar(tag, value, style=style)

    def boolean_dumper(self, value):
        """
        Dump booleans as yes or no strings.
        They will be loaded back as boolean by default alright.
        """
        value = 'yes' if value else 'no'
        return self.represent_scalar('tag:yaml.org,2002:bool', value, style=None)


SaneDumper.add_representer(int, SaneDumper.string_dumper)
SaneDumper.add_representer(odict, SaneDumper.ordered_dumper)
if not OLD_PY:
    SaneDumper.add_representer(OrderedDict, SaneDumper.ordered_dumper)
SaneDumper.add_representer(type(None), SaneDumper.null_dumper)
SaneDumper.add_representer(bool, SaneDumper.boolean_dumper)
SaneDumper.add_representer(bytes, SaneDumper.string_dumper)
SaneDumper.add_representer(str, SaneDumper.string_dumper)
SaneDumper.add_representer(unicode, SaneDumper.string_dumper)
SaneDumper.add_representer(float, SaneDumper.string_dumper)
