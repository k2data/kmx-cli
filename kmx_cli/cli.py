#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlparse
from sqlparse.tokens import DML, DDL, Keyword, Whitespace, Wildcard, Comparison
from sqlparse.sql import IdentifierList, Identifier, Where
from sqlparse.sql import Comparison as sqlcomp

import requests
import json
import argparse
import copy
import socket

from tabulate import tabulate
from colorama import init, Fore, Back
import arrow
import re

init(autoreset=True)

headers = {"Content-Type": "application/json"}


def formatted_output(query_result, fmt='psql'):
    ''' @param: query_result is a dict
        @param: fmt may be 'plain', 'simple', 'grid', 'fancy_grid',
                'psql', 'pipe', 'orgtbl', 'rst', 'html' etc
                detail see https://pypi.python.org/pypi/tabulate
    '''
    result = []
    headers = ['device', 'ts', 'sensorName', 'sensorValue']
    non_exist = '-'  # show when key does not exist
    err_msg = query_result['message']

    if 'dataRows' in query_result.keys():
        recs = query_result['dataRows']
        for rec in recs:
            device = rec.get('device', non_exist)
            ts = rec.get('iso', non_exist)
            if 'dataPoints' in rec.keys():
                sensor_recs = rec['dataPoints']
                for sensor in sensor_recs:
                    result.append((device, ts, sensor.get('sensor', non_exist), sensor.get('value', non_exist)))
        if result:
            print tabulate(result, headers, tablefmt=fmt)
        print err_msg
    elif 'dataPoints' in query_result.keys():
        for rec in query_result['dataPoints']:
            result.append((rec['device'], rec.get('timestamp', non_exist), rec.get('sensor', non_exist),rec.get('value', non_exist)))
        if result:
            print tabulate(result, headers, tablefmt=fmt)
        print err_msg
    else :
        print json.dumps(query_result, sort_keys=True, indent=4) + '\n'

class cli:
    def __init__(self):
        print 'KMX CLI is running ...'
        # self.url = 'http://192.168.130.2/cloud/qa3/kmx/v2'

    def get(self, uri):
        response = requests.get(uri)
        print Fore.RED + uri
        payload = json.loads(response.text)
        formatted_output(payload)
        # print json.dumps(payload, sort_keys=True, indent=4) + '\n'

    def post(self, uri, payload):
        response = requests.post(uri, headers=headers, data=payload)
        responsePayload = json.loads(response.text)

        print Fore.RED + uri
        print Fore.CYAN + payload
        print Fore.MAGENTA + json.dumps(responsePayload, sort_keys=True, indent=4) + '\n'

    def isDML(self, sql):
        tokens = sql.tokens
        firstToken = tokens[0]
        if firstToken.ttype is not DML:
            # print Back.RED + '   The SQL is not a select statement ...'
            return False
        else:
            return True

    def isDDL(self, sql):
        tokens = sql.tokens
        firstToken = tokens[0]
        if firstToken.ttype is not DDL:
            # print Back.RED + '   The SQL is not a create statement ...'
            return False
        else:
            return True

    def getColumnAndTables(self, sql):
        ids = []
        # print sql.tokens
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

    def getColumns(self, sql):
        if not self.isDML(sql):
            return None
        ids = self.getColumnAndTables(sql)
        columns = []
        for id in ids:
            if id.upper() == 'FROM':
                break
            columns.append(id)
        return columns

    def getTables(self, sql):
        if not self.isDML(sql):
            return None
        ids = self.getColumnAndTables(sql)
        columns = self.getColumns(sql)
        tables = copy.deepcopy(ids)
        for id in ids:
            if id.upper() <> 'FROM':
                tables.remove(id)
            else:
                tables.remove(id)
                break
        return tables

    def relativeTimeParser(self, relativeStr, format):
        if format.upper() <> 'ISO' and format.upper() <> 'TIMESTAMP':
            print 'The time format is either not ISO or TIMESTAMP'
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
                print param
                if format.upper() == 'ISO':
                    return arrow.now().replace(**param).format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+","%2B")
                elif format.upper() == 'TIMESTAMP':
                    return int(round(arrow.now().replace(**param).float_timestamp * 1000))
            else:
                print 'The relative time format is wrong ...'
                return relativeStr

    def getWhere(self, sql):
        # if self.isDML(sql) == False:
        if not self.isDML(sql):
            return None
        tokens = sql.tokens
        for token in tokens:
            if isinstance(token, Where):
                # print token.value
                pointQueryValue = {}
                pointQuery = {"sampleTime": pointQueryValue}

                rangeQueryStart = {}
                rangeQueryEnd = {}
                rangeQuery = {"timeRange": {"start": rangeQueryStart, "end": rangeQueryEnd}}

                whereToekns = token.tokens
                # print whereToekns
                # If there is comparison token in where token
                hasComparisonToken = False
                for token in whereToekns:
                    if isinstance(token, sqlcomp):
                        hasComparisonToken = True
                        # print token.value
                        comparisonTokens = token.tokens
                        # id = None
                        # comp = None
                        # value = None
                        for ctoken in comparisonTokens:
                            # print ctoken.ttype
                            if isinstance(ctoken, Identifier):
                                # print ctoken.value
                                id = ctoken.value
                            elif ctoken.ttype is Comparison:
                                # print ctoken.value
                                comp = ctoken.value
                            elif ctoken.ttype is not Whitespace:
                                # print ctoken.value
                                value = ctoken.value
                        # tell if comparion is "=", if yes, the query is a point query
                        value = str(value).replace("'", "").replace("+","%2B")
                        # If time is relative time
                        if value.upper().startswith('NOW'):
                            value = self.relativeTimeParser(value, id)
                        # print value
                        if comp == '=':
                            pointQueryValue.update({id: value})
                        elif comp == '>':
                            rangeQueryStart.update({id: value})
                        elif comp == '<':
                            rangeQueryEnd.update({id: value})

                if not hasComparisonToken:
                    id = None
                    comp = None
                    value = None
                    for token in whereToekns:
                        if token.ttype is Keyword and (
                                    token.value.upper() == 'WHERE' or token.value.upper() == 'AND' or token.value.upper() == 'OR'):
                            continue
                        # if token.ttype is Keyword and token.value.upper() == 'AND':
                        #     continue
                        if token.ttype is Whitespace:
                            continue

                        if token.ttype is Keyword:
                            id = token.value
                        elif token.ttype is Comparison:
                            comp = token.value
                        elif token.ttype is not Whitespace:
                            value = token.value

                        if id and value:
                            value = str(value).replace("'", "").replace("+","%2B")
                            # If time is relative time
                            if value.upper().startswith('NOW'):
                                value = self.relativeTimeParser(value, id)
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

    def doQuery(self, dml):
        devices = self.getTables(dml)
        if not devices:
            print 'Device should be provided ...'
            return
        if len(devices) > 1:
            print 'Multi-devices query is not supported now ...'
            return
        sensors = self.getColumns(dml)
        predicate = self.getWhere(dml)
        if not predicate:
            print 'The select statement does NOT contain WHERE predicates, currently is not supported ...'
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
            print 'The query is not supported now ...'

        sources = {"device": devices[0], "sensors": sensors}
        sources[key] = value
        select = {"sources": sources}

        uri = self.url + '/data/' + query_url + '?select=' + json.dumps(select)
        self.get(uri)

    def transfer(self, sqls):
        for sql in sqls:
            if self.isDML(sql):
                self.doQuery(sql)
            if self.isDDL(sql):
                self.create(sql)

    def queryMeta(self, columns):
        if len(columns) < 2:
            print 'Please add table in your sql. Table show be in [devices ,device-type] ....'
        else:
            if columns[1] != 'devices'.lower() and columns[1].lower() != 'device-types':
                print ' Usage : show table [id] .   '
                print 'Table show be in [ devices , device-type ] ....'
                return
            id = ''
            if len(columns) == 3:
                id = columns[2]

            uri = self.url + '/' + columns[1] + '/' + id
            self.get(uri)

    def parseAttr(self,payload,tokens):
        length = len(tokens) + 1;
        if length > 4:
            for index in range(4, length, 2):
                key = tokens[index][0].value.encode("utf-8").strip()
                if key == 'tags':
                    payload['tags'] = tokens[index][1].value.encode("utf-8").strip()[1:-1].split(',')
                elif key == 'attributes':
                    attributes = []
                    attrs = tokens[index][1].value[1:-1].split(',')
                    for att in attrs:
                        attribute = {}
                        items = att.encode("utf-8").strip().split(' ')
                        attribute['name'] = items[0].strip()
                        if len(items) >= 2:
                            attribute['attributeValue'] = items[1].strip()
                        else:
                            print Back.YELLOW + 'attribute:' + items[0] + ' have no value...'
                        attributes.append(attribute)
                    payload['attributes'] = attributes
        return payload

    def create(self, sql):
        tokens = sql.tokens
        path = tokens[2].value.encode("utf-8").lower().strip()

        uri = self.url + '/' + path
        payload = {}
        if path == 'device-types':
            sensors = []
            columns = tokens[4][1].value[1:-1].split(',')
            for column in columns:
                sensor = {}
                items = column.encode("utf-8").strip().split(' ')
                if len(items) < 2 :
                    print Back.RED + 'sensor : ' + items[0] + ' should have valueType...'
                    return
                sensor['id'] = items[0].strip()
                sensor['valueType'] = items[1].strip().upper()
                sensors.append(sensor)

                payload['id'] = tokens[4][0].value.encode("utf-8").strip()
                payload['sensors'] = sensors

        elif path == 'devices':
            payload['id'] = tokens[4][0].value.encode("utf-8").strip()
            payload['deviceTypeId'] = tokens[4][1].value[1:-1].strip()

        else:
            print ' Table ERROR .. Table show be in [ device-types ,devices ]'
            return
        payload = self.parseAttr(payload,tokens)
        self.post(uri, json.dumps(payload))

    def excute(self):
        hostname = socket.gethostname();
        ip = socket.gethostbyname(hostname);

        while True:
            sql = raw_input('[' + hostname + '@' + ip + '] > ')

            if sql.upper() == 'EXIT' or sql.upper() == 'BYE':
                print 'Exit KMX CLI ...'
                return

            columns = sql.split(' ')
            if columns[0].upper() == 'SHOW':
                self.queryMeta(columns)
            else:
                parsed = sqlparse.parse(sql)
                self.transfer(parsed)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='Input HTTP REST URL of your KMX query engine.')
    args = parser.parse_args()
    url = args.url

    if url:
        print 'URL input is: ' + Back.GREEN + str(url)
        client = cli()
        client.url = url
        client.excute()

    else:
        print 'You must provide an HTTP REST URL for KMX query ...'
        print 'Use -u or --url to init URL'
        print 'Use -h to get help ...'

def test():
    client = cli()
    client.url = 'http://192.168.130.2/cloud/qa3/kmx/v2'
    parsed = sqlparse.parse("create device-types dt_test(s1 string,s2 ) tags(a,b,c,d) attributes(ab,c d)")
    # parsed = sqlparse.parse("create devices d(dt) tags(a,b,c,d) attributes(a b,c d)")
    # parsed = sqlparse.parse("select WCNVConver_chopper_igbt_temp,WCNVPwrReactInstMagf from GW150001 where iso > '2015-04-24T20:10:00.000%2B08:00' and iso < '2015-05-01T07:59:59.000%2B08:00'")
    client.transfer(parsed)


if __name__ == '__main__':
    run()
    # test()
