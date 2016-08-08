#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Usage:
     e.g.
     ./cli.py -u http://192.168.130.2/cloud/qa3/kmx/v2
'''

import sqlparse

import socket
import cmd

from colorama import Back
from metadata import query_meta, create_meta
from query import dyn_query
from identify import isDDL, isDML, isKeyword, isIdentifier, isIdentifierList
import importor


class cli(cmd.Cmd):

    hostname = socket.gethostname();
    ip = socket.gethostbyname(hostname);
    prompt = '[' + hostname + '@' + ip + '] > '

    def onecmd(self, sql):
        statements = sqlparse.parse(sql.strip(),'utf-8')
        rc = transfer(statements)
        if rc == 'stop':
            return True

def transfer(url, statements):
    for statement in statements:
        if str(statement).upper() in ('BYE', 'EXIT'):
            log.default('Exit KMX CLI ...')
            return 'stop'
        elif isDML(statement):
            dyn_query(url, statement)
        elif isDDL(statement):
            create_meta(url,statement)
        elif isKeyword(statement):
            query_meta(url,statement)
        elif isIdentifier(statement) or isIdentifierList:
            importor.run(url, statement)
        else:
            log.error('The input statement "' + str(statement) + '" is not supported ...')
        print

def run(url):
    log.primary('Query URL: ' + str(url))
    client = cli()
    client.url = url
    client.cmdloop()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True, help='Input HTTP REST URL of your KMX query engine.')
    args = parser.parse_args()

    run(args.url)
