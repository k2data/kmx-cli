#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sqlparse
import cli

num = str(random.randint(10000, 99999))
device_type = 'test_dt_' + num
device = 'test_d_' + num

sqls = [
    'create deviceType ' + device_type + '(s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)',
    'create deviceType update_' + device_type + '(s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)',
    'create device ' + device + '(' + device_type + ') tags(t1,t2,标签) attributes(属性 属性值,k2 v2)',

    'show devices',
    'show devices ' + device,
    'show devices non_existent_device',

    'show device-types',
    'show device-types ' + device_type,
    'show device-types non_existent_deviceType',

    'select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts=1469672032196',

    'select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>1469672032196 and ts<1469672032644',
    "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196%2B08:00' and ts<'2016-07-28T10:13:52.644%2B08:00'",
    "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00'",

    "select WCNVConver_chopper_igbt_temp,WCNVPwrReactInstMagf from GW150001 where iso > '2015-04-24T20:10:00.000%2B08:00' and iso < '2015-05-01T07:59:59.000%2B08:00'",
    "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'now-100w' and ts<'now'",

    "import testdata/test.csv into " + device_type,
    "import test.csv into " + device_type,
    "import 'testdata/test.csv' into " + device_type,
    "import '../build/data.csv' into " + device_type,

    'update devicetype set tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where id = "' + device_type+ '"',
    'update device set deviceTypeId=update_' + device_type + ' ,tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where id = "' + device + '"'
]

for sql in sqls:
    statements = sqlparse.parse(sql, 'utf-8')
    print 'execute :\t' + sql
    for statement in statements:
        cli.transfer('http://192.168.130.2/cloud/qa3/kmx/v2', statements)