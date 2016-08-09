#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import time
import arrow
from request import get, post
import log


def is_regist(url):
    response = get(url)
    status_code = response.status_code
    log.info(' get: ' + url + '  ' + str(status_code) + ' ' + response.reason)
    return status_code == 200


def regist(url, payload):
    log.default('POST:\t' + url + '\n' + payload)
    response = post(url, payload)
    status_code = response.status_code

    log.default(response.reason + ' ' + str(response.status_code))
    # log.default(response.text)
    response.close()
    return status_code == 201


def wait_published(url, key='device'):
    response = get(url)
    status_code = response.status_code
    status = ''
    if status_code == 200:
        counter = 0
        response_payload = json.loads(response.text)
        status = response_payload[key]['status']
        response.close()

        while status != 'PUBLISHED' and counter < 30:
            time.sleep(2)
            counter += 1
            response = get(url)
            response_payload = json.loads(response.text)
            status = response_payload[key]['status']
            response.close()
            log.default(' get ' + str(counter) + ' times : ' + url + '  ' + str(status_code) + ' ' + response.reason + '\t' + status)
    log.info(' get: ' + url + '  ' + str(status_code) + ' ' + response.reason + '\t' + status)
    return status == 'PUBLISHED'


def device_payload(device, device_type_id):
    return json.dumps(dict(id=device, deviceTypeId=device_type_id))


def device_type_payload(device, sensor_ids, types):
    sensors = []
    for i in range(len(sensor_ids)):
        sensor = dict(id=sensor_ids[i], valueType=types[i].upper())
        sensors.append(sensor)
    return json.dumps(dict(id=device, sensors=sensors))


def get_iso(value, time_format="YYYY-MM-DD'T'HH:mm:ss.SSSZ"):
    return dict(iso=value)


def get_timestamp(value, time_format='timestamp'):
    return dict(timestamp=long(value))


def get_custom_time(value, time_format):
    return dict(iso=str(arrow.get(value, time_format)))


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


def post_data(url, payload, success_writer, fail_writer, line, success, fail):
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


def send_data(url, csv, sensors, types, method, time_format):
    total, success, fail, drop, size = 0, 0, 0, 0, len(sensors) + 2

    success_writer = open(csv.name + '.success.log', 'w')
    drop_writer = open(csv.name + '.drop.log', 'w')
    fail_writer = open(csv.name + '.fail.log', 'w')

    line = csv.readline().strip()
    while line:
        total += 1
        items = line.split(',')

        if len(items) == size:
            simple_time = method(items[1], time_format=time_format)
            payload = get_payload(items[0], simple_time, sensors, types, items[2:])
            success, fail = post_data(url, payload, success_writer, fail_writer, line, success, fail)
        else:
            drop += 1
            drop_writer.write(line)
        line = csv.readline().strip()

    success_writer.close()
    drop_writer.close()
    fail_writer.close()
    log.primary('import report : total=%i  success=%i  fail=%i  drop=%i' % (total, success, fail, drop))


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


def parse_description(csv, path):
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
    description = parse_description(csv, path)
    if not description or len(description) < 2:
        csv.close()
        return
    sensors, device, time_mark, time_format, types = description

    #  检查device-type 和 devices是否注册，没有则自动注册
    log.default(' check if deviceType:' + device_type + ' is registed and PUBLISHED')
    if not is_regist(url + '/device-types/' + device_type):
        log.primary(' deviceType：' + device_type + " doesn't be registered, will regist automatically")
        regist(url + '/device-types',device_type_payload(device_type, sensors, types))
    success = wait_published(url + '/device-types/' + device_type,key='deviceType')

    log.default(' check if device:' + device + ' is registed and PUBLISHED')
    if success and not is_regist(url + '/devices/' + device):
        log.primary(' device：' + device + " doesn't be registered, will regist automatically")
        regist(url + '/devices',device_payload(device, device_type))
    success = wait_published(url + '/devices/' + device)

    if success:
        log.default('.....................start import ')
        post_data_url = url + '/channels/devices/data'

        if time_mark.lower() == 'iso':
            method = get_iso
        elif time_mark.lower() == 'ts' or time == 'timestamp':
            method = get_timestamp
        else:
            method = get_custom_time

        send_data(post_data_url, csv, sensors, types, method, time_format)
        csv.close()
        log.default('.....................finished import')
    else:
        log.error(' deviceType:' + device_type + ' or device:' + device + ' can not be synchronized into system. Please check if KMX is running in normal state')