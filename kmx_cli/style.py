#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colorama import Back, Fore


def default(message):
    print message


def info(message):
    print Fore.CYAN + message + Fore.RESET
    pass


def primary(message):
    print Fore.BLUE + message + Fore.RESET
    pass


def success(message):
    print Fore.GREEN + message + Fore.RESET


def warn(message):
    print Back.YELLOW + message + Fore.RESET


def error(message):
    print Back.RED + message + Fore.RESET


if __name__ == '__main__':
    default("default message")
    primary("primary message")
    info("info message")
    success("success message")
    warn("warn message")
    error("error message")
