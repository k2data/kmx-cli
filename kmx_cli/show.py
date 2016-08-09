#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Chang, Xue
Usage:
show {device|device-type} idd
show {devices|device-types} like regex
show {devices} where device-type=idd
'''

from colorama import Back
import json
import re

from request import get, post
from pretty import pretty_meta, pretty_meta_list, pretty_output_meta_all
import log
import identify

# add new keywords into sqlparse module
from sqlparse import sql as _sql
from sqlparse.tokens import Keyword
from sqlparse.keywords import KEYWORDS

NEW_KEYWORDS = ['DEVICE', 'DEVICES', 'DEVICETYPE', 'DEVICETYPES']
for key in NEW_KEYWORDS:
    KEYWORDS[key] = Keyword

charset = 'utf-8'

def do_show(base_url, statement):
    ''' Usage:show {device|device-type} idd
              show {devices|device-types} like regex
              show {devices} where device-type=idd
    '''
    sql_tokens = statement.tokens
    log.success(sql_tokens)
    key = sql_tokens[2].value.upper()

    key_next = sql_tokens[4]

    log.success(key)
    if key == 'DEVICE':
        qurey_single(base_url, 'devices', key_next.value, 'devices', pretty_meta_list)
    elif key == 'DEVICETYPE':
        qurey_single(base_url, 'device-types', key_next.value, 'deviceType', pretty_meta)
    elif key in ['DEVICES', 'DEVICETYPES']:
        sub_url = get_suburl(key)
        main_key = get_main_key(key) # the json key of response
        log.primary('main_key:%s'%main_key)
        log.primary('sub_url:%s'%sub_url)
        log.success(key_next.value)
        if 'LIKE' == key_next.value.upper():
            query_regex_common(base_url, sub_url, main_key, sql_tokens[6].value)
        elif identify.isWhere(key_next):
            where_tokens = key_next.tokens
            log.success(where_tokens)
            query_by_attrs('%s/%s'%(base_url, sub_url), where_tokens, main_key)

def qurey_single(url, sub_url, idd, main_key, process_func):
    ''' to support: show device xxx
                    show devicetype xxx
    '''
    # query from k2db
    response = get('/'.join((url, sub_url, idd)))
    resopnse_payload = json.loads(response.text)
    # output as text table
    process_func(resopnse_payload, main_key)

def query_regex_common(url, sub_url, main_key, raw_str, fmt='psql'):
    '''to support: show {devices|devicetypes} like xxx
        1. query all devices or device-types
        2. filter results with condition related to device or devicetype
        3. output the result as text table
    @param: url: base url
    @param: sub_url: devices or device-types
    @param: match_key: deviceType
    @param: raw_str: str or regexpress
    '''
    regex_match = regex_trans(raw_str)
    result = []
    # query first page
    response = get('%s/%s?order=asc-id&page=1'%(url, sub_url))
    resopnse_payload = json.loads(response.text)
    filter_result(resopnse_payload, main_key, re.compile(regex_match).match, result)
    pages = resopnse_payload['pageInfo']['pages']
    # query other pages
    for pageNum in xrange(2, pages):
        response = get('%s/%s?order=asc-id&page=%s'%(url, sub_url, pageNum))
        response_payload = json.loads(response.text)
        filter_result(response_payload, main_key, re.compile(regex_match).match, result)
    # output
    total = len(result)
    response_payload = {'pageInfo':{'total':total, 'size':total, 'pageSzie':total, 'pageNum':1, 'pages':1}, main_key:result}
    pretty_output_meta_all(response_payload, main_key, fmt)

def query_by_attrs(base_url, where_tokens, main_key, fmt='psql'):
    ''' to support: show {devices|devicetypes} where key=value and key=value ...'''
    # form url
    url_attrs = []
    for comp_exp in where_tokens[2:]:
        if isinstance(comp_exp, _sql.Comparison):
            key, value = comp_exp.split('=')
            key = filter_quote(key)
            value = filter_quote(value)
            url_attrs.append('%s=%s'%(key, value))
    if url_attrs:
        url = '%s?%s'%(base_url, '&'.join(url_attrs))
        log.success(url)
    else:
        raise Exception('where statement is wrong')
    # query first page
    response = get('%s&order=asc-id&page=1'%(url))
    response_payload = json.loads(response.text)
    pretty_output_meta_all(response_payload, main_key, fmt)
    # query others
    pages = response_payload['pageInfo']['pages']
    for pageNum in xrange(2, pages):
        response = get('%s&order=asc-id&page=%s'%(url, pageNum))
        resopnse_payload = json.loads(response.text)
        pretty_output_meta_all(resopnse_payload, main_key, fmt)

########################### support function #####################################
def get_main_key(value):
    ''' use to parse response of REST API '''
    key = value.upper().strip()
    if key in NEW_KEYWORDS:
        if 'DEVICETYPE' in key:
            return 'deviceType'
        else:
            return 'devices'
    return value.lower()

def get_suburl(value):
    ''' use to request REST API '''
    key = value.upper().strip()
    if key in NEW_KEYWORDS:
        if 'DEVICETYPE' in key:
            return 'device-types'
        else:
            return 'devices'
    return value.lower()

def regex_trans(regex_str):
    ''' change the regexpress string of mysql to python format '''
    regex_new = regex_str.replace('"', '')
    regex_new = regex_new.replace("'", '')
    regex_new = regex_new.replace('%', '.*')
    regex_new = regex_new.replace('*', '.*')
    regex_new = regex_new.replace('_', '.?')
    return regex_new.strip()

def filter_quote(str_value):
    str_value = str_value.replace('"', '')
    str_value = str_value.replace("'", '')
    return str_value.strip()

def filter_result(result_dict, main_key, is_match, result=[]):
    body = result_dict[main_key]
    if not body:
        return
    for rec in body:
        if is_match(rec['id']):
            result.append(rec)
