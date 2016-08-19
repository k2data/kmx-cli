#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sqlparse
import cli

num = str(random.randint(10000, 99999))
device_type = 'test_dt_' + num
device = 'test_d_' + num

sql = '''create deviceType {device_type} (s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2);
create deviceType update_{device_type} (s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2);
create device {device}({device_type}) tags(t1,t2,标签) attributes(属性 属性值,k2 v2);

show devices;
show devices {device};
show device {device};
show device non_existent_device;
show devices like GW150020;
show devices like GW1500%;
show devices where devicetype=gw_dt_1;

show devicetypes;
show devicetypes {device_type};
show devicetype {device_type};
show devicetype non_existent_deviceType;
show devicetypes like gw_dt_1;
show devicetypes like gw*;

select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts=1469672032196;

select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>1469672032196 and ts<1469672032644;
select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00';
select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00';

select WCNVConver_chopper_igbt_temp,WCNVPwrReactInstMagf from GW150001 where iso > '2015-04-24T20:10:00' and iso < '2015-05-01 07:59';
select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts>'now-100w' and ts<'now';

select describe(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts=1469672032196;

select describe(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>1469672032196 and ts<1469672032644;
select hist(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00';
select plot(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00';
select boxplot(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00';

import testdata/test.csv into import_{device_type};
import test.csv into import_{device_type};
import 'testdata/test.csv' into import_{device_type};
import '../build/data.csv' into import_{device_type};

update devicetype set tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where id = "{device_type}";
update device set deviceTypeId=update_{device_type}, tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where id = "{device}";

drop device xx;
drop device {device};
drop devicetype {device_type};

eguiesdf;
'''.format(device_type=device_type,device=device)


if __name__ == '__main__':
    statements = sqlparse.parsestream(sql.replace('\n', ''), 'utf-8')
    cli.transfer('http://192.168.130.2/cloud/qa3/kmx/v2', statements)
