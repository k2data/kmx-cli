#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
kmx -u http://192.168.130.2/cloud/qa3/kmx/v2

# create meta data
>> create deviceType device_type_name(sensor1 String,sensor2 Float) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)
>> create device device_name(device_type_name) tags(t1,t2,标签) attributes(属性 属性值,k2 v2)

# update meta data
>> update devicetype set tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where id = "device_type_name"
>> update device set deviceTypeId=device_type_name ,tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where id = "device_name"
>> drop {device|devicetype} idd

# load dynamic data
>> import 'filepath/data.csv' into device_type_name
data.csv
---------------------------------------------------------------
device,iso,sensor1,sensor2,sensor3,sensor4,sensor5,sensor6
device_name,iso,DOUBLE,BOOLEAN,INT,LONG,FLOAT,STRING
device_name,2016-01-01T12:34:56.789+08:00,34.56789,false,3456789,1451622896789,34.56789,s34.56789
device_name,2016-01-01T12:34:57.789+08:00,34.57789,true,3457789,1451622897789,34.57789,s34.57789
---------------------------------------------------------------

# query
----------
## query meta data
Usage:
show {device|devicetype} idd
show {devices|devicetypes} like pattern
show {devices|devicetypes} where key=value
show {devices|devicetypes} [page x] [size x]

Note:
'*', '%' and '_' are supported as wildcards in pattern
wildcard: '*' match 0 ~ * characters
wildcard: '%' match 0 ~ * characters
wildcard: '_' match 0 ~ 1 character

String must be quoted if chinese or other special characters in it.

>> show devices
>> show devices page 1 size 10
>> show devices like *gw%
>> show devices where devicetype=device_type_name
>> show devicetypes where tag='标签'

## query dynamic data
>> select sensor_name from device_name where ts > 'now-1h' and ts < 'now'
>> select sensor_name from device_name where ts > 'now-1h'
>> select sensor_name from device_name where ts < 'now-1d'
>> select * from device_name
>> select sensor1,sensor2 from device_name where ts=1469672032196
>> select * from device_name where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00'

# URL control
>> url
>> url http://192.168.130.2/cloud/qa1/kmx/v2

# History
>> history

# Shell command
>> !pwd
>> !ls

'''
import argparse
import cmd
import socket

import sqlparse
from colorama import Back

import importor
import create
import update
from identify import isDDL, isDML, isKeyword, isIdentifier, isIdentifierList
from drop import drop
from query import dyn_query
import show
import log


def execute_ddl(url, statement):
    start = statement.tokens[0].value.lower()
    if start == 'create':
        create.create(url, statement)
    elif start == 'drop':
        drop(url, statement)


def execute_dml(url, statement):
    start = statement.tokens[0].value.lower()
    if start == 'update':
        update.update(url, statement)
    else:
        dyn_query(url, statement)


def transfer(url, statements):
    for statement in statements:
        # print 'execute: ' + statement.value
        if str(statement).lstrip().strip().upper().startswith('SOURCE'):
            from batch import batch_exec
            batch_exec(url, statement)
        elif isDML(statement):
            execute_dml(url, statement)
        elif isDDL(statement):
            execute_ddl(url, statement)
        elif isKeyword(statement):
            show.do_show(url, statement)
        elif isIdentifier(statement) or isIdentifierList(statement):
            importor.run(url, statement)
        else:
            error_message(None)
        print


def error_message(line):
    if line:
        log.error('** unknown syntax:%s **'%line)
    else:
        log.error('** syntax error: the statement is not supported **')


class Client(cmd.Cmd):
    hostname = socket.gethostname();
    ip = socket.gethostbyname(hostname);
    prompt = '[' + hostname + '@' + ip + '] > '

    def onecmd(self, line):
        """
        Override:
        just modify this statement:
        func = getattr(self, 'do_' + cmd)
        """
        line = line.strip()
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if not cmd:
            return error_message(None)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        else:
            try:
                func = getattr(self, 'do_' + cmd.lower())
            except AttributeError:
                return self.default(line)
            return func(arg)

    def do_help(self, arg):
        cmd.Cmd.do_help(self, arg)
        log.warn(__doc__)

    def default(self, line):
        self.kmx_cmd(line)

    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.
        Just pass, do nothing.
        """
        pass

    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)
        self._hist = []

    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modifdy the input line
            before execution (for example, variable substitution) do it here.
        """
        if line and line.upper() != 'HISTORY':
            self._hist += [line.strip()]
        return line

    def do_history(self, line):
        """Print a list of commands that have been entered"""
        for cmdline in self._hist:
            print cmdline

    def exit(self, line):
        log.primary('Exit KMX CLI...')
        log.primary('Bye!')
        return True

    def do_bye(self, line):
        ''' exit KMX CLI '''
        return self.exit(line)

    def do_exit(self, line):
        ''' exit KMX CLI '''
        return self.exit(line)

    def do_shell(self, line):
        "Run a shell command"
        # print "running shell command:", line
        import os
        output = os.popen(line).read()
        print output
        self.last_output = output

    def do_url(self, line):
        if line:
            self.url = line
            print 'New URL: ' + Back.GREEN + self.url + Back.RESET
        else:
            print 'Query URL:' + Back.GREEN + self.url + Back.RESET

    def do_author(self, line):
        authors = """
        Yang Rui, Zheng Chunxi, Chang Xue, Li Zhenxing
        @K2data
        """
        print authors

    def kmx_cmd(self, sql):
        try:
            statements = sqlparse.parse(sql, 'utf-8')
            transfer(self.url, statements)
        except Exception as e:
            error_message(e)


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--url', help='Input HTTP REST URL of your KMX query engine.')
    args = parser.parse_args()
    url = args.url

    if url:
        welcome = """
 _   _____  _____   __  _____  _____  __
| | / /|  \/  |\ \ / / |  _  ||____ |/  |
| |/ / | .  . | \ V /  | |/' |    / /`| |
|    \ | |\/| | /   \  |  /| |    \ \ | |
| |\  \| |  | |/ /^\ \ \ |_/ /.___/ /_| |_
\_| \_/\_|  |_/\/   \/  \___(_)____(_)___/
        """
        print welcome
        print 'Query URL: ' + Back.GREEN + str(url) + Back.RESET
        client = Client()
        client.url = url
        client.cmdloop()

    else:
        print 'You must provide an HTTP REST URL for KMX query ...'
        print 'Use -u or --url to init URL'
        print 'Use -h to get help ...'


if __name__ == '__main__':
    run()
