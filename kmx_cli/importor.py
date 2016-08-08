#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import time
from colorama import Back
from request import get, post


def is_registed(url):
    response = get(url)
    status_code = response.status_code
    return status_code == 200


def wait_published(url, key='device'):
    response = get(url)
    status_code = response.status_code
    if status_code == 200:
        counter = 0
        response_payload = json.loads(response.text)
        response.close()

        while response_payload[key]['status'] != 'PUBLISHED' and counter < 30:
            time.sleep(2)
            response = get(url)
            response_payload = json.loads(response.text)
            response.close()


def device_payload(id, deviceTypeId):
    return json.dumps(dict(id=id, deviceTypeId=deviceTypeId))


def device_type_payload(id, sensor_ids, types):
    sensors = []
    for i in range(len(sensor_ids)):
        sensor = dict(id=sensor_ids[i], valueType=types[i].upper())
        sensors.append(sensor)
    return json.dumps(dict(id=id,sensors=sensors))


def regist(url, payload):
    print url
    print payload
    response = post(url, payload)
    print response.text
    response.close()


def get_sensor_value(value, vt):
    vt = vt.lower()
    if vt == 'double' or vt == 'float':
        return float(value)
    if vt == 'int':
        return  int(value)
    if vt == 'long':
        return  long(value)
    if vt == 'boolean':
        v = not value or value.lower() == 'n' or value.lower() == 'no' or value.lower() == '0'
        return not v
    return value


def get_payload(device, sampleTime, sensors, types, values):
    payload = {}
    datas = []
    for i in range(len(sensors)):
        data = {}
        data['sensorId'] = sensors[i]
        data['sensorValue'] = get_sensor_value(values[i], types[i])
        datas.append(data)

    payload['deviceId'] = device
    payload['sampleTime'] = sampleTime
    payload['sensorData'] = datas
    payload['deviceId'] = device

    return json.dumps(payload)


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
    print 'import report : total=%i  success=%i  warn=%i  fail=%i  drop=%i' % (total, success, warn, fail, drop)


def send_iso(url, csv, sensors, types):
    total = 0; success = 0; fail = 0; warn = 0; drop = 0;
    size = len(sensors) + 2

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
            sampleTime = {}
            sampleTime['iso'] = items[1]

            payload = get_payload(items[0], sampleTime, sensors, types, items[2:])
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
    total = 0; success = 0; warn = 0; fail = 0; drop = 0;
    size = len(sensors) + 2

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
            sampleTime = {}
            sampleTime['timestamp'] = long(items[1])

            payload = get_payload(items[0], sampleTime, sensors, types, items[2:])
            success, fail = send_data(url, payload, success_writer, fail_writer, line, success, fail)
        line = csv.readline().strip()

    success_writer.close()
    drop_writer.close()
    warn_writer.close()
    fail_writer.close()

    print_report(total, success, warn, fail, drop)


def send_time(url, csv, time_format, sensors, types):
    total = 0; success = 0; warn = 0; fail = 0; drop = 0;
    size = len(sensors) + 2

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
            sampleTime = {}
            sampleTime['iso'] = items[1] + time_format

            payload = get_payload(items[0], sampleTime, sensors, types, items[2:])
            success, fail = send_data(url, payload, success_writer, fail_writer, line, success, fail)
        line = csv.readline().strip()

    success_writer.close()
    drop_writer.close()
    warn_writer.close()
    fail_writer.close()

    print_report(total, success, warn, fail, drop)


def file_checker(csv):
    # size = 0  # 列数
    # sensors = []; types = []
    #
    # time = ''; time_format = ''
    #
    # line = csv.readline()
    #
    # # 解析第一行,拿到时间标示和sensor信息
    # if line:
    #     items = line.split(',')
    #     if len(items) < 3:
    #         csv.close()
    #         print Back.YELLOW + 'empty errors, skip import ...' + Back.RESET
    #         return
    #     size = len(items)
    #     time = items[1]
    #     sensors = items[2:]
    # else:
    #     csv.close()
    #     print Back.YELLOW + 'empty file: ' + path + '. skip import ...' + Back.RESET
    #     return
    #
    # # 解析第一行,拿到时间格式和sensor信息
    # line = csv.readline()
    # if line:
    #     items = line.split(',')
    #     if len(items) < 3:
    #         csv.close()
    #         print Back.YELLOW + 'empty errors, skip import ...' + Back.RESET
    #         return
    #     time_format = items[1]
    #     types = items[2:]
    return


def usage():
    print "Usage : import '${csvfile}' into ${deviceType}"
    print "file path show be quoted in ' '"


def parse_sql(statement):
    items = str(statement).split(' ')
    tokens = statement.tokens

    if len(tokens) < 7:
        print Back.RED + 'import Syntax error ...' + Back.RESET
        usage()
        return

    if len(items) < 2 or not items[1].startswith('\''):
        print Back.YELLOW + "file path show be quoted in ''" + Back.RESET
        usage()
        return

    path = tokens[2].value[1:-1];
    if not os.path.isfile(path):
        print Back.RED + 'file: ' + path + ' not found' + Back.RESET
        return

    into = tokens[4].value.encode("utf-8").strip()
    if into.lower() != 'into':
        print Back.RED + 'import Syntax error : <' + into + '>' + into + Back.RESET
        usage()
        return
    return path, tokens[6].value.encode("utf-8").strip()


def run(url, statement):
    items = parse_sql(statement)
    if len(items) < 2:
        return

    path, device_type = items()

    csv = open(path, 'r')

    line = csv.readline().strip()
    # 解析第一行,拿到时间标示和sensor信息
    if line:
        items = line.split(',')
        if len(items) < 3:
            csv.close()
            print Back.YELLOW + 'empty errors, skip import ...' + Back.RESET
            return
        time = items[1]
        sensors = items[2:]
    else:
        csv.close()
        print Back.YELLOW + 'empty file: ' + path + '. skip import ...' + Back.RESET
        return

    # 解析第二行,拿到device,时间格式和sensor信息
    line = csv.readline().strip()
    if line:
        items = line.split(',')
        if len(items) < 3:
            csv.close()
            print Back.YELLOW + 'empty errors, skip import ...' + Back.RESET
            return
        device = items[0]
        time_format = items[1]
        types = items[2:]

    #  检查device-type 和 devices是否注册，没有则自动注册
    if not is_registed(url + '/device-types/' + device_type):

        regist(url + '/device-types',device_type_payload(device_type, sensors, types))
        wait_published(url + '/device-types/' + device_type,key='deviceType')

    if not is_registed(url + '/devices/' + device):
        regist(url + '/devices',device_payload(device, device_type))
        wait_published(url + '/devices/' + device)

    post_data_url = url + '/channels/devices/data'
    if time.lower() == 'iso':
        send_iso(post_data_url, csv, sensors, types)
    elif time.lower() == 'ts' or time == 'timestamp':
        send_timestamp(post_data_url, csv, sensors, types)
    else:
        send_time(post_data_url, csv, time_format, sensors, types)

    csv.close()
