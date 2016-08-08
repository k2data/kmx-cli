#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlparse

import argparse
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

    def transfer(self, statements):
        for statement in statements:
            if str(statement).upper() == 'BYE' or str(statement).upper() == 'EXIT':
                print 'Exit KMX CLI ...'
                return 'stop'
            elif isDML(statement):
                dyn_query(self.url, statement)
            elif isDDL(statement):
                create_meta(self.url,statement)
            elif isKeyword(statement):
                query_meta(self.url,statement)
            elif isIdentifier(statement) or isIdentifierList:
                importor.run(self.url, statement)
            else:
                print Back.RED + 'The input statement "' + str(statement) + '" is not supported ...' + Back.RESET
            print

    def onecmd(self, sql):
        statements = sqlparse.parse(sql.strip())
        rc = self.transfer(statements)
        if rc == 'stop':
            return True


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='Input HTTP REST URL of your KMX query engine.')
    args = parser.parse_args()
    url = args.url

    if url:
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
