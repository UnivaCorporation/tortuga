# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Union, Optional, List


def parse_tag_query_string(tag_dict):
    tagspec = []

    # Build list of tag (name, value) tuples
    for tag_ in tag_dict \
            if isinstance(tag_dict, list) else [tag_dict]:
        for tag_item in tag_.split(',', 1):
            tagval = tag_item.split('=', 1)

            if len(tagval) == 2:
                tagspec.append((tagval[0], tagval[1]))
            else:
                tagspec.append((tagval[0],))

    return tagspec


def make_options_from_query_string(
        value: Union[list, str, None],
        default_options: Optional[List[str]] = None) -> dict:
    # take string or list of strings and convert into dict of key=True
    # for use with query methods that take settingsDict. Defaults can
    # be provided as a list of strings

    addl_options = {}

    if value:
        if isinstance(value, str):
            addl_options[value] = True
        else:
            addl_options = dict(
                **addl_options,
                **{key: True for key in value}
            )

    if not default_options:
        return addl_options

    options = {key: True for key in default_options}
    merged_options = options.copy()
    merged_options.update(addl_options)

    return merged_options
