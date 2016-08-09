#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sqlparse
import cli

num = str(random.randint(10000, 99999))

sqls = [
    'create deviceType create_dt_' + num + '(s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)',
    'create device create_d_' + num + '(create_dt_' + num + ') tags(t1,t2) attributes(k1 v1,k2 v2)',

    # 'show devices',
    # 'show devices create_dt_' + num,
    # 'show devices non_existent_device',
    #
    # 'show device-types',
    # 'show device-types create_dt_' + num,
    # 'show device-types non_existent_deviceType',
    #
    # 'select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts=1469672032196',
    #
    # 'select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>1469672032196 and ts<1469672032644',
    # "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196%2B08:00' and ts<'2016-07-28T10:13:52.644%2B08:00'",
    # "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00'",
    #
    # "select WCNVConver_chopper_igbt_temp,WCNVPwrReactInstMagf from GW150001 where iso > '2015-04-24T20:10:00.000%2B08:00' and iso < '2015-05-01T07:59:59.000%2B08:00'",
    # "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'now-100w' and ts<'now'",

    # "import testdata/test.csv into import",
    # "import test.csv into import",
    # "import 'testdata/test.csv' into import",
    # "import '../build/data.csv' into import"
]

for sql in sqls:
    statements = sqlparse.parse(sql, 'utf-8')
    for statement in statements:
        cli.transfer('http://192.168.130.2/cloud/qa3/kmx/v2', statements)
