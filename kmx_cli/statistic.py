#!/usr/bin/env python
# -*- coding: utf-8 -*-
import log
try:
    import pandas
    import numpy
    import pylab
except:
    raise Exception('statistic dependy on pandas. but pandas does not install on your system.\n' + "try 'sudo apt-get instal -y python-pandas' to install it")

from request import get


def is_number(value):
    try:
        float(value)
        return True
    except:
        return False


def parse_payload(payload, sensors):
    placeholder = None
    index = []
    values = {}
    for sensor in sensors:
        values[sensor] = []

    data_rows = payload['dataRows']
    for data_row in data_rows:
        if data_row.has_key('iso'):
            index.append(data_row['iso'])
        else:
            index.append(data_row['timestamp'])
        data_points = data_row['dataPoints']
        for data_point in data_points:
            sensor = data_point['sensor']
            value = placeholder if 'value' not in data_point.keys() else data_point['value']
            if value != 'null' and is_number(value):
                values[sensor].append(value)
            else:
                values[sensor].append(placeholder)
    return index, values


def get_data(sensors, values):
    numpy.seterr(all='ignore')
    data_type = 'float64'
    data = {}
    for sensor in sensors:
        data[sensor] = numpy.array(values[sensor], dtype=data_type)
    return data


def get_data_frame_data(payload, sensors):
    index, values = parse_payload(payload, sensors)
    data = get_data(sensors,values)
    data_frame = pandas.DataFrame(data=data, index=index, columns=sensors)
    # for sensor in sensors:
    #     data = data_frame[sensor]
    #     data = data.apply(lambda value: numpy.NaN if value == float('inf') else value)
    #     data_frame[sensor] = data_frame[data.notnull()]
    return data_frame


def describe(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    log.default(data_frame.describe())


def plot(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    data_frame.plot()
    pylab.show()


def box(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    data_frame.boxplot(return_type='dict')
    # data_frame.boxplot(return_type='axes')
    pylab.show()


def execute(payload, sensors, function):
    if function == 'describe':
        describe(payload, sensors)
    elif function == 'line':
        plot(payload, sensors)
    elif function == 'box':
        box(payload, sensors)
    else:
        log.error("do not support :" + function)


if __name__ == '__main__':
    url = 'http://192.168.130.2/cloud/qa3/kmx/v2/data/data-rows?' +\
          'select={"sources":{"device":"C30229_05",' + \
          '"sensors":["engineTemperature","xx","enginRotate","latitudeNum"],' + \
          '"timeRange":{"start":{"iso":"1970-01-01T00:00:00.001-00:00"},"end":{"iso":"2016-08-15T09:44:55.687%2B08:00"}}}}' + \
          '&size=5'
    import json
    response = get(url)
    response_payload = json.loads(response.text)
    response.close()
    sensor_ids = ["engineTemperature", "xx", "enginRotate","latitudeNum"]

    describe(response_payload, sensor_ids)
    plot(response_payload, sensor_ids)
    box(response_payload, sensor_ids)