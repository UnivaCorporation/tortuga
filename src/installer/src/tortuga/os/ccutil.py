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

"""Helper functions for generating cloud-config files"""


from jinja2 import Template


def incl_user_data_buf(buf, dstfile, owner='root:root', permissions='0644'):
    """Return dict formatted for conversion to YAML. Use 'buf' as file
    contents
    """

    return {
        'path': dstfile,
        'content': buf,
        'owner': owner,
        'permissions': permissions,
    }


def incl_user_data_file(filename, dstfile, owner='root:root',
                        permissions='0644'):
    """Read file contents into buf, return dict suitable for conversion to
    YAML
    """

    with open(filename) as fp:
        buf = fp.read()

    return incl_user_data_buf(buf, dstfile, owner=owner,
                              permissions=permissions)


def incl_user_data_tmpl(tmplfile, dstfile, searchList=None,
                        owner='root:root', permissions='0644'):
    """Convert template into dict suitable for conversion to YAML
    """

    with open(tmplfile) as fp:
        tmpl = fp.read()

    return incl_user_data_buf(
        Template(tmpl).render(searchList[0]),
        dstfile, owner=owner, permissions=permissions)
