#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import socket

import sqlparse
from colorama import Back

import importor
import log
from batch import get_batchparameters
from identify import isDDL, isDML, isKeyword, isIdentifier, isIdentifierList
from metadata import query_meta, create_meta
from query import dyn_query


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
        if (str(sql).lstrip().strip().upper()==("SOURCE")):
            log.error('Please enter at least one script path after the keyword "SOURCE"')
            log.info('Usage: SOURCE Script1,Script2...')
            return
        if (str(sql).lstrip().strip().upper().startswith("SOURCE")):
            script_path=get_batchparameters(sql)
            if(script_path).endswith(','):
                script_path=script_path[:-1]
            paths=script_path.split(',')
            for path in paths:
                if os.path.exists(path.lstrip().rstrip()):
                    for line in open(path.lstrip().rstrip()):
                        parsed = sqlparse.parse(line[:-1])
                        log.info(line[:-1])
                        self.transfer(parsed)
                else:
                    log.error('The file ' +path.lstrip().rstrip()+' not existing,please check...')

        else:
            parsed = sqlparse.parse(sql)
            rc = self.transfer(parsed)
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
