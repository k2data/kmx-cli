#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from colorama import Fore




def get(url):
    '''
    :param url:
    :param key:
    :return:
    '''
    print Fore.CYAN + url
    return requests.get(url)


def post(url, payload=None, headers={"Content-Type": "application/json"}):
    '''
    :param url:
    :param payload:
    :param headers:
    :return:
    '''
    print Fore.CYAN + url
    return requests.post(url, payload=payload, headers=headers)