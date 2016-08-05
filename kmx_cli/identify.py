#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlparse
from sqlparse.tokens import DML, DDL, Keyword
from sqlparse.sql import Identifier, IdentifierList
from colorama import Back

identifiers = ['show', 'create', 'select', 'import']


def unrecognized(statement):
    print Back.RED + 'Action <' + statement.tokens[0].value.encode("utf-8").split(' ')[0] + '> is not supported. Only supported: ' + ','.join(identifiers) + Back.RESET


def identify(statement, category):
    token = statement.tokens[0]
    identifier = token.value.encode("utf-8").lower()
    if identifier in identifiers:
        if category == 'DML':
            return token.ttype is DML
        elif category == 'DDL':
            return token.ttype is DDL
        elif category == 'Keyword':
            return token.ttype is Keyword
        elif category == 'Identifier':
            return identifier.split(' ')[0] in identifiers
        elif category == 'IdentifierList':
            return identifier.split(' ')[0] in identifiers
    return False


def isDML(statement):
    return identify(statement, 'DML')


def isDDL(statement):
    return identify(statement, 'DDL')


def isKeyword(statement):
    return identify(statement, 'Keyword')


def isIdentifier(statement):
    return identify(statement, 'Identifier')


def isIdentifierList(statement):
    return identify(statement, 'IdentifierList')



