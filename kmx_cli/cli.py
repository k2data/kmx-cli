#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Usage:
     e.g.
     kmx_cli -u http://192.168.130.2/cloud/qa3/kmx/v2
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
from metadata import ddl_operations
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
        if str(statement).lstrip().strip().upper().startswith('SOURCE'):
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

    def onecmd(self, line):
        """
        Override:
        just modify this statement:
        func = getattr(self, 'do_' + cmd)
        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd.lower())
            except AttributeError:
                return self.default(line)
            return func(arg)

    def default(self, line):
        self.kmxcmd(self.url, line)

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
        return self.exit(line)

    def do_exit(self, line):
        return self.exit(line)

    def do_shell(self, line):
        "Run a shell command"
        # print "running shell command:", line
        import os
        output = os.popen(line).read()
        print output
        self.last_output = output

    def do_url(self, line):
        self.url = line
        print 'New URL: ' + Back.GREEN + self.url + Back.RESET

    def kmxcmd(self, url, sql):
        parsed = sqlparse.parse(sql)
        transfer(self.url, parsed)

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
