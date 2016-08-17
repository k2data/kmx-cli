#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import pandas
    import numpy
    import pylab
except:
    raise Exception('statistic dependy on pandas. but pandas does not install on your system.\n' + "try 'sudo apt-get instal -y python-pandas' to install it")

from request import get
import log


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
        ids = []
        if 'iso' in data_row:
            index.append(data_row['iso'])
        else:
            index.append(data_row['timestamp'])
        data_points = data_row['dataPoints']
        for data_point in data_points:
            sensor = data_point['sensor']
            if sensor not in ids:
                value = placeholder if 'value' not in data_point else data_point['value']
                if value != 'null' and is_number(value):
                    values[sensor].append(value)
                else:
                    values[sensor].append(placeholder)
                ids.append(sensor)
    return index, values


def get_data(sensors, values):
    numpy.seterr(all='ignore')
    data = {}
    for sensor in sensors:
        data[sensor] = numpy.array(values[sensor])
    return data


def get_data_frame_data(payload, sensors):
    index, values = parse_payload(payload, sensors)
    data = get_data(sensors,values)
    data_frame = pandas.DataFrame(data=data, index=index, columns=sensors)
    return data_frame


def describe(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    log.default(data_frame.describe())


def hist(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    data_frame.hist(color='lightblue')
    # pylab.xlabel('sensor value')
    # pylab.ylabel('distribution')
    pylab.show()
    pylab.close()


def plot(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    data_frame.plot()
    # pylab.title('plot diagram')
    # pylab.xlabel('time')
    # pylab.ylabel('sensor value')
    pylab.show()
    pylab.close()


def box(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    data_frame.boxplot(return_type='dict')
    pylab.show()
    pylab.close()


def execute(payload, sensors, function):
    if function == 'describe':
        describe(payload, sensors)
    elif function == 'plot':
        plot(payload, sensors)
    elif function == 'boxplot':
        box(payload, sensors)
    elif function == 'hist':
        hist(payload, sensors)
    else:
        log.error("statistic do not support :" + function + '. Only support [describe, hist, plot, boxplot]')


if __name__ == '__main__':
    url = 'http://192.168.130.2/cloud/qa3/kmx/v2/data/data-rows?' +\
          'select={"sources":{"device":"C30229_05",' + \
          '"sensors":["engineTemperature","xx","enginRotate","latitudeNum"],' + \
          '"timeRange":{"start":{"iso":"1970-01-01T00:00:00.001-00:00"},"end":{"iso":"2016-08-15T09:44:55.687%2B08:00"}}}}' + \
          '&size=100'
    import json
    response = get(url)
    response_payload = json.loads(response.text)
    response.close()
    sensor_ids = ["engineTemperature", "xx","enginRotate", "enginRotate","latitudeNum"]

    # describe(response_payload, sensor_ids)
    plot(response_payload, sensor_ids)
    # box(response_payload, sensor_ids)