import logging

from pyparsing import Suppress, pyparsing_common

from .baseparser import BaseParser, W, quote, delimitedSet
from .parse_exceptions import *

log = logging.getLogger('pybel')


# TODO remove citation and annotations as arguments?
class ControlParser(BaseParser):
    def __init__(self, custom_annotations=None):
        """Builds parser for BEL custom_annotations statements

        :param custom_annotations: A dictionary from {annotation: set of valid values} for parsing
        :type custom_annotations: dict
        """

        self.citation = {}
        self.annotations = {}
        self.valid_annotations = dict() if custom_annotations is None else custom_annotations
        self.statement_group = None

        # custom_annotations = oneOf(self.custom_annotations.keys())
        annotation_key = pyparsing_common.identifier.setResultsName('key')
        annotation_key.setParseAction(self.handle_annotation_key)

        set_tag = Suppress('SET')
        unset_tag = Suppress('UNSET')

        self.set_statement_group = set_tag + W + Suppress('STATEMENT_GROUP') + W + Suppress('=') + W + quote('group')
        self.set_statement_group.setParseAction(self.handle_statement_group)

        self.set_citation = set_tag + W + Suppress('Citation') + W + Suppress('=') + W + delimitedSet('values')
        self.set_citation.setParseAction(self.handle_citation)

        self.set_evidence = set_tag + W + Suppress('Evidence') + W + Suppress('=') + W + quote('value')
        self.set_evidence.setParseAction(self.handle_evidence)

        self.set_command = set_tag + W + annotation_key + W + Suppress('=') + W + quote('value')
        self.set_command.setParseAction(self.handle_set_command)

        self.set_command_list = set_tag + W + annotation_key + W + Suppress('=') + W + delimitedSet('values')
        self.set_command_list.setParseAction(self.handle_set_command_list)

        self.unset_command = unset_tag + W + annotation_key
        self.unset_command.setParseAction(self.handle_unset_command)

        self.unset_evidence = unset_tag + W + Suppress('Evidence')
        self.unset_evidence.setParseAction(self.handle_unset_evidence)

        self.unset_citation = unset_tag + W + Suppress('Citation')
        self.unset_citation.setParseAction(self.handle_unset_citation)

        self.unset_statement_group = unset_tag + W + Suppress('STATEMENT_GROUP')
        self.unset_statement_group.setParseAction(self.handle_unset_statement_group)

        self.commands = (self.set_statement_group | self.set_citation | self.set_evidence |
                         self.set_command | self.set_command_list | self.unset_citation |
                         self.unset_evidence | self.unset_statement_group | self.unset_command)

    def handle_annotation_key(self, s, l, tokens):
        key = tokens['key']
        if key not in self.valid_annotations:
            raise InvalidAnnotationKeyException("Illegal annotation: {}".format(key))
        return tokens

    def handle_unset_evidence(self, s, l, tokens):
        if 'Evidence' not in self.annotations:
            log.debug("PyBEL024 Can't unset missing key: {}".format('Evidence'))
        else:
            del self.annotations['Evidence']
        return tokens

    def handle_unset_citation(self, s, l, tokens):
        if 0 == len(self.citation):
            log.debug("PyBEL024 Can't unset missing key: {}".format('Citation'))
        else:
            self.citation.clear()
        return tokens

    def handle_citation(self, s, l, tokens):
        self.citation.clear()
        self.annotations.clear()

        values = tokens['values']

        if len(values) not in (3, 6):
            raise InvalidCitationException('Invalid citation: {}'.format(s))

        self.citation = dict(zip(('type', 'name', 'reference', 'date', 'authors', 'comments'), values))

        return tokens

    def handle_evidence(self, s, l, tokens):
        value = tokens['value']
        self.annotations['Evidence'] = value
        return tokens

    def handle_statement_group(self, s, l, tokens):
        self.statement_group = tokens['group']
        return tokens

    def handle_set_command(self, s, l, tokens):
        key = tokens['key']
        value = tokens['value']

        if value not in self.valid_annotations[key]:
            raise IllegalAnnotationValueExeption('Illegal annotation value: {}'.format(value))

        self.annotations[key] = value
        return tokens

    def handle_set_command_list(self, s, l, tokens):
        key = tokens['key']
        values = tokens['values']

        for value in values:
            if value not in self.valid_annotations[key]:
                raise IllegalAnnotationValueExeption('Illegal annotation value: {}'.format(value))

        self.annotations[key] = set(values)
        return tokens

    def handle_unset_statement_group(self, s, l, tokens):
        self.statement_group = None
        return tokens

    def handle_unset_command(self, s, l, tokens):
        key = tokens['key']

        if key not in self.annotations:
            raise MissingAnnotationKeyException("Can't unset missing key: {}".format(key))

        del self.annotations[key]
        return tokens

    def get_language(self):
        return self.commands

    def get_annotations(self):
        annot = self.annotations.copy()
        for key, value in self.citation.items():
            annot['citation_{}'.format(key)] = value
        return annot

    def clear_annotations(self):
        self.annotations.clear()

    def clear(self):
        self.annotations.clear()
        self.citation.clear()
        self.statement_group = None
