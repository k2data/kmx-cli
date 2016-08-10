#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Usage:
     e.g.
     ./cli.py -u http://192.168.130.2/cloud/qa3/kmx/v2
'''

import cmd
import socket

import sqlparse
from colorama import Back

import importor
import create
import update
from identify import isDDL, isDML, isKeyword, isIdentifier, isIdentifierList
from metadata import query_meta, ddl_operations
from query import dyn_query
import show
import log


def execute_ddl(url, statement):
    ddl = statement.tokens[0].value.lower()
    if ddl == 'create':
        create.create(url, statement)
    elif ddl == 'drop':
        ddl_operations(url, statement)


def execute_dml(url, statement):
    dml = statement.tokens[0].value.lower()
    if dml == 'update':
        update.update(url, statement)
    else:
        dyn_query(url, statement)


def transfer(url, statements):
    for statement in statements:
        if str(statement).upper() in ['BYE', 'EXIT', 'QUIT']:
            print 'Exit KMX CLI ...'
            return 'stop'
        elif str(statement).lstrip().strip().upper().startswith('SOURCE'):
            from batch import batch_exec
            batch_exec(url,statement)
        elif isDML(statement):
            execute_dml(url, statement)
        elif isDDL(statement):
            execute_ddl(url, statement)
        elif isKeyword(statement):
            show.do_show(url, statement)
        elif isIdentifier(statement) or isIdentifierList(statement):
            importor.run(url, statement)
        else:
            error_message(str(statement))
        print


def error_message(line):
    log.error('**unknown syntax:%s'%line)


class cli(cmd.Cmd):
    hostname = socket.gethostname();
    ip = socket.gethostbyname(hostname);
    prompt = '[' + hostname + '@' + ip + '] > '

    def onecmd(self, sql):
        parsed = sqlparse.parse(sql)
        rc = transfer(self.url,parsed)
        if rc == 'stop':
            return True

def run(url):
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
    client = cli()
    client.url = url
    client.cmdloop()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--url', required=True, help='Input HTTP REST URL of your KMX query engine.')
    args = parser.parse_args()

    run(args.url)
