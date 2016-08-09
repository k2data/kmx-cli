#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import sqlparse

import cli
import log


def get_batchparameters(sql):
    sql_str = str(sql).lstrip().rstrip()
    if sql_str.__contains__(' td'):
        operation_str = sql_str[sql_str.find(' td'):].rstrip().lstrip()
        terminator = operation_str[2]
        script_path = operation_str[3:].rstrip().lstrip()
    else:
        script_path = sql_str[6:].rstrip().lstrip()
    return script_path


def get_allfilepath(path):
    files = []
    for fpathe, dirs, fs in os.walk(path):
        for f in fs:
            if not f.endswith('~'):
                files.append(os.path.join(fpathe, f))
    return files


def batch_exec(url,sql):
    if str(sql).rstrip().lstrip().upper()=='SOURCE':
        log.error('Please enter at least one script path after the keyword "SOURCE"')
        log.info('Usage: SOURCE Script1,Script2...')
        return
    script_path = get_batchparameters(sql)
    if (script_path).endswith(','):
        script_path = script_path[:-1]
    paths = script_path.split(',')
    for path in paths:
        if os.path.exists(path.lstrip().rstrip()):
            if os.path.isfile(path.lstrip().rstrip()):
                file_handler = open(path.lstrip().rstrip())
                for line in file_handler:
                    if line.startswith('#') or line.startswith('--') or line[:7].upper()=='SOURCE ':
                        continue
                    parsed = sqlparse.parse(line[:-1])
                    log.info(line[:-1])
                    cli.transfer(url,parsed)
                file_handler.close()
            elif os.path.isdir(path.lstrip().rstrip()):
                files = get_allfilepath(path.lstrip().rstrip())
                for file in files:
                    if os.path.isfile(file.lstrip().rstrip()):
                        file_handler = open(file.lstrip().rstrip())
                        for line in file_handler:
                            parsed = sqlparse.parse(line[:-1])
                            log.info(line[:-1])
                            cli.transfer(url,parsed)
                        file_handler.close()
        else:
            log.error('Can not find the File/Dir : ' + path.lstrip().rstrip() + ' ,please check...')


def test():
    statements = sqlparse.parse("  source    /home/pc/Desktop/test.sql")
    for s in statements:
        print get_batchparameters(s)


def test1():
    get_allfilepath('/home/pc/Desktop/test')


if __name__ == '__main__':

    test1()
