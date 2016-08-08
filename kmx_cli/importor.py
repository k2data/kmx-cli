#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import time
import arrow
from request import get, post
import log


default_time_format = 'YYYY-MM-DD HH:mm:ss'


def is_regist(url):
    response = get(url)
    status_code = response.status_code
    log.info(' get: ' + url + '  ' + str(status_code) + response.reason)
    return status_code == 200


def wait_published(url, key='device'):
    response = get(url)
    status_code = response.status_code
    status = 'PREPUBLISH'
    if status_code == 200:
        counter = 0
        response_payload = json.loads(response.text)
        status = response_payload[key]['status']
        response.close()

        while status != 'PUBLISHED' and counter < 30:
            time.sleep(2)
            response = get(url)
            response_payload = json.loads(response.text)
            status = response_payload[key]['status']
            response.close()
            log.info(' get ' + str(counter) + ' times : ' + url + '  ' + str(status_code) + response.reason + '\t' + status)
    log.info(' get: ' + url + '  ' + str(status_code) + response.reason + '\t' + status)


def device_payload(device, device_type_id):
    return json.dumps(dict(id=device, deviceTypeId=device_type_id))


def device_type_payload(id, sensor_ids, types):
    sensors = []
    for i in range(len(sensor_ids)):
        sensor = dict(id=sensor_ids[i], valueType=types[i].upper())
        sensors.append(sensor)
    return json.dumps(dict(id=id, sensors=sensors))


def regist(url, payload):
    log.info('POST:\t' + url + '\n' + payload)
    response = post(url, payload)
    log.info(response.reason + ' ' + str(response.status_code))
    log.info(response.text)
    response.close()


def get_sensor_value(value, vt):
    vt = vt.lower()
    if vt == 'double' or vt == 'float':
        return float(value)
    if vt == 'int':
        return int(value)
    if vt == 'long':
        return long(value)
    if vt == 'boolean':
        v = not value or value.lower() == 'n' or value.lower() == 'no' or value.lower() == '0'
        return not v
    return value


def get_payload(device, sample_time, sensors, types, values):
    sensor_data = []
    for i in range(len(sensors)):
        sensor_data.append(dict(sensorId=sensors[i], sensorValue=get_sensor_value(values[i], types[i])))
    return json.dumps(dict(deviceId=device, sampleTime=sample_time, sensorData=sensor_data))


def send_data(url, payload, success_writer, fail_writer, line, success, fail):
    response = post(url, payload)
    response_payload = response.text
    code = response.status_code

    if code == 202:
        success += 1
        success_writer.write(line + '\n' + payload + '\n' + response_payload + '\n' + str(code) + ' ' + response.reason + '\n\n')
    else:
        fail += 1
        fail_writer.write(line + '\n' + url + '\n' + payload + '\n' + response_payload + '\n' + str(code) + ' ' + response.reason + '\n\n')

    response.close()
    return success, fail


def print_report(total, success, warn, fail, drop):
    log.primary('import report : total=%i  success=%i  warn=%i  fail=%i  drop=%i' % (total, success, warn, fail, drop))


def send_iso(url, csv, sensors, types):
    total, success, fail, warn, drop, size = 0, 0, 0, 0, 0, len(sensors) + 2

    success_writer = open(csv.name + '.success.log', 'w')
    drop_writer = open(csv.name + '.drop.log', 'w')
    warn_writer = open(csv.name + '.warn.log', 'w')
    fail_writer = open(csv.name + '.fail.log', 'w')

    line = csv.readline().strip()
    while line:
        total += 1
        items = line.split(',')

        if len(items) < size:
            drop += 1
            drop_writer.write(line)
        elif len(items) >= size:
            payload = get_payload(items[0], dict(iso=items[1]), sensors, types, items[2:])
            success, fail = send_data(url, payload, success_writer, fail_writer, line, success, fail)

            if len(items) > size:
                warn += 1
                warn_writer.write(line + '\n')

        line = csv.readline().strip()

    success_writer.close()
    drop_writer.close()
    warn_writer.close()
    fail_writer.close()
    print_report(total, success, warn, fail, drop)


def send_timestamp(url, csv, sensors, types):
    total, success, fail, warn, drop, size = 0, 0, 0, 0, 0, len(sensors) + 2

    success_writer = open(csv.name + '.success.log', 'w')
    drop_writer = open(csv.name + '.drop.log', 'w')
    warn_writer = open(csv.name + '.warn.log', 'w')
    fail_writer = open(csv.name + '.fail.log', 'w')

    line = csv.readline().strip()
    while line:
        total += 1
        items = line.split(',')

        if len(items) < size:
            drop += 1
            drop_writer.write(line)
        elif len(items) > size:
            warn += 1
            warn_writer.write(line)
        else:
            payload = get_payload(items[0],  dict(timestamp=long(items[1])), sensors, types, items[2:])
            success, fail = send_data(url, payload, success_writer, fail_writer, line, success, fail)
        line = csv.readline().strip()

    success_writer.close()
    drop_writer.close()
    warn_writer.close()
    fail_writer.close()

    print_report(total, success, warn, fail, drop)


def send_time(url, csv, time_format, sensors, types):
    total, success, fail, warn, drop, size = 0, 0, 0, 0, 0, len(sensors) + 2

    success_writer = open(csv.name + '.success.log', 'w')
    drop_writer = open(csv.name + '.drop.log', 'w')
    warn_writer = open(csv.name + '.warn.log', 'w')
    fail_writer = open(csv.name + '.fail.log', 'w')

    line = csv.readline().strip()
    while line:
        total += 1
        items = line.split(',')

        if len(items) < size:
            drop += 1
            drop_writer.write(line)
        elif len(items) > size:
            warn += 1
            warn_writer.write(line)
        else:
            iso = str(arrow.get(items[1], time_format))
            payload = get_payload(items[0], dict(iso=iso), sensors, types, items[2:])
            success, fail = send_data(url, payload, success_writer, fail_writer, line, success, fail)
        line = csv.readline().strip()

    success_writer.close()
    drop_writer.close()
    warn_writer.close()
    fail_writer.close()

    print_report(total, success, warn, fail, drop)


def usage():
    log.default("Usage : import '${csvfile}' into ${deviceType}")
    log.default("file path show be quoted in ' '")


def parse_sql(statement):
    items = str(statement).split(' ')
    tokens = statement.tokens

    if len(tokens) < 7:
        log.error('import Syntax error ...')
        usage()
        return

    if len(items) < 2 or not items[1].startswith('\''):
        usage()
        return

    path = tokens[2].value[1:-1]
    if not os.path.isfile(path):
        log.error('file: ' + path + ' not found')
        return

    into = tokens[4].value.encode("utf-8").strip()
    if into.lower() != 'into':
        log.error('import Syntax error : <' + into + '>' + into + '. do you mean "into" ?')
        usage()
        return
    return path, tokens[6].value.encode("utf-8").strip()


def parse_heads(csv, path):
    line = csv.readline().strip()
    # 解析第一行,拿到时间标示和sensor信息
    if line:
        items = line.split(',')
        if len(items) < 3:
            log.warn('empty errors, skip import ...')
            return
        time_str = items[1]
        sensors = items[2:]
    else:
        log.warn('empty file: ' + path + '. skip import ...')
        return

    # 解析第二行,拿到device,时间格式和sensor信息
    line = csv.readline().strip()
    if line:
        items = line.split(',')
        if len(items) < 3:
            log.warn('empty valueTypes, skip import ...')
            return
        device = items[0]
        time_format = items[1]
        types = items[2:]
    return sensors, device, time_str, time_format, types


def run(url, statement):
    items = parse_sql(statement)
    if not items or len(items) < 2:
        return

    path, device_type = items

    csv = open(path, 'r')
    headers = parse_heads(csv, path)
    if not headers or len(headers) < 2:
        csv.close()
        return

    sensors, device, time_str, time_format,types = headers

    #  检查device-type 和 devices是否注册，没有则自动注册
    if not is_regist(url + '/device-types/' + device_type):
        log.primary('deviceType：' + device_type + " doesn't be registered, will regist automatically")
        regist(url + '/device-types',device_type_payload(device_type, sensors, types))
        wait_published(url + '/device-types/' + device_type,key='deviceType')

    if not is_regist(url + '/devices/' + device):
        log.primary('device：' + device + " doesn't be registered, will regist automatically")
        regist(url + '/devices',device_payload(device, device_type))
        wait_published(url + '/devices/' + device)

    log.default('.....................start import ')
    post_data_url = url + '/channels/devices/data'
    if time_str.lower() == 'iso':
        send_iso(post_data_url, csv, sensors, types)
    elif time_str.lower() == 'ts' or time == 'timestamp':
        send_timestamp(post_data_url, csv, sensors, types)
    else:
        send_time(post_data_url, csv, time_format, sensors, types)

    csv.close()
    log.default('.....................finished import')
