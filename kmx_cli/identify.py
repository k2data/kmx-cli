#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlparse.tokens import DML, DDL, Keyword
from colorama import Back

default_identifiers = ['show', 'create', 'select']
custom_identifiers = ['import']


def token_value(token):
    return token.value.encode("utf-8")


def unrecognized(statement):
    print Back.RED + 'Action <' + token_value(statement.tokens[0]).split(' ')[0] + '> is not supported. Only supported: ' + ','.join(identifiers) + Back.RESET


def identify(statement, category):
    token = statement.tokens[0]
    identifier = token.value.encode("utf-8").lower()

    if category == 'DML':
        return token.ttype is DML and identifier in default_identifiers
    elif category == 'DDL':
        return token.ttype is DDL and identifier in default_identifiers
    elif category == 'Keyword':
        return token.ttype is Keyword and identifier in default_identifiers
    elif category == 'Identifier':
        return False and identifier.split(' ')[0] in custom_identifiers
    elif category == 'IdentifierList':
        return identifier.split(' ')[0] in custom_identifiers
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


if __name__ == '__main__':
    import sqlparse
    statements = sqlparse.parse('import data.csv into test_deviceType;select * from devices;create devices id(deviceTypeId) tags(t1,t2) attributes(k1 v1,k2 v2);show devices')
    for statement in statements:
        print '"' + str(statement.tokens[0]) + '" isDML : ' + str(isDML(statement))
        print '"' + str(statement.tokens[0]) + '" isDDL : ' + str(isDDL(statement))
        print '"' + str(statement.tokens[0]) + '" isKeyword : ' + str(isKeyword(statement))
        print '"' + str(statement.tokens[0]) + '" isIdentifier : ' + str(isIdentifier(statement))
        print '"' + str(statement.tokens[0]) + '" isIdentifierList : ' + str(isIdentifierList(statement))
        print


