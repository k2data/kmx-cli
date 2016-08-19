#!/usr/bin/env python
# -*- coding: utf-8 -*-

import log
from request import delete

charset = 'utf-8'


def drop(url, statement):
    ids = ''
    tokens = statement.tokens
    if len(tokens) < 3 or tokens[0].value.strip().lower() != 'drop':
        log.error('Error: Syntax error ,please check your input.')
        log.info('Usage: DROP {DEVICE | DEVICETYPE}  id [, id]...' )
        return

    params = tokens[2].value.strip().split(' ')
    path = params[0].lower()
    table_type = ''

    if path != 'device' and path != 'devicetype':
        log.error('Error: Syntax error ,please check your input.')
        log.info('Usage: DROP {DEVICE | DEVICETYPE}  id [, id]...')
        return
    if path == 'device':
        table_type='devices'
    if path == 'devicetype':
        table_type='device-types'

    if len(params) > 1:
        ids = str(params[1])

    if ids.endswith(','):
        ids = ids[:-1]

    for id in ids.split(','):
        uri = url + '/' + table_type + '/internal/' + id
        log.info(uri)
        response = delete(uri)
        if response.status_code == 200:
            log.warn("Warning: The drop command only change the device/device-type to inactive status, related data still exists in database,please delete them manually as needed.")
        log.primary('%s %s ' % (response.status_code,response.reason))
        response.close()


if __name__ == '__main__':
    import sqlparse
    statements = sqlparse.parse('drop devicetype dt_dWnkm_N_000_inst_000,dt_dWnkm_N_000_inst_001,dt_dWnkm_N_000_inst_001,')
    for statement in statements:
        print statement
        drop('http://192.168.130.2/cloud/qa3/kmx/v2', statement)
