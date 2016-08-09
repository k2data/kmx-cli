#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import sqlparse
from colorama import Back

import log
from pretty import pretty_meta, pretty_meta_list
from request import get, post, delete

charset = 'utf-8'


def query_meta(url,statement):
    tokens = statement.tokens
    if len(tokens) < 3 or tokens[0].value.strip().lower() != 'show':
        print Back.YELLOW + 'Please add table name in your sql. Table name show be in [devices ,device-type] ....' + Back.RESET
        return

    params = tokens[2].value.strip().split(' ')
    path = params[0].lower()

    if path != 'devices' and path != 'device-types':
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


def drop_meta(url,statement):
    tokens = statement.tokens
    if len(tokens) < 3 or tokens[0].value.strip().lower() != 'drop':
        print Back.YELLOW + 'Please add table name in your sql. Table name show be in [devices ,device-type] ....' + Back.RESET
        return

    params = tokens[2].value.strip().split(' ')
    path = params[0].lower()

    if path != 'devices' and path != 'device-types':
        print ' Usage : drop table_name [id] .   '
        print 'Table name show be in [ devices , device-type ] ....'
        return
    id = ''
    if len(params) > 1 :
        id = params[1]

    uri = url + '/' + path + '/internal/' + id
    log.info(uri)
    response = delete(uri)
    if not response.status_code==200:
       resopnse_payload = json.loads(response.text)
    else:
        # '{"message":"the '+path+' '+ id +' deleted","code":0}'
        resopnse_payload=json.loads('{"message":"the '+path+' '+ id +' deleted","code":0}')

    if len(params) > 1 :
        path = path[:-1]
        if '-' in path:
            path = 'deviceType'
        pretty_meta(resopnse_payload, path)
    else:
        pretty_meta_list(resopnse_payload, path)

def test_drop_meta(d):
     drop_meta('http://192.168.130.2/cloud/qa3/kmx/v2',d)

if __name__=='__main__':
    statements = sqlparse.parse('drop devices dt_dWnkm_N_000_inst_000')
    for s in statements:
        test_drop_meta(s)