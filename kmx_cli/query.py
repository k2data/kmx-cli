#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlparse.keywords import KEYWORDS
from sqlparse import tokens
from sqlparse.tokens import Keyword, Whitespace, Wildcard, Comparison, Literal, Number
from sqlparse.sql import IdentifierList, Identifier, Where, TokenList
from sqlparse.sql import Comparison as sqlcomp

import arrow
import re
import copy
import json
import timeit

from request import get
from pretty import pretty_data_query
import log

close_list = list(Where.M_CLOSE[1])
close_list.append('PAGE')
close_list.append('SIZE')
Where.M_CLOSE = (Where.M_CLOSE[0], tuple(close_list))
KEYWORDS['PAGE'] = tokens.Keyword


def get_column_tables(sql):
        ids = []
        for token in sql.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    ids.append(identifier.get_name())
            elif isinstance(token, Identifier):
                ids.append(token.value)
            elif token.ttype is Keyword and token.value.upper() == 'FROM':
                ids.append(token.value)
            elif token.ttype is Wildcard:
                ids.append(token.value)
        return ids


def get_columns(sql):
    ids = get_column_tables(sql)
    columns = []
    for id in ids:
        if id.upper() == 'FROM':
            break
        columns.append(id)
    return columns


def get_tables(sql):
    ids = get_column_tables(sql)
    columns = get_columns(sql)
    tables = copy.deepcopy(ids)
    for id in ids:
        if id.upper() <> 'FROM':
            tables.remove(id)
        else:
            tables.remove(id)
            break
    return tables


def relative_time_parser(relativeStr, format):
    if format.upper() <> 'ISO' and format.upper() <> 'TIMESTAMP':
        log.error('The time format is either not ISO or TIMESTAMP')
        return relativeStr
    if relativeStr.upper() == 'NOW':
        if format.upper() == 'ISO':
            return arrow.now().format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+","%2B")
        elif format.upper() == 'TIMESTAMP':
            return int(round(arrow.now().float_timestamp * 1000))
    else:
        regex = '^(now)(-)([0-9]+)([s,m,h,d,w]{1})$'
        pattern = re.compile(regex)
        if pattern.match(str(relativeStr)):
            segments = pattern.findall(str(relativeStr))
            if segments[0][3] == 's':
                unit = 'seconds'
            elif segments[0][3] == 'm':
                unit = 'minutes'
            elif segments[0][3] == 'h':
                unit = 'hours'
            elif segments[0][3] == 'd':
                unit = 'days'
            elif segments[0][3] == 'w':
                unit = 'weeks'
            replaceStr = unit + "=%s%s" % (segments[0][1],segments[0][2])
            param = {unit:int("%s%s" % (segments[0][1],segments[0][2]))}
            if format.upper() == 'ISO':
                return arrow.now().replace(**param).format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+","%2B")
            elif format.upper() == 'TIMESTAMP':
                return int(round(arrow.now().replace(**param).float_timestamp * 1000))
        else:
            log.error('The relative time format is wrong ...')
            return relativeStr


def get_where(sql):
    tokens = sql.tokens
    for token in tokens:
        if isinstance(token, Where):
            pointQueryValue = {}
            pointQuery = {"sampleTime": pointQueryValue}

            rangeQueryStart = {}
            rangeQueryEnd = {}
            rangeQuery = {"timeRange": {"start": rangeQueryStart, "end": rangeQueryEnd}}

            whereToekns = token.tokens

            for token in whereToekns:
                if isinstance(token, sqlcomp):
                    comparisonTokens = token.tokens
                    for ctoken in comparisonTokens:
                        if isinstance(ctoken, Identifier):
                            id = ctoken.value
                        elif ctoken.ttype is Comparison:
                            comp = ctoken.value
                        elif ctoken.ttype is not Whitespace:
                            value = ctoken.value

                    # tell ts format is timestamp or iso
                    if value.startswith("'") and value.endswith("'"):
                        id = 'iso'
                    else:
                        id = 'timestamp'

                    value = str(value).replace("'", "").replace("+","%2B")

                    # If time is relative time
                    if value.upper().startswith('NOW'):
                        value = relative_time_parser(value, 'iso')

                    if comp == '=':
                        pointQueryValue.update({id: value})
                    elif comp == '>':
                        rangeQueryStart.update({id: value})
                    elif comp == '<':
                        rangeQueryEnd.update({id: value})


            if pointQueryValue:
                return pointQuery
            if rangeQueryStart:
                return rangeQuery


def dyn_query(url, dml):
    devices = get_tables(dml)
    if not devices:
        log.error('Device should be provided ...')
        return
    if len(devices) > 1:
        log.error('Multi-devices query is not supported now ...')
        return
    sensors = get_columns(dml)
    # Support wildcard * in select
    if len(sensors) == 1 and sensors[0] == '*':
        sensors = get_sensors_by_device(url, devices[0])

    predicate = get_where(dml)
    if not predicate:
        log.error('The select statement does NOT contain WHERE predicates, currently is not supported ...')
        return None
    query_url = 'data-points'
    if predicate.has_key('sampleTime'):
        key = 'sampleTime'
        value = predicate['sampleTime']
    elif predicate.has_key('timeRange'):
        key = 'timeRange'
        value = predicate['timeRange']
        query_url = 'data-rows'
    else:
        log.error('The query is not supported now ...')

    sources = {"device": devices[0], "sensors": sensors}
    sources[key] = value
    select = {"sources": sources}

    # page and size
    page,size = get_page_size(dml)
    page_size = ''
    if page:
        page_size += '&page=' + str(page)
    if size:
        page_size += '&size=' + str(size)

    if page_size:
        uri = url + '/data/' + query_url + '?select=' + json.dumps(select) + page_size
    else:
        uri = url + '/data/' + query_url + '?select=' + json.dumps(select)
    log.primary(uri)
    print
    start_time = timeit.default_timer()
    response = get(uri)
    elapsed = timeit.default_timer() - start_time
    rc = response.status_code
    if rc != 200:
        log.error('Code: ' + str(rc))
        log.error(response.text)
    else:
        pretty_data_query(json.loads(response.text))
        log.default('Returned in %.2f s' % elapsed)
    response.close()


def get_page_size(sql):
    page = None
    size = None
    tokens = TokenList(sql.tokens)
    if isinstance(tokens, TokenList):
        page_token = tokens.token_matching([lambda t: t.value.upper() == 'PAGE'],0)
        if page_token:
            page_idx = tokens.token_index(page_token, 0)
            while tokens[page_idx].ttype is not Literal.Number.Integer:
                page_idx += 1
            page = tokens[page_idx].value

        size_token = tokens.token_matching([lambda t: t.value.upper() == 'SIZE'],0)
        if size_token:
            size_idx = tokens.token_index(size_token, 0)
            while tokens[size_idx].ttype is not Literal.Number.Integer:
                size_idx += 1
            size = tokens[size_idx].value
    return page,size


def get_sensors_by_device(url, deviceid):
    uri = url + '/devices/' + deviceid
    payload = get(uri).text
    response = json.loads(payload)
    sensors_list = response['device']['sensors']
    sensor_ids = []
    for sensor in sensors_list:
        sensor_ids.append(sensor['id'])
    return sensor_ids