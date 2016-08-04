#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlparse
from sqlparse.tokens import DML, DDL, Keyword

import argparse
import socket

from colorama import init, Fore, Back
from metadata import query_meta, create_meta
from query import dyn_query

init(autoreset=True)


# def formatted_output(query_result, fmt='psql'):
#     ''' @param: query_result is a dict
#         @param: fmt may be 'plain', 'simple', 'grid', 'fancy_grid',
#                 'psql', 'pipe', 'orgtbl', 'rst', 'html' etc
#                 detail see https://pypi.python.org/pypi/tabulate
#     '''
#     result = []
#     headers = ['device', 'ts', 'sensorName', 'sensorValue']
#     non_exist = '-'  # show when key does not exist
#     err_msg = query_result['message']
#
#     if 'dataRows' in query_result.keys():
#         recs = query_result['dataRows']
#         for rec in recs:
#             device = rec.get('device', non_exist)
#             ts = rec.get('iso', non_exist)
#             if 'dataPoints' in rec.keys():
#                 sensor_recs = rec['dataPoints']
#                 for sensor in sensor_recs:
#                     result.append((device, ts, sensor.get('sensor', non_exist), sensor.get('value', non_exist)))
#         if result:
#             print tabulate(result, headers, tablefmt=fmt)
#         print err_msg
#     elif 'dataPoints' in query_result.keys():
#         for rec in query_result['dataPoints']:
#             result.append((rec['device'], rec.get('timestamp', non_exist), rec.get('sensor', non_exist),rec.get('value', non_exist)))
#         if result:
#             print tabulate(result, headers, tablefmt=fmt)
#         print err_msg
#     else :
#         print json.dumps(query_result, sort_keys=True, indent=4) + '\n'

class cli:
    def __init__(self):
        print 'KMX CLI is running ...'
        # self.url = 'http://192.168.130.2/cloud/qa3/kmx/v2'

    # def get(self, uri):
    #     response = requests.get(uri)
    #     print Fore.RED + uri
    #     payload = json.loads(response.text)
    #     formatted_output(payload)
    #     # print json.dumps(payload, sort_keys=True, indent=4) + '\n'
    #
    # def post(self, uri, payload):
    #     response = requests.post(uri, headers=headers, data=payload)
    #     responsePayload = json.loads(response.text)
    #
    #     print Fore.RED + uri
    #     print Fore.CYAN + payload
    #     print Fore.MAGENTA + json.dumps(responsePayload, sort_keys=True, indent=4) + '\n'

    def isDML(self, statement):
        return statement.tokens[0].ttype is DML


    def isDDL(self, statement):
        return statement.tokens[0].ttype is DDL


    def isKeyword(self, statement):
        return statement.tokens[0].ttype is Keyword


    # def getColumnAndTables(self, sql):
    #     ids = []
    #     # print sql.tokens
    #     for token in sql.tokens:
    #         if isinstance(token, IdentifierList):
    #             for identifier in token.get_identifiers():
    #                 ids.append(identifier.get_name())
    #         elif isinstance(token, Identifier):
    #             ids.append(token.value)
    #         elif token.ttype is Keyword and token.value.upper() == 'FROM':
    #             ids.append(token.value)
    #         elif token.ttype is Wildcard:
    #             ids.append(token.value)
    #     return ids
    #
    # def getColumns(self, sql):
    #     if not self.isDML(sql):
    #         return None
    #     ids = self.getColumnAndTables(sql)
    #     columns = []
    #     for id in ids:
    #         if id.upper() == 'FROM':
    #             break
    #         columns.append(id)
    #     return columns
    #
    # def getTables(self, sql):
    #     if not self.isDML(sql):
    #         return None
    #     ids = self.getColumnAndTables(sql)
    #     columns = self.getColumns(sql)
    #     tables = copy.deepcopy(ids)
    #     for id in ids:
    #         if id.upper() <> 'FROM':
    #             tables.remove(id)
    #         else:
    #             tables.remove(id)
    #             break
    #     return tables
    #
    # def relativeTimeParser(self, relativeStr, format):
    #     if format.upper() <> 'ISO' and format.upper() <> 'TIMESTAMP':
    #         print 'The time format is either not ISO or TIMESTAMP'
    #         return relativeStr
    #     if relativeStr.upper() == 'NOW':
    #         if format.upper() == 'ISO':
    #             return arrow.now().format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+","%2B")
    #         elif format.upper() == 'TIMESTAMP':
    #             return int(round(arrow.now().float_timestamp * 1000))
    #     else:
    #         regex = '^(now)(-)([0-9]+)([s,m,h,d,w]{1})$'
    #         pattern = re.compile(regex)
    #         if pattern.match(str(relativeStr)):
    #             segments = pattern.findall(str(relativeStr))
    #             if segments[0][3] == 's':
    #                 unit = 'seconds'
    #             elif segments[0][3] == 'm':
    #                 unit = 'minutes'
    #             elif segments[0][3] == 'h':
    #                 unit = 'hours'
    #             elif segments[0][3] == 'd':
    #                 unit = 'days'
    #             elif segments[0][3] == 'w':
    #                 unit = 'weeks'
    #             replaceStr = unit + "=%s%s" % (segments[0][1],segments[0][2])
    #             param = {unit:int("%s%s" % (segments[0][1],segments[0][2]))}
    #             print param
    #             if format.upper() == 'ISO':
    #                 return arrow.now().replace(**param).format('YYYY-MM-DDTHH:mm:ss.SSSZZ').replace("+","%2B")
    #             elif format.upper() == 'TIMESTAMP':
    #                 return int(round(arrow.now().replace(**param).float_timestamp * 1000))
    #         else:
    #             print 'The relative time format is wrong ...'
    #             return relativeStr
    #
    # def getWhere(self, sql):
    #     if not self.isDML(sql):
    #         return None
    #     tokens = sql.tokens
    #     for token in tokens:
    #         if isinstance(token, Where):
    #             # print token.value
    #             pointQueryValue = {}
    #             pointQuery = {"sampleTime": pointQueryValue}
    #
    #             rangeQueryStart = {}
    #             rangeQueryEnd = {}
    #             rangeQuery = {"timeRange": {"start": rangeQueryStart, "end": rangeQueryEnd}}
    #
    #             whereToekns = token.tokens
    #
    #             for token in whereToekns:
    #                 if isinstance(token, sqlcomp):
    #                     comparisonTokens = token.tokens
    #                     for ctoken in comparisonTokens:
    #                         if isinstance(ctoken, Identifier):
    #                             id = ctoken.value
    #                         elif ctoken.ttype is Comparison:
    #                             comp = ctoken.value
    #                         elif ctoken.ttype is not Whitespace:
    #                             value = ctoken.value
    #
    #                     # tell ts format is timestamp or iso
    #                     if value.startswith("'") and value.endswith("'"):
    #                         id = 'iso'
    #                     else:
    #                         id = 'timestamp'
    #
    #                     value = str(value).replace("'", "").replace("+","%2B")
    #
    #                     # If time is relative time
    #                     if value.upper().startswith('NOW'):
    #                         value = self.relativeTimeParser(value, 'iso')
    #
    #                     if comp == '=':
    #                         pointQueryValue.update({id: value})
    #                     elif comp == '>':
    #                         rangeQueryStart.update({id: value})
    #                     elif comp == '<':
    #                         rangeQueryEnd.update({id: value})
    #
    #
    #             if pointQueryValue:
    #                 return pointQuery
    #             if rangeQueryStart:
    #                 return rangeQuery
    #
    # def doQuery(self, dml):
    #     devices = self.getTables(dml)
    #     if not devices:
    #         print 'Device should be provided ...'
    #         return
    #     if len(devices) > 1:
    #         print 'Multi-devices query is not supported now ...'
    #         return
    #     sensors = self.getColumns(dml)
    #     predicate = self.getWhere(dml)
    #     if not predicate:
    #         print 'The select statement does NOT contain WHERE predicates, currently is not supported ...'
    #         return None
    #     query_url = 'data-points'
    #     if predicate.has_key('sampleTime'):
    #         key = 'sampleTime'
    #         value = predicate['sampleTime']
    #     elif predicate.has_key('timeRange'):
    #         key = 'timeRange'
    #         value = predicate['timeRange']
    #         query_url = 'data-rows'
    #     else:
    #         print 'The query is not supported now ...'
    #
    #     sources = {"device": devices[0], "sensors": sensors}
    #     sources[key] = value
    #     select = {"sources": sources}
    #
    #     uri = self.url + '/data/' + query_url + '?select=' + json.dumps(select)
    #     response = get(uri)
    #     pretty(json.loads(response.text))

    def transfer(self, statements):
        for statement in statements:
            if self.isDML(statement):
                dyn_query(self.url, statement)
            elif self.isDDL(statement):
                create_meta(self.url,statement)
            elif self.isKeyword(statement):
                query_meta(self.url,statement)


    def excute(self):
        hostname = socket.gethostname();
        ip = socket.gethostbyname(hostname);

        while True:
            sql = raw_input('[' + hostname + '@' + ip + '] > ')

            if sql.upper() == 'EXIT' or sql.upper() == 'BYE':
                print 'Exit KMX CLI ...'
                return

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


if __name__ == '__main__':
    run()

