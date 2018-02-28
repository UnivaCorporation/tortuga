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
