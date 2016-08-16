#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tabulate import tabulate
from colorama import Fore
import log


def pretty_page(pages):
    print 'total:%d    size:%d    pageNum:%d    pages:%d    pageSize:%d\n' % (pages['total'],pages['size'],pages['pageNum'],pages['pages'],pages['pageSize'])


def draw_table(rows, headers, fmt='psql', path=None):
    if not rows:
        print 'return 0 record.'
    elif fmt == 'csv' and path:
        output = open(path, 'w')
        output.write(','.join(headers) + '\n')
        for row in rows:
            output.write(','.join([str(i) for i in row]) + '\n')
        output.close()
    else:
        print tabulate(rows, headers, tablefmt=fmt)


def pretty_data_query(payload, fmt='psql', path=None):
    ''' @author: Chang, Xue
        @param: query_result is a dict
        @param: fmt may be 'json', 'plain', 'simple', 'grid', 'fancy_grid',
                'psql', 'pipe', 'orgtbl', 'rst', 'html' etc
                detail see https://pypi.python.org/pypi/tabulate
        Note: 范围查询可能有重复数据， 单设备-传感器时间点查询只返回一行
    '''
    if format == 'json':
        print json.dumps(payload, sort_keys=True, indent=4)
        return

    result = []
    headers = ['device', 'time']
    non_exist = ''  # show when key does not exist
    sensor_map = {}

    if 'dataRows' in payload.keys(): # 范围查询
        keys = payload['dataRows'][0].keys()
        ts_key = 'iso' if 'iso' in keys else 'timestamp'

        recs = payload['dataRows']
        tmp_res = []
        # parse as single dict
        for rec in recs:
            device = rec.get('device', non_exist)
            ts = rec.get(ts_key, non_exist)
            result_dict = {'device':device, 'time':ts }
            if 'dataPoints' in rec.keys():
                sensor_recs = rec['dataPoints']
                for sensor in sensor_recs:
                    sensor_name = sensor.get('sensor', non_exist)
                    if not sensor_name in headers:
                        headers.append(sensor_name)
                    result_dict[sensor_name] = sensor.get('value', non_exist)
            tmp_res.append(result_dict)
        # align sensors
        for result_dict in tmp_res:
            row = []
            for key in headers:
                row.append(result_dict.get(key, '')) #如果该行没有该sensor补空
            result.append(row)
        draw_table(result, headers, fmt, path)
    elif 'dataPoints' in payload.keys(): #单设备-传感器时间点查询
        keys = payload['dataPoints'][0].keys()
        ts_key = 'iso' if 'iso' in keys else 'timestamp'
        row = []

        for rec in payload['dataPoints']:
            if not row:
                row = [rec['device'], rec.get(ts_key, non_exist)]
            sensor = rec.get('sensor', non_exist)
            headers.append(sensor)
            row.append(rec.get('value', non_exist))
        result.append(row)
        draw_table(result, headers, fmt, path)

    if 'pageInfo' in payload:
        pages = payload['pageInfo']
        print 'size:%d    pageNum:%d    pageSize:%d\n' % (pages['size'],pages['pageNum'],pages['pageSize'])
    if payload['code'] == 0:
        log.default(payload['message'])
    else:
        log.error(payload['message'])
    return payload['code']


def pretty_meta_list(payload, action, fmt='psql'):
    ''' query all devices or device-types
        @action: devices, deviceTypes
    '''
    if format == 'json':
        print json.dumps(payload, sort_keys=True, indent=4)
        return

    results = []
    if action == 'device-types':
        action = 'deviceTypes'
    lists = payload[action]

    if action == 'deviceTypes':
        headers = ['id','url']
        for data in lists:
            results.append((data['id'], data['url']))
    else:
        headers = ['id','deviceTypeId','url','deviceTypeUrl']
        for data in lists:
            results.append((data['id'], data['deviceType']['id'], data['url'], data['deviceType']['url']))
    draw_table(results, headers, fmt)

    pages = payload['pageInfo']
    if pages and pages['total'] != 0:
        pretty_page(pages)


def pretty_meta(dict_payload, path, fmt='psql'):
    ''' create/query single device or device-types
        @path: deviceType, device
    '''
    if format == 'json':
        print json.dumps(dict_payload, sort_keys=True, indent=4)
        return

    result = []
    rows = []
    sensors = []
    headers = dict_payload.keys()

    if path in dict_payload.keys():
        payload = dict_payload[path]
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
        draw_table(sensor_rows, keys, fmt)

    draw_table(result, headers, fmt)
