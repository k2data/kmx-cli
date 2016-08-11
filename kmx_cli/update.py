#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from sqlparse.tokens import Keyword, Comparison, Whitespace
from sqlparse.sql import Identifier, IdentifierList, Where, Parenthesis
from sqlparse.sql import Comparison as sqlComparison
import log
import request
import pretty

tables = ['device', 'devicetype']


def strip_quotes(value):
    value = value.strip()
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]
    return value


def parse_where(token):
    # 判断是否是where
    if not isinstance(token, Where):
        log.error("Syntax error: " + token.value + '. expected where')
        return

    # 判断where条件长度
    tokens = token.tokens
    if len(tokens) not in [3, 4]:
        log.error("Syntax error: " + token.value)
        return

    # 判断where条件
    comparisons = tokens[2].tokens
    for parison in comparisons:
        if hasattr(parison, 'ttype') and parison.ttype is Whitespace:
            comparisons.remove(parison)

    if len(comparisons) != 3:
        log.error("Syntax error in where: " + token.value)
        return

    if comparisons[0].value.strip().lower != 'id':
        log.error("Syntax error in where : " + comparisons[0].value + '. expected <id>')
        return

    if comparisons[1].ttype is not Comparison or comparisons[1].value.strip() != '=':
        log.error("Syntax error in where : " + comparisons[1].value + '. expected <=>')
        return

    # 取出 = 后面的值，并去掉"或者'
    return strip_quotes(comparisons[2].value)


def get_tags(parenthesis):
    tokens = parenthesis.tokens
    tags = []
    for token in tokens:
        if isinstance(token, Identifier) or isinstance(token, IdentifierList):
            value_tokens = token.value.strip().split(',')
            for value in value_tokens:
                tags.append(strip_quotes(value))
    return tags


def get_attributes(parenthesis):
    tokens = parenthesis.tokens
    attributes = []
    for token in tokens:
        if isinstance(token, Identifier) or isinstance(token, IdentifierList):
            value_tokens = token.value.strip().split(',')
            for attribute in value_tokens:
                items = attribute.strip().split(' ')
                if len(items) < 2:
                    attributes.append(dict(name=strip_quotes(items[0])))
                else:
                    attributes.append(dict(name=strip_quotes(items[0]), attributeValue=strip_quotes(items[1])))
    return attributes


def parse_set_comparison(token, payload):
    if not isinstance(token, sqlComparison):
        log.error(' set 语法错误')
        return
    tokens = token.tokens
    key = tokens[0].value

    for i in range(1, len(tokens)):
        item = tokens[i]
        if item.ttype is Comparison:
            operator = item.value
            if operator != '=':
                log.error('Syntax error, unkown operator :' + operator)
                return
        elif item.ttype is Whitespace:
            continue
        else:
            if isinstance(item, Identifier):
                payload[key] = strip_quotes(item.value)
                '''
                单引号和双引号问题
                '''
            elif isinstance(item, Parenthesis):
                if key == 'tags':
                    payload[key] = get_tags(item)
            # elif hasattr(item,'ttype') and item.ttype is Single:
            #     payload[key] = item.value.replace("'", '')
                elif key == 'attributes':
                    payload[key] = get_attributes(item)
                else:
                    payload[key] = strip_quotes(item.value)
            else:
                log.error('Syntax error at: %s' % item)
                return
    return payload


def parse_set(token):
    payload = {}
    if isinstance(token, IdentifierList):
        tokens = token.tokens
        for t in tokens:
            if isinstance(t, sqlComparison):
                payload = parse_set_comparison(t, payload)
    elif isinstance(token, sqlComparison):
        payload = parse_set_comparison(token, payload)
    else:
        log.error(' set 语法错误parse_set')
    return payload


def parse_sql(tokens):
    primary = parse_where(tokens[8])
    payload = parse_set(tokens[6])
    payload['id'] = primary
    return primary, json.dumps(payload, ensure_ascii=False)


def update(url, statement):
    tokens = statement.tokens
    if len(tokens) != 9:
        log.error("Syntax error: " + str(tokens))
        return

    table = tokens[2].value.lower()
    if table not in tables:
        log.error('Syntax error: tableName should be in [' + ','.join(tables) + ']')
        return

    if not tokens[4].ttype is Keyword or tokens[4].value.lower() != 'set':
        log.error('Syntax error at : ' + tokens[4].value)
        return

    url_path = table + 's'
    key = 'device'
    if url_path == 'devicetypes':
        url_path = 'device-types'
        key = 'deviceType'

    primary, payload = parse_sql(tokens)
    if not primary or not payload:
        return

    uri = url + '/' + url_path + '/' + primary
    response = request.put(uri, payload=payload)

    log.default('put : %s\n%s' % (uri, payload))
    log.info('%s %s' % (response.status_code, response.reason))
    pretty.pretty_meta(json.loads(response.text),key)

    response.close()
