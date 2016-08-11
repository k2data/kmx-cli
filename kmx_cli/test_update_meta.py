#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sqlparse
import cli

num = str(random.randint(10000, 99999))
device_type = 'test_dt_' + num
device = 'test_d_' + num

sql = '''
update devicetype set tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where idx="{device_type}";
eguiesdf;
'''.format(device_type=device_type,device=device)


if __name__ == '__main__':
    statements = sqlparse.parsestream(sql.replace('\n', ''), 'utf-8')
    cli.transfer('http://192.168.130.2/cloud/qa3/kmx/v2', statements)
