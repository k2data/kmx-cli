#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        print '-------------------------------------------'
        if category == 'DML':
            return statement.tokens[0].ttype is DML
        elif category == 'DDL':
            return statement.tokens[0].ttype is DDL
        elif category == 'Keyword':
            return statement.tokens[0].ttype is Keyword
        elif category == 'Identifier':
            return statement.tokens[0].ttype is Identifier
        elif category == 'IdentifierList':
            return statement.tokens[0].ttype is IdentifierList
    elif category == 'IdentifierList':
        identifier = statement.tokens[0].value.encode("utf-8").lower().split(' ')[0]
        return identifier in identifiers
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




