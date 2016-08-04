#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlparse
from cli import cli

client = cli()
client.url = 'http://192.168.130.2/cloud/qa3/kmx/v2'

sqls = [
    'show devices',
    'show device-types',

    'create device-types test_create_010(s1 String,s2 Float) tags(t1,t2) attributes(k1 v1,k2 v2)',
    'create devices text_d(dt_sync_01_dWavQ) tags(t1,t2) attributes(k1 v1,k2 v2)',

    'show devices text_d',
    'show device-types dt_sync_01_dWavQ',
    
    'select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>1469672032196 and ts<1469672032644',
    "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196%2B08:00' and ts<'2016-07-28T10:13:52.644%2B08:00'",
    'select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts=1469672032196',
    "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00'",
    "select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'now-100w' and ts<'now'"
       ]


for sql in sqls:
    parsed = sqlparse.parse(sql)
    client.transfer(parsed)

