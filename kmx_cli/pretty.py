#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tabulate import tabulate
from colorama import Fore


def pretty_page(pages):
    print 'total:%d    size:%d    pageNum:%d    pages:%d    pageSize:%d\n' % (pages['total'],pages['size'],pages['pageNum'],pages['pages'],pages['pageSize'])


def pretty(dict, format='psql'):
    ''' @param: query_result is a dict
        @param: fmt may be 'plain', 'simple', 'grid', 'fancy_grid',
                'psql', 'pipe', 'orgtbl', 'rst', 'html' etc
                detail see https://pypi.python.org/pypi/tabulate
    '''
    result = []
    headers = ['device', 'ts', 'sensorName', 'sensorValue']
    non_exist = '-'  # show when key does not exist
    err_msg = dict['message']

    if 'dataRows' in dict.keys():
        recs = dict['dataRows']
        for rec in recs:
            device = rec.get('device', non_exist)
            ts = rec.get('iso', non_exist)
            if 'dataPoints' in rec.keys():
                sensor_recs = rec['dataPoints']
                for sensor in sensor_recs:
                    result.append((device, ts, sensor.get('sensor', non_exist), sensor.get('value', non_exist)))
        if result:
            print tabulate(result, headers, tablefmt=format)
    elif 'dataPoints' in dict.keys():
        for rec in dict['dataPoints']:
            result.append((rec['device'], rec.get('timestamp', non_exist), rec.get('sensor', non_exist),rec.get('value', non_exist)))
        if result:
            print tabulate(result, headers, tablefmt=format)
    print Fore.YELLOW + err_msg

    if 'pageInfo' in dict:
        pages = dict['pageInfo']
        print 'size:%d    pageNum:%d    pageSize:%d\n' % (pages['size'],pages['pageNum'],pages['pageSize'])


def pretty_meta_list(payload, action, format='psql'):
    if not action:
        print json.dumps(payload, sort_keys=True, indent=4) + '\n'
        return

    results = []
    if action == 'device-types':
        action = 'deviceTypes'
    lists = payload[action]

    if action == 'deviceTypes' :
        headers = ['id','url']
        for data in lists:
            results.append((data['id'], data['url']))
        print tabulate(results, headers, tablefmt=format)
    else :
        headers =  ['id','url','deviceTypeId','deviceTypeUrl']
        for data in lists:
            results.append( (data['id'], data['url'], data['deviceType']['id'], data['deviceType']['url']) )
        print tabulate(results, headers, tablefmt=format)

    pages = payload['pageInfo']
    if pages:
        pretty_page(pages)


def pretty_meta(payload, path, format='psql'):
    result = []
    rows = []
    sensors = []
    headers = payload.keys()

    if path in payload.keys() :
        payload = payload[path];
        sensors = payload.pop('sensors')
        headers = payload.keys()

    for header in headers:
        rows.append(json.dumps(payload[header]))
    result.append(tuple(rows))

    if sensors:
        sensorRows = []
        keys = sensors[0].keys()
        for sensor in sensors:
            row = []
            for key in keys:
                row.append(sensor[key])
            sensorRows.append(tuple(row))
        print tabulate(sensorRows, keys, tablefmt=format)

    print tabulate(result, headers, tablefmt=format)
    print
