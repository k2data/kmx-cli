#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlparse
def get_batchparameters(sql):
    sql_str=str(sql).lstrip().rstrip()
    if sql_str.__contains__(' td'):
        operation_str=sql_str[sql_str.find(' td'):].rstrip().lstrip()
        terminator=operation_str[2]
        script_path=operation_str[3:].rstrip().lstrip()
    else:
        script_path = sql_str[6:].rstrip().lstrip()
    return script_path







def test():
    statements= sqlparse.parse("  source    /home/pc/Desktop/test.sql")
    for s in statements:
       print get_batchparameters(s)

if __name__=='__main__':

   test()



