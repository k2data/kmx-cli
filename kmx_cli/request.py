#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from colorama import Fore
from pretty import pretty, pretty_meta_list

headers = {"Content-Type": "application/json"}


def get(url):
    '''
    :param url:
    :param key:
    :return:
    '''
    print Fore.CYAN + url
    return requests.get(url)


def post(url, payload):
    '''
    :param url:
    :param payload:
    :return:
    '''
    print Fore.CYAN + url
    return requests.post(url, headers=headers, data=payload)