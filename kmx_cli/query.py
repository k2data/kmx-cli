#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlparse.keywords import KEYWORDS
from sqlparse import tokens
from sqlparse.tokens import Keyword, Whitespace, Wildcard, Comparison, Literal
from sqlparse.sql import IdentifierList, Identifier, Where, TokenList, Function
from sqlparse.sql import Comparison as sqlcomp

import arrow
import re
import copy
import json
import timeit
import identify

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


def get_sensors(sql):
    # ids = get_column_tables(sql)
    # columns = []
    # for id in ids:
    #     if id.upper() == 'FROM':
    #         break
    #     columns.append(id)
    # return columns
    function = None
    sensors = []
    condition = identify.trip_tokens(sql.tokens)[1]
    is_function = isinstance(condition, Function)
    if is_function:
        tokens = identify.trip_tokens(condition.tokens)
        function = tokens[0].value.lower()
        values = identify.trip_tokens(tokens[1].tokens)[1].value.split(',')
    else:
        values = condition.value.split(',')
    for value in values:
        sensors.append(value.strip())
    return is_function, sensors, function


def get_tables(sql):
    ids = get_column_tables(sql)
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
    pointQueryValue = {}
    pointQuery = {"sampleTime": pointQueryValue}
    rangeQueryStart = {}
    rangeQueryEnd = {}
    rangeQuery = {"timeRange": {"start": rangeQueryStart, "end": rangeQueryEnd}}

    tokens = sql.tokens
    for token in tokens:
        if isinstance(token, Where):
            whereToekns = token.tokens

            for token in whereToekns:
                if isinstance(token, sqlcomp):
                    comparisonTokens = token.tokens
                    for ctoken in comparisonTokens:
                        if isinstance(ctoken, Identifier):
                            time_key = ctoken.value
                        elif ctoken.ttype is Comparison:
                            comp = ctoken.value
                        elif ctoken.ttype is not Whitespace:
                            value = ctoken.value

                    if value.startswith("'") and value.endswith("'"):
                        time_key = 'iso'
                        value = identify.strip_quotes(value)
                        if value.upper().startswith('NOW'):
                            value = relative_time_parser(value, 'iso')
                        else:
                            value = str(arrow.get()).replace("+", "%2B")
                        if len(value) >= 32:
                            value = value[0:23] + value[26:]
                    else:
                        time_key = 'timestamp'

                    if comp == '=':
                        pointQueryValue.update({time_key: value})
                    elif comp == '>':
                        rangeQueryStart.update({time_key: value})
                    elif comp == '<':
                        rangeQueryEnd.update({time_key: value})

    if pointQueryValue:
        return pointQuery
    elif rangeQueryStart:
        if not rangeQueryEnd:
            rangeQueryEnd.update({'iso': arrow.now().format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+", "%2B")})
        return rangeQuery
    elif rangeQueryEnd:
        rangeQueryStart.update({'iso': arrow.get('1970-01-01T00:00:00.001Z').format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+", "%2B")})
        return rangeQuery
    else:
        rangeQueryStart.update({'iso': arrow.get('1970-01-01T00:00:00.001Z').format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+", "%2B")})
        rangeQueryEnd.update({'iso': arrow.now().format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+", "%2B")})
        return rangeQuery


def get_into(sql):
    return identify.find_next_token_by_ttype(sql, lambda token: token.value.upper() == 'INTO', Literal.String.Single)


def dyn_query(url, dml):
    devices = get_tables(dml)
    if not devices:
        log.error('Device should be provided ...')
        return
    if len(devices) > 1:
        print devices
        log.error('Multi-devices query is not supported now ...')
        return
    is_function, sensors, function = get_sensors(dml)
    # Support wildcard * in select
    if len(sensors) == 1 and sensors[0] == '*':
        sensors = get_sensors_by_device(url, devices[0])

    predicate = get_where(dml)
    # if not predicate:
    #     log.error('The select statement does NOT contain WHERE predicates, currently is not supported ...')
    #     return None
    query_url = 'data-points'
    is_statistic = False
    if predicate.has_key('sampleTime'):
        key = 'sampleTime'
        value = predicate['sampleTime']
    elif predicate.has_key('timeRange'):
        key = 'timeRange'
        value = predicate['timeRange']
        query_url = 'data-rows'
        is_statistic = True
    else:
        log.error('The query is not supported now ...')

    sources = {"device": devices[0], "sensors": sensors}
    sources[key] = value
    select = {"sources": sources}

    pages, size = get_page_size(dml)

    uri = url + '/data/' + query_url + '?select=' + json.dumps(select)
    if size:
        uri += '&size=' + str(size)

    do_query(dml, uri, pages, is_statistic)


def merge(old, new):
    if not old:
        return new
    if not new:
        return old
    size = new['pageInfo']['size']
    if size > 0:
        rows = new['dataRows']
        for row in rows:
            old['dataRows'].append(row)
        # old['dataRows'].extend[rows]
        old['pageInfo']['size'] = old['pageInfo']['size'] + size
        return old


def query_one_page(url):
    log.primary(url)
    response = get(url)
    rc = response.status_code
    response.close()

    if rc != 200:
        log.error('Code: ' + str(rc))
        log.error(response.text)
        return
    else:
        return json.loads(response.text)


def do_query(dml, url, pages, is_statistic):
    start_time = timeit.default_timer()
    payload = {}
    if pages:
        pages = pages.split(',')
        if len(pages) == 1:
            uri = url + '&page=' + str(pages[0])
            payload = query_one_page(uri)
        elif len(pages) == 2:
            start, end = int(pages[0].strip()), int(pages[1].strip())
            if start > end:
                log.error("start page must less than end page")
                return
            while start <= end:
                uri = url + '&page=' + str(start)
                payload = merge(payload, query_one_page(uri))
                start += 1
        else:
            log.error("to many page params...")
            return
    else:
        payload = query_one_page(url)
    elapsed = timeit.default_timer() - start_time

    into, path = get_into(dml)
    if into:
        if path:
            pretty_data_query(payload, fmt='csv', path=identify.strip_quotes(path))
        else:
            log.error("Syntax error after : " + into + '. Should follow a file path.')
    else:
        pretty_data_query(payload, fmt='psql', path=path)

    log.default('Returned in %.2f s' % elapsed)

    is_function, sensors, function = get_sensors(dml)
    if is_function:
        if is_statistic:
            import statistic
            print
            statistic.execute(payload, sensors, function)
        else:
            log.error("data point query does not suppurt statistic")


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
    return page, size


def get_sensors_by_device(url, device_id):
    uri = url + '/devices/' + device_id
    payload = get(uri).text
    response = json.loads(payload)
    sensors_list = response['device']['sensors']
    sensor_ids = []
    for sensor in sensors_list:
        sensor_ids.append(sensor['id'])
    return sensor_ids


if __name__ == '__main__':
    import sqlparse
    statements = sqlparse.parsestream('select descs(s1 ,s2) from device where ts > 1;select s1 ,s2 from device where ts > 1', 'utf-8')
    for statement in statements:
        print get_sensors(statement)