#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from sqlparse.sql import Function, Parenthesis
from request import post
import identify
import log
from pretty import pretty_meta

value_types = ['BOOLEAN', 'INT', 'DOUBLE', 'FLOAT', 'LONG', 'STRING']


def parse_attr(payload, tokens):
    length = len(tokens)
    if length > 7:
        if not isinstance(tokens[6], Function):
            log.error("create Syntax error at: " + str(tokens[6]))
            return
        for i in range(6, length, 2):
            token = tokens[i]
            if isinstance(token, Function):
                key = tokens[i][0].value
                for t in token:
                    if isinstance(t, Parenthesis):
                        values = t.value[1:-1].split(',')
                        if key == 'tags':
                            lists = []
                            for value in values:
                                lists.append(value.strip())
                            payload['tags'] = lists
                        elif key == 'attributes':
                            lists = []
                            for value in values:
                                items = value.strip().split()
                                if len(items) >= 2:
                                    lists.append(dict(name=items[0], attributeValue=items[1]))
                                else:
                                    log.warn('attribute:' + items[0] + ' have no value...')
                                    lists.append(dict(name=items[0]))
                            payload['attributes'] = lists
                        else:
                            log.error("create Syntax error at: " + str(token) + '. Just allowed tags or attributes')
                            return
    return payload


def device_type_payload(tokens):
    columns = tokens[-1].value[1:-1].strip().split(',')
    sensors = []
    for column in columns:
        items = column.strip().split(' ')
        if len(items) < 2:
            log.error('sensor : ' + items[0] + ' should have valueType...')
            return
        value_type = items[1].upper()
        if value_type not in value_types:
            log.warn("sensor : " + items[0] + "'s valueType=" + value_type + ". That is not in [" + ",".join(value_types) + "] as KMX supported and will caused regist failed")
        sensor = dict(id=items[0], valueType=value_type)
        sensors.append(sensor)
    return dict(id=tokens[0].value, sensors=sensors)


def device_payload(tokens):
    parenthesis = tokens[-1].tokens
    if len(parenthesis[1].tokens) > 1:
        log.error("create Syntax error at: " + str(parenthesis) + ', device only can relate to one deviceType.')
        return
    return dict(id=tokens[0].value, deviceTypeId=parenthesis[1].value)


def create(url, state_ment):
    tokens = state_ment.tokens

    if not isinstance(tokens[4], Function):
        log.error("create Syntax error at: " + str(tokens[4]))
        # log.error("create Syntax error at: " + str(tokens[4]) + "\t" + str(sys._getframe().f_lineno))
        return

    path = tokens[2].value.lower() + 's'
    key = path[:-1]

    if path == 'devicetypes':
        path = 'device-types'
        key = 'deviceType'
    uri = url + '/' + path

    function_token = tokens[4].tokens
    if not isinstance(function_token[-1], Parenthesis):
        log.error("create Syntax error at: " + str(tokens))
        return

    if path == 'device-types':
        payload = device_type_payload(function_token)
    elif path == 'devices':
        payload = device_payload(function_token)
    else:
        log.error(' Table ERROR .. Table should be in [ deviceType ,device ]')
        return

    payload = parse_attr(payload, tokens)
    if not payload:
        return

    response = post(uri, json.dumps(payload))
    status_code = response.status_code
    if status_code == 201:
        log.default(str(status_code) + ' ' + response.reason + '\n')
        pretty_meta(json.loads(response.text), key)
    else:
        log.warn(str(status_code) + ' ' + response.reason + '\n' + response.text + '\n')
    response.close()

if __name__ == '__main__':
    import sqlparse
    url = 'http://localhost/cloud/local/kmx/v2'
    sql = 'create deviceType create_dt(s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)'
    statements = sqlparse.parse(sql, 'utf-8')
    for statement in statements:
        create(url, statement)
