#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import pandas
    import numpy
    import pylab
except:
    raise Exception('statistic dependy on pandas. but pandas does not install on your system.\n' + "try 'sudo apt-get install -y python-pandas' to install it")

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
        elif 'timestamp' in data_row :
            index.append(data_row['timestamp'])
        else:
            return None,None
        data_points = data_row['dataPoints']
        for data_point in data_points:
            sensor = data_point['sensor']
            if sensor not in ids:
                value = placeholder if 'value' not in data_point else data_point['value']
                if value is not None and value != 'null' and is_number(value):
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
    if index and values:
        data = get_data(sensors,values)
        return pandas.DataFrame(data=data, index=index, columns=sensors)
    else:
        log.warn("query return 0 data point. skip statistic")
        return


def describe(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    log.default(data_frame.describe())


def hist(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    if data_frame is not None and not data_frame.empty:
        data_frame.hist(color='lightblue')
        # pylab.xlabel('sensor value')
        # pylab.ylabel('distribution')
        pylab.show()
        pylab.close()


def plot(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    if data_frame is not None and not data_frame.empty:
        data_frame.plot()
        pylab.title('plot diagram')
        pylab.xlabel('time')
        pylab.ylabel('sensor value')



def box(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    if data_frame is not None and not data_frame.empty:
        # data_frame.boxplot(return_type='dict')
        data_frame.boxplot()
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
          '"sensors":["engineTemperature","xx","enginRotate","enginRotate","latitudeNum"],' + \
          '"timeRange":{"start":{"iso":"1970-01-01T00:00:00.001-00:00"},"end":{"iso":"2016-08-15T09:44:55.687%2B08:00"}}}}' + \
          '&size=20'
    url = 'http://192.168.130.2/cloud/qa3/kmx/v2/data/data-rows?' +\
          'select={"sources": {"device": "device_async_02_ZnMix", ' +\
          '"sensors": ["sensor_DOUBLE", "sensor_BOOLEAN", "sensor_FLOAT", "sensor_INT", "sensor_LONG", "sensor_STRING"], ' +\
          '"timeRange": {"start": {"iso": "1970-01-01T00:00:00.001-00:00"}, "end": {"iso": "2016-08-29T10:30:43.195%2B08:00"}}}}' +\
          '&page=3&size=100'
    import json
    print is_number('0.0')
    response = get(url)
    response_payload = json.loads(response.text)
    response.close()
    sensor_ids = ["engineTemperature", "xx", "enginRotate", "enginRotate", "latitudeNum"]
    sensor_ids = ["sensor_DOUBLE", "sensor_BOOLEAN", "sensor_FLOAT", "sensor_INT", "sensor_LONG", "sensor_STRING"]

    describe(response_payload, sensor_ids)
    plot(response_payload, sensor_ids)
    box(response_payload, sensor_ids)