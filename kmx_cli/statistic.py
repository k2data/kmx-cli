#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import pandas
    import numpy
    import pylab
    import matplotlib
    import matplotlib.pyplot as plt
except:
    raise Exception('statistic dependy on pandas. but pandas does not install on your system.\n' + "try 'sudo apt-get install -y python-pandas' to install it")

import log


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def not_empty(lists):
    for x in lists:
        if x:
            return True
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
        elif 'timestamp' in data_row:
            index.append(data_row['timestamp'])
        else:
            return None, None
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
    index.sort()
    if index and values:
        data = get_data(sensors, values)
        return pandas.DataFrame(data=data, index=index, columns=sensors)
    else:
        log.warn("query return 0 data point. skip statistic")
        return


# 快速地算出了均值、标准差、最小和最大值
def describe(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    log.default(data_frame.describe())


# 直方图
def hist(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    if data_frame is not None and not data_frame.empty:
        data_frame.hist(color='lightblue')
        # pylab.xlabel('sensor value')
        # pylab.ylabel('distribution')
        pylab.show()
        pylab.close()


# 直方图
def hist_normed(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    if data_frame is not None and not data_frame.empty:
        data_frame.hist(color='lightblue', normed=True)
        pylab.show()
        pylab.close()


# plot折线图
def plot(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    if data_frame is not None and not data_frame.empty:
        data_frame.plot()
        pylab.title('Timing diagram')
        pylab.xlabel('time')
        pylab.ylabel('value')
        # pylab.grid(axis='x', alpha=0.8)
        pylab.show()
        pylab.close()


# 箱图
def box_plot(payload, sensors):
    data_frame = get_data_frame_data(payload, sensors)
    if data_frame is not None and not data_frame.empty:
        data_frame.boxplot()
        pylab.show()
        pylab.close()


# 散列图scatter
def scatter(payload, sensors):
    """
    scatter()所绘制的散列图可以指定每个点的颜色和大小。
    scatter()的前两个参数是数组，分别指定每个点的X轴和Y轴的坐标。
    s参数指定点的大 小，值和点的面积成正比。它可以是一个数，指定所有点的大小；也可以是数组，分别对每个点指定大小。
    c参数指定每个点的颜色，可以是数值或数组。这里使用一维数组为每个点指定了一个数值。通过颜色映射表，每个数值都会与一个颜色相对应。默认的颜色映射表中蓝色与最小值对应，红色与最大值对应。当c参数是形状为(N,3)或(N,4)的二维数组时，则直接表示每个点的RGB颜色。
    marker参数设置点的形状，可以是个表示形状的字符串，也可以是表示多边形的两个元素的元组，第一个元素表示多边形的边数，第二个元素表示多边形的样式，取值范围为0、1、2、3。0表示多边形，1表示星形，2表示放射形，3表示忽略边数而显示为圆形。
    alpha参数设置点的透明度。
    lw参数设置线宽，lw是line width的缩写。
    facecolors参数为“none”时，表示散列点没有填充色
    """
    index, values = parse_payload(payload, sensors)
    if not index or not values:
        log.warn("query return 0 data point. skip statistic")
        return

    datas = get_data(sensors, values)
    if not datas:
        log.warn("query return 0 data point. skip statistic")
        return

    x = datas[sensors[0]]
    n = len(datas)
    fig, axes = plt.subplots(1, n - 1, figsize=(24, 8))

    if n <= 1:
        log.error('the contrast sensors must be more than one, but got [ %s ]' % ','.join(sensors))
        return

    if isinstance(axes, numpy.ndarray):
        for index in range(1, n):
            y = datas[sensors[index]]
            axes[index-1].scatter(x, y, alpha=0.5, cmap=plt.cm.hsv)
    elif isinstance(axes, matplotlib.axes.Subplot):
        y = datas[sensors[1]]
        if not_empty(y):
            axes.scatter(x, y, alpha=0.5, cmap=plt.cm.hsv)
    else:
        log.error('unsupport data type')
        plt.close()
        return
    plt.show()
    plt.close()


# 梯形图step()
def step(payload, sensors):
    index, values = parse_payload(payload, sensors)
    if not index or not values:
        log.warn("query return 0 data point. skip statistic")
        return

    datas = get_data(sensors, values)
    if not datas:
        log.warn("query return 0 data point. skip statistic")
        return

    x = datas[sensors[0]]
    n = len(datas)
    fig, axes = plt.subplots(1, n - 1, figsize=(24, 8))

    if n <= 1:
        log.error('the contrast sensors must be more than one, but got [ %s ]' % ','.join(sensors))
        return

    if isinstance(axes, numpy.ndarray):
        for index in range(1, n):
            y = datas[sensors[index]]
            axes[index-1].step(x, y, color='lightblue', lw=1, alpha=0.8)
    elif isinstance(axes, matplotlib.axes.Subplot):
        y = datas[sensors[1]]
        if not_empty(y):
            axes.step(x, y, color='lightblue', lw=1, alpha=0.8)
    else:
        log.error('unsupport data type')
        return

    plt.show()
    plt.close()


# 柱状图bar()
def bar(payload, sensors):
    """
    用每根柱子的长度表示值的大小，它们通常用来比较两组或多组值。
    bar()的第一个参数为每根柱子左边缘的横坐标;第二个参数为每根柱子的高度;第三个参数指定所有柱子的宽度,当第三个参数为序列时，可以为每根柱子指定宽度。bar()不自动修改颜色。
    """
    index, values = parse_payload(payload, sensors)
    if not index or not values:
        log.warn("query return 0 data point. skip statistic")
        return

    datas = get_data(sensors, values)
    if not datas:
        log.warn("query return 0 data point. skip statistic")
        return

    x = datas[sensors[0]]
    n = len(datas)
    fig, axes = plt.subplots(1, n - 1, figsize=(24, 8))

    if n <= 1:
        log.error('the contrast sensors must be more than one, but got [ %s ]' % ','.join(sensors))
        return

    if isinstance(axes, numpy.ndarray):
        for index in range(1, n):
            y = datas[sensors[index]]
            axes[index-1].bar(x, y, align="center", width=0.5/n, alpha=0.5)
    elif isinstance(axes, matplotlib.axes.Subplot):
        y = datas[sensors[1]]
        if not_empty(y):
            plt.ylabel(sensors[1])
            axes.bar(x, y, align="center", width=0.5/n, alpha=0.5)
    else:
        log.error('unsupport data type')
        return
    plt.xlabel(sensors[0])
    plt.show()
    plt.close()


# 填充图
def fill_between(payload, sensors):
    index, values = parse_payload(payload, sensors)
    if not index or not values:
        log.warn("query return 0 data point. skip statistic")
        return

    datas = get_data(sensors, values)
    if not datas:
        log.warn("query return 0 data point. skip statistic")
        return

    x = datas[sensors[0]]
    n = len(datas)
    fig, axes = plt.subplots(1, n - 1, figsize=(24, 8))

    if n <= 1:
        log.error('the contrast sensors must be more than one, but got [ %s ]' % ','.join(sensors))
        return

    if isinstance(axes, numpy.ndarray):
        for index in range(1, n):
            y = datas[sensors[index]]
            axes[index - 1].fill_between(x, y, color="green", alpha=0.5)
    elif isinstance(axes, matplotlib.axes.Subplot):
        y = datas[sensors[1]]
        if not_empty(y):
            axes.fill_between(x, y, color="green", alpha=0.5)
    else:
        log.error('unsupport data type')
        return


def execute(payload, sensors, function):
    if function == 'describe':
        describe(payload, sensors)
    elif function == 'plot':
        plot(payload, sensors)
    elif function == 'boxplot':
        box_plot(payload, sensors)
    elif function == 'hist':
        hist(payload, sensors)
    elif function == 'histf':
        hist_normed(payload, sensors)
    elif function == 'scatter':
        scatter(payload, sensors)
    elif function == 'step':
        step(payload, sensors)
    elif function == 'bar':
        bar(payload, sensors)
    elif function == 'fill':
        fill_between(payload, sensors)
    else:
        log.error("statistic do not support :" + function + '. Only support [describe, hist, histf, plot, boxplot, scatter, step, bar, fill]')


if __name__ == '__main__':
    import cli
    import sqlparse

    device = 'GW150008'
    # sensors = ['WCNVConver_setup_igbt2', 'WCNVConver_chopper_igbt_temp', 'xxx', 'WCNVConver_generator_capacitorstmpf', 'WCNVConver_setup_igbt1', 'WCNVConver_setup_igbt3', 'WCNVHzInstMagf']
    sensors = ['WCNVConver_setup_igbt2', 'WCNVConver_chopper_igbt_temp']
    #
    # sqls = ['select describe({sensors}) from {device} limit 286',
    #         'select hist({sensors}) from {device}  limit 286',
    #         'select histf({sensors}) from {device}  limit 286',
    #         'select plot({sensors}) from {device}  limit 286',
    #         'select boxplot({sensors}) from {device}  limit 286',
    #         'select scatter({sensors}) from {device}  limit 286',
    #         'select bar({sensors}) from {device}  limit 286',
    #         'select step({sensors}) from {device}  limit 286',
    #         'select fill({sensors}) from {device}  limit 286']
    # #
    # # # sqls = ['select scatter({sensors}) from {device}  limit 28']
    # for sql in sqls:
    #     statements = sqlparse.parsestream(sql.format(sensors=','.join(sensors), device=device), 'utf-8')
    #     cli.transfer('http://192.168.130.2/cloud/qa3/kmx/v2', statements)

    statements = sqlparse.parsestream("select scatter(enginRotate, engineTemperature,gsmSignal) from C2063B limit 100", 'utf-8')
    cli.transfer('http://218.56.128.30:16805/kmx/v2', statements)
