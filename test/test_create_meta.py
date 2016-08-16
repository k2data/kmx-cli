#!/usr/bin/env python
#encoding: utf-8

import random
import unittest
import sqlparse
import sys
import os
import time

cur_dir = os.path.abspath(os.path.dirname(__file__))
path = os.path.abspath(os.path.join(cur_dir, '../kmx_cli'))
sys.path.append(path)
import create,metadata,client,log


class Tester(unittest.TestCase):

    def setUp(self):
        log.primary('================================================== setUp ==================================================')
        self.url = 'http://192.168.130.2/cloud/qa3/kmx/v2'
        self.num = str(random.randint(10000, 99999))
        self.device_type = ['test_dt1_%s' % self.num, 'test_dt2_%s' % self.num]
        self.device = 'test_d_%s' % self.num
        self.execute('create deviceType ' + self.device_type[0] + '(s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)')

    def execute(self, sql, is_assert=False):
        statements = sqlparse.parse(sql, 'utf-8')
        if is_assert:
            for statement in statements:
                self.assertEqual(create.create(self.url, statement), True, 'failed with sql=[' + sql + ']')
        else:
            client.transfer(self.url, statements)

    def tearDown(self):
        time.sleep(20)
        log.primary('================================================== tearDown ==================================================')
        deletes = [
                    'drop device ' + self.device,
                    'drop devicetype ' + self.device_type[0],
                    'drop devicetype ' + self.device_type[1]
                  ]
        statements = sqlparse.parse(';'.join(deletes), 'utf-8')
        client.transfer(self.url, statements)

    def test_create_device(self):
        log.primary('================================================== test create device ==================================================')
        sql = 'create device ' + self.device + '(' + self.device_type[0] + ') tags(t1,t2,标签) attributes(属性 属性值,k2 v2)'
        self.execute(sql, is_assert=True)

    def test_create_device_type(self):
        log.primary('================================================== test create deviceType ==================================================')
        sql = 'create deviceType ' + self.device_type[1] + '(s1 String,s2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)'
        self.execute(sql, is_assert=True)


if __name__ == '__main__':
    unittest.main()
