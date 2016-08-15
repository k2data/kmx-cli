#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sqlparse
import cli

num = str(random.randint(10000, 99999))
device_type = 'test_dt_' + num
device = 'test_d_' + num

sql = '''

select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts=1469672032196;

select describe(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>1469672032196 and ts<1469672032644;
select box(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196%2B08:00' and ts<'2016-07-28T10:13:52.644%2B08:00';
select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00';

select WCNVConver_chopper_igbt_temp,WCNVPwrReactInstMagf from GW150001 where iso > '2015-04-24T20:10:00.000%2B08:00' and iso < '2015-05-01T07:59:59.000%2B08:00';
select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'now-100w' and ts<'now';

'''.format(device_type=device_type,device=device)



if __name__ == '__main__':
    statements = sqlparse.parsestream(sql.replace('\n', ''), 'utf-8')
    cli.transfer('http://192.168.130.2/cloud/qa3/kmx/v2', statements)
