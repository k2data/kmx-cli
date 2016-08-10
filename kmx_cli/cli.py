#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
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
        if str(statement).upper() == 'BYE' or str(statement).upper() == 'EXIT':
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
            query_meta(url, statement)
        elif isIdentifier(statement) or isIdentifierList(statement):
            importor.run(url, statement)
        else:
            print Back.RED + 'The input statement "' + str(statement) + '" is not supported ...' + Back.RESET
        print


class cli(cmd.Cmd):
    hostname = socket.gethostname();
    ip = socket.gethostbyname(hostname);
    prompt = '[' + hostname + '@' + ip + '] > '

    def onecmd(self, sql):
        parsed = sqlparse.parse(sql)
        rc = transfer(self.url,parsed)
        if rc == 'stop':
            return True


def run():
    parser = argparse.ArgumentParser()
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
        client = cli()
        client.url = url
        client.cmdloop()

    else:
        print 'You must provide an HTTP REST URL for KMX query ...'
        print 'Use -u or --url to init URL'
        print 'Use -h to get help ...'


if __name__ == '__main__':
    run()
