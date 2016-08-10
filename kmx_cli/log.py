#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colorama import Back, Fore


def default(message):
    print message


def info(message):
    print '%s%s%s'%(Fore.CYAN, message, Fore.RESET)


def primary(message):
    print '%s%s%s'%(Fore.BLUE, message, Fore.RESET)


def success(message):
    print '%s%s%s'%(Fore.GREEN, message, Fore.RESET)


def warn(message):
    print '%s%s%s'%(Fore.YELLOW, message, Fore.RESET)


def error(message):
    print '%s%s%s'%(Back.RED, message, Back.RESET)


if __name__ == '__main__':
    default("default message")
    info("info message")
    primary("primary message")
    success("success message")
    warn("warn message")
    error("error message")
