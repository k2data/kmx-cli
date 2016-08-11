#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import sqlparse
from colorama import Back

import log
from pretty import pretty_meta, pretty_meta_list
from request import get, post, delete

charset = 'utf-8'


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
        log.error('Error: Syntax error ,please check your input.')
        log.info('Usage: DROP {DEVICE | DEVICETYPE}  id [, id]...' )
        return

    params = tokens[2].value.strip().split(' ')
    path = params[0].lower()
    table_type=''
    if path != 'device' and path != 'devicetype':
        log.error('Error: Syntax error ,please check your input.')
        log.info('Usage: DROP {DEVICE | DEVICETYPE}  id [, id]...')
        return
    if path=='device':
        table_type='devices'
    if path=='devicetype':
        table_type='device-types'
    id = ''
    if len(params) > 1 :
        ids = str(params[1])
    if ids.endswith(','):
        ids=ids[:-1]
    for id in ids.split(','):
        uri = url + '/' + table_type + '/internal/' + id
        log.info(uri)
        response = delete(uri)
        if not response.status_code==200:
           resopnse_payload = json.loads(response.text)
        elif response.status_code==200:
            # '{"message":"the '+path+' '+ id +' deleted","code":0}'
            resopnse_payload=json.loads('{"message":"the '+path+' '+ id +' deleted.","code":0}')
            print
            log.warn("Warning: The drop command only change the device/device-type to inactive status, related data still exists in database,please delete them manually as needed.")
        response.close()
        if len(params) > 1 :

            pretty_meta(resopnse_payload, path)
        else:
            pretty_meta_list(resopnse_payload, path)

def ddl_operations(url,statement):
    tokens = statement.tokens
    if tokens[0].value.strip().lower() == 'drop':
        drop_meta(url,statement)
    elif tokens[0].value.strip().lower() == 'create':
        create_meta(url, statement)
    else:
        print 'Option should be in [ Create , Drop ]'


def test_drop_meta(d):
     drop_meta('http://192.168.130.2/cloud/qa3/kmx/v2',d)

if __name__=='__main__':
    statements = sqlparse.parse('drop devicetype dt_dWnkm_N_000_inst_000,dt_dWnkm_N_000_inst_001,dt_dWnkm_N_000_inst_001,')
    for s in statements:
        test_drop_meta(s)
