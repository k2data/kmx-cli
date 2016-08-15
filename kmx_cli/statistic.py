#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas
import numpy
import pylab
import json
from request import get
import log

numpy.seterr(divide='ignore',invalid='ignore')


def parse_payload(payload, sensors):
    index = []
    values = {}
    for sensor in sensors:
        values[sensor] = []

    data_rows = json.loads(payload)['dataRows']
    for data_row in data_rows:
        if data_row.has_key('iso'):
            index.append(data_row['iso'])
        else:
            index.append(data_row['timestamp'])
        data_points = data_row['dataPoints']
        for data_point in data_points:
            sensor = data_point['sensor']
            if data_point.has_key('value') and data_point['value'] != 'null':
                values[sensor].append(data_point['value'])
            else:
                values[sensor].append(float("+inf"))
    return index, values


def get_data(sensors, values):
    data_type = 'float64'
    data = {}
    for sensor in sensors:
        data[sensor] = numpy.array(values[sensor], dtype=data_type)
    return data


def get_data_frame_data(payload, sensors):
    index, values = parse_payload(payload, sensors)
    data = get_data(sensors,values)
    return pandas.DataFrame(data=data, index=index, columns=sensors)


def describe(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    log.default(data_frame.describe())


def plot(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    data_frame.plot()
    pylab.show()


def box(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    # data_frame.boxplot(return_type='dict')
    data_frame.boxplot(return_type='axes')
    pylab.show()


if __name__ == '__main__':
    url = 'http://192.168.130.2/cloud/qa3/kmx/v2/data/data-rows?' +\
          'select={"sources":{"device":"C302D0_10",' + \
          '"sensors":["engineTemperature","xx","enginRotate"],' + \
          '"timeRange":{"start":{"iso":"1970-01-01T00:00:00.001-00:00"},"end":{"iso":"2016-08-15T09:44:55.687%2B08:00"}}}}' + \
          '&size=5'
    response = get(url)
    response_payload = response.text
    response.close()
    sensor_ids = ["engineTemperature", "xx", "enginRotate"]

    describe(response_payload, sensor_ids)
    plot(response_payload, sensor_ids)
    box(response_payload, sensor_ids)