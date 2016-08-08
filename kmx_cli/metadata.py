#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colorama import Back
import json
from request import get, post
from pretty import pretty_meta, pretty_meta_list


charset = 'utf-8'


def query_meta(url,statement):
    tokens = statement.tokens
    if len(tokens) < 3 or tokens[0].value.strip().lower() != 'show':
        print Back.YELLOW + 'Please add table name in your sql. Table name show be in [devices ,device-type] ....' + Back.RESET
        return

    params = tokens[2].value.strip().split(' ')
    path = params[0].lower()

    if path != 'devices'.lower() and path != 'device-types':
        print ' Usage : show table_name [id] .   '
        print 'Table name show be in [ devices , device-type ] ....'
        return
    id = ''
    if len(params) > 1 :
        id = params[1]

    uri = url + '/' + path + '/' + id
    response = get(uri)
    resopnse_payload = json.loads(response.text)

    if len(params) > 1 :
        path = path[:-1]
        if '-' in path:
            path = 'deviceType'
        pretty_meta(resopnse_payload, path)
    else:
        pretty_meta_list(resopnse_payload, path)


def parse_attr(payload, tokens):
    length = len(tokens) + 1;
    if length > 4:
        for index in range(4, length, 2):
            key = tokens[index][0].value.strip()
            if key == 'tags':
                payload['tags'] = tokens[index][1].value.strip()[1:-1].split(',')
            elif key == 'attributes':
                attributes = []
                attrs = tokens[index][1].value[1:-1].split(',')
                for att in attrs:
                    attribute = {}
                    items = att.strip().split(' ')
                    attribute['name'] = items[0].strip()
                    if len(items) >= 2:
                        attribute['attributeValue'] = items[1].strip()
                    else:
                        print Back.YELLOW + 'attribute:' + items[0] + ' have no value...' + Back.RESET
                    attributes.append(attribute)
                payload['attributes'] = attributes
    return payload


def create_meta(url, statements):
    tokens = statements.tokens
    path = tokens[2].value.lower().strip()

    action = 'device'
    uri = url + '/' + path

    payload = {}
    if path == 'device-types':
        action = 'deviceType'
        sensors = []
        columns = tokens[4][1].value[1:-1].split(',')
        for column in columns:
            sensor = {}
            items = column.strip().split(' ')
            if len(items) < 2:
                print Back.RED + 'sensor : ' + items[0] + ' should have valueType...' + Back.RESET
                return
            sensor['id'] = items[0].strip()
            sensor['valueType'] = items[1].strip().upper()
            sensors.append(sensor)

            payload['id'] = tokens[4][0].value.strip()
            payload['sensors'] = sensors

    elif path == 'devices':
        payload['id'] = tokens[4][0].value.strip()
        payload['deviceTypeId'] = tokens[4][1].value[1:-1].strip()

    else:
        print ' Table ERROR .. Table show be in [ device-types ,devices ]'
        return
    payload = parse_attr(payload, tokens)

    response = post(uri, json.dumps(payload))
    response_payload = json.loads(response.text)
    pretty_meta(response_payload, action)
    response.close()
