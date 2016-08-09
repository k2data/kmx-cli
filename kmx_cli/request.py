#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


def get(url):
    '''
    :param url:
    :param key:
    :return:
    '''
    return requests.get(url)


def post(url, payload=None, headers={"Content-Type": "application/json"}):
    '''
    :param url:
    :param payload:
    :param headers:
    :return:
    '''
    return requests.post(url, data=payload, headers=headers)


def delete(url):
    '''
    :param url:
    :param key:
    :return:
    '''
    return requests.delete(url)