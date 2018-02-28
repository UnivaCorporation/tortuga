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

# pylint: disable=no-member

import logging
import pkgutil

from tortuga.objects.rule import Rule
from tortuga.rule.ruleEngineNoop import RuleEngineNoop
from tortuga.rule.ruleXmlParserNoop import RuleXmlParserNoop
import tortuga.rule
from tortuga.rule.ruleEngineInterface import RuleEngineInterface
from tortuga.rule.ruleXmlParserInterface import RuleXmlParserInterface


def __look_for_subclass(modulename, cls):
    module = __import__(modulename)

    # Find the dict associated with the "last" component in the module
    d = module.__dict__
    for m in modulename.split('.')[1:]:
        d = d[m].__dict__

    entry = None

    for key, entry in d.items():
        if key == cls.__name__:
            # Do not include the class we're looking for
            continue

        try:
            if issubclass(entry, cls):
                break
        except TypeError:
            # Ignore any types that aren't classes
            continue
    else:
        return None

    return entry


def find_subclass(path, prefix, cls):
    for _, modname, _ in pkgutil.walk_packages(
            path=path, prefix=prefix + '.'):
        subclass = __look_for_subclass(modname, cls)

        if subclass:
            break
    else:
        return None

    return subclass


class RuleObjectFactory(object):
    """
    Rule object factory class.
    """

    def __init__(self):
        self._logger = logging.getLogger(
            'tortuga.rule.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())

        # create engine and parser.
        self._engine = None
        self._parser = None

    def getNewRuleObject(self):     # pylint: disable=no-self-use
        """ Get rule object. """
        return Rule()

    def getEngine(self):
        """ Get rule engine. """
        if not self._engine:
            subclass = find_subclass(
                path=tortuga.rule.__path__,
                prefix=tortuga.rule.__name__,
                cls=RuleEngineInterface)

            if subclass:
                self._engine = subclass()
            else:
                # Fallback to the default
                self._engine = RuleEngineNoop()

        return self._engine

    def getParser(self):
        """ Get rule object parser. """
        if not self._parser:
            subclass = find_subclass(
                path=tortuga.rule.__path__,
                prefix=tortuga.rule.__name__,
                cls=RuleXmlParserInterface
            )

            if subclass:
                self._parser = subclass()
            else:
                # Fallback to the default
                self._parser = RuleXmlParserNoop()

        return self._parser
