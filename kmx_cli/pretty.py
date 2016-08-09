#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tabulate import tabulate
from colorama import Fore
import log

def pretty_page(pages):
    print 'total:%d    size:%d    pageNum:%d    pages:%d    pageSize:%d\n' % (pages['total'],pages['size'],pages['pageNum'],pages['pages'],pages['pageSize'])

def pretty_data_query(payload, format='psql'):
    ''' @author: Chang, Xue
        @param: query_result is a dict
        @param: fmt may be 'plain', 'simple', 'grid', 'fancy_grid',
                'psql', 'pipe', 'orgtbl', 'rst', 'html' etc
                 detail see https://pypi.python.org/pypi/tabulate
    '''
    result = []
    headers = ['device', 'time']
    non_exist = '-'  # show when key does not exist
    err_msg = payload['message']
    sensor_map = {}

    if 'dataRows' in payload.keys():
        keys = payload['dataRows'][0].keys()
        ts_key = 'iso' if 'iso' in keys else 'timestamp'
        recs = payload['dataRows']
        tmp_res = []
        # parse as single dict
        for rec in recs:
            print rec
            device = rec.get('device', non_exist)
            ts = rec.get(ts_key, non_exist)
            result_dict = {'device':device, 'time':ts }
            if 'dataPoints' in rec.keys():
                sensor_recs = rec['dataPoints']
                for sensor in sensor_recs:
                    sensor_name = sensor.get('sensor', non_exist)
                    if not sensor_map.has_key(sensor_name):
                        headers.append(sensor_name)
                    result_dict[sensor_name] = sensor.get('value', non_exist)
            tmp_res.append(result_dict)
        # align sensors
        for result_dict in tmp_res:
            row = []
            for key in headers:
                row.append(result_dict.get(key, ''))
            result.append(row)
        if result:
            print tabulate(result, headers, tablefmt=format)
    elif 'dataPoints' in payload.keys():
        keys = payload['dataPoints'][0].keys()
        ts_key = 'iso' if 'iso' in keys else 'timestamp'
        for rec in payload['dataPoints']:
            print rec
            sensor = rec.get('sensor', non_exist)
            index = sensor_map.get(sensor, 0)
            sensor_map[sensor] = sensor_map.get(sensor, 0) + 1
            if index == 0:
                headers.append(sensor)
            if index > len(result) - 1:
                result.append([rec['device'], rec.get(ts_key, non_exist), rec.get('value', non_exist)])
            else:
                result[index].append(rec.get('value', non_exist))
        if result:
            print tabulate(result, headers, tablefmt=format)

    if 'pageInfo' in payload:
        pages = payload['pageInfo']
        print 'size:%d    pageNum:%d    pageSize:%d\n' % (pages['size'],pages['pageNum'],pages['pageSize'])
    log.default(err_msg)

def pretty_meta_list(payload, action, format='psql'):
    if not action:
        print json.dumps(payload, sort_keys=True, indent=4) + '\n'
        return

    results = []
    if action == 'device-types':
        action = 'deviceTypes'
    lists = payload[action]

    if action == 'deviceTypes':
        headers = ['id','url']
        for data in lists:
            results.append((data['id'], data['url']))
        print tabulate(results, headers, tablefmt=format)
    else:
        headers = ['id','deviceTypeId','url','deviceTypeUrl']
        for data in lists:
            results.append((data['id'], data['deviceType']['id'], data['url'], data['deviceType']['url']))
        print tabulate(results, headers, tablefmt=format)

    pages = payload['pageInfo']
    if pages:
        pretty_page(pages)


def pretty_meta(payload, path, format='psql'):
    result = []
    rows = []
    sensors = []
    headers = payload.keys()

    if path in payload.keys():
        payload = payload[path];
        sensors = payload.pop('sensors')
        headers = payload.keys()

    for header in headers:
        rows.append(json.dumps(payload[header], ensure_ascii=False))
    result.append(tuple(rows))

    if sensors:
        sensor_rows = []
        keys = sensors[0].keys()
        if 'url' in keys:
           keys.remove('url')
        for sensor in sensors:
            row = []
            for key in keys:
                row.append(sensor[key])
            sensor_rows.append(tuple(row))
        print tabulate(sensor_rows, keys, tablefmt=format) + '\n'

    print tabulate(result, headers, tablefmt=format)
    print

def pretty_output_meta_all(payload, main_key, fmt='psql'):
    body = payload[main_key]
    headers = body[0].keys()
    result = []
    non_exist = '-'

    for single in body:
        row = []
        for key in headers:
            row.append(json.dumps(single.get(key, non_exist), ensure_ascii=False))
        result.append(row)
    if result:
        print tabulate(result, headers, tablefmt=fmt)
    if payload.has_key('pageInfo'):
        pretty_page(payload['pageInfo'])
    print
