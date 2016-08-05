#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlparse
from sqlparse.tokens import DML, DDL, Keyword

import argparse
import socket

from colorama import init, Back
from metadata import query_meta, create_meta
from query import dyn_query

init(autoreset=True)


class cli:

    def __init__(self):
        print 'KMX CLI is running ...'

    def isDML(self, statement):
        return statement.tokens[0].ttype is DML

    def isDDL(self, statement):
        return statement.tokens[0].ttype is DDL

    def isKeyword(self, statement):
        return statement.tokens[0].ttype is Keyword

    def transfer(self, statements):
        for statement in statements:
            if self.isDML(statement):
                dyn_query(self.url, statement)
            elif self.isDDL(statement):
                create_meta(self.url,statement)
            elif self.isKeyword(statement):
                query_meta(self.url,statement)

    def execute(self):
        hostname = socket.gethostname();
        ip = socket.gethostbyname(hostname);

        while True:
            sql = raw_input('[' + hostname + '@' + ip + '] > ')

            if sql.upper() == 'EXIT' or sql.upper() == 'BYE':
                print 'Exit KMX CLI ...'
                return

            parsed = sqlparse.parse(sql)
            self.transfer(parsed)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='Input HTTP REST URL of your KMX query engine.')
    args = parser.parse_args()
    url = args.url

    if url:
        print 'URL input is: ' + Back.GREEN + str(url) + Back.WHITE
        client = cli()
        client.url = url
        client.execute()

    else:
        print 'You must provide an HTTP REST URL for KMX query ...'
        print 'Use -u or --url to init URL'
        print 'Use -h to get help ...'


if __name__ == '__main__':
    run()
