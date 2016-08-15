#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from sqlparse.sql import Identifier, IdentifierList, TokenList, Token, Where, Comparison
from sqlparse.tokens import DML, DDL, Keyword, Whitespace
import log

default_identifiers = ['show', 'create', 'select', 'drop', 'update']
custom_identifiers = ['import']

identifiers = copy.deepcopy(default_identifiers)
identifiers.extend(custom_identifiers)


def unrecognized(statement):
    log.error('command： <' + statement.tokens[0].value.encode("utf-8").split(' ')[0] + '> is not supported. Only supported: ' + ','.join(identifiers))


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
        return isinstance(token, Identifier) and identifier.split(' ')[0] in custom_identifiers
    elif category == 'IdentifierList':
        return isinstance(token, IdentifierList) and identifier.split(' ')[0] in custom_identifiers
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

def isWhere(statement):
    ''' @author: Chang, Xue '''
    return isinstance(statement, Where)

def canIgnore(statement):
    ''' match Whitespace, Punctuation '''
    if hasattr(statement, 'ttype'):
        return str(statement.ttype) in ('Token.Text.Whitespace', 'Token.Punctuation')
    return False

def isWildcard(statement):
    ''' @author: Chang,Xue
        match Wildcard '''
    return not hasattr(statement, 'ttype') or str(statement.ttype) == 'Token.Wildcard'

def isComparison(statement):
    '''@author: Chang,Xue
       match Wildcard '''
    return isinstance(statement, Comparison)


def trip_tokens(tokens):
    for token in tokens:
        if hasattr(token, 'ttype') and token.ttype is Whitespace:
            tokens.remove(token)
    return tokens


def find_next_token_by_ttype(sql, lambda_func, target_ttype):
    '''
    import sqlparse
    from sqlparse.tokens import Literal
    parsed = sqlparse.parse("select longitudeNum from C2063B where ts>'now-3d' and ts < 'now' size 30 page 2 size 10")
    find_next_token_by_ttype(parsed[0], lambda t: t.value.upper() == 'PAGE', Literal.Number.Integer)
    :param sql:
    :param lambda_func:
    :param target_ttype:
    :return:
    '''
    tokens = TokenList(sql.tokens)
    if isinstance(tokens, TokenList):
        tokens = list(tokens.flatten())
        tokens = TokenList(tokens)
        source_token = tokens.token_matching(lambda_func, 0)
        if source_token:
            source_idx = tokens.token_index(source_token, 0)
            start = source_idx + 1
            find = True
            from sqlparse.tokens import Whitespace
            while tokens[start].ttype is not target_ttype or tokens[start].ttype is Whitespace:
                if start < len(list(tokens)) - 1:
                    start += 1
                else:
                    find = False
                    break
            # print start
            if find:
                target = tokens[start].value
            else:
                target = None
            # print source_token
            # print target
    return source_token,target

if __name__ == '__main__':
    import sqlparse
    '''    statements = sqlparse.parse('import data.csv into test_deviceType;select * from devices;create devices id(deviceTypeId) tags(t1,t2) attributes(k1 v1,k2 v2);show devices;testdcz; dafs a')
    for statement in statements:
        print '"' + str(statement.tokens[0]) + '" isDML : ' + str(isDML(statement))
        print '"' + str(statement.tokens[0]) + '" isDDL : ' + str(isDDL(statement))
        print '"' + str(statement.tokens[0]) + '" isKeyword : ' + str(isKeyword(statement))
        print '"' + str(statement.tokens[0]) + '" isIdentifier : ' + str(isIdentifier(statement))
        print '"' + str(statement.tokens[0]) + '" isIdentifierList : ' + str(isIdentifierList(statement))
        print
    '''
    s='''where key1=value1 and key2 = value2 and key3="value3" and "key4"=value4 and "key5" = "value5";'''
    st = sqlparse.parse(s)[0]
    print st.tokens
    print
    sss = reformat_tokens(st)
    print sss
    for index in xrange(1, len(sss), 3):
        print index, sss[index]
