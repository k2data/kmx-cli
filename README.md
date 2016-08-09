# kmx-cli
A CLI for KMX query.

Currently, KMX query only support HTTP Rest style query, which is a little bit hard to use for developers.

## KMX Data Point Query
KMX data point query is designed like:
```
http://192.168.130.2/cloud/qa3/kmx/v2/data/data-points?
    select=
        {"sources":
            {
                "device": "device_name",
                "sensors": ["sensor_name"],
                "sampleTime":
                {
                    "timestamp": "1469672032196"
                }
            }
        }
```
If a developer want to have a quick try, he/she will have to input a complex url, which is
very easy to make mistakes, and very frustrating.
A Command line interface which accept SQL like queries may be a better tool to have. KMX CLI
is build to provide developers a easy to use tool.

For above RESTFul query, in kmx-cli, it's like below:
```
select
    device_name
from
    sensor_name
where
    ts=1469672032196
```

## KMX Data Range Query
KMX data range query is more complicate:
```
http://192.168.130.2/cloud/qa3/kmx/v2/data/data-points?
    select=
        {
            "sources":{
                "device":"device_name",
                "sensors":[
                    "sensor_name"
                ],
                "timeRange":{
                    "start":{
                        "iso":"2016-07-28T10:13:52.196%2B08:00"
                    },
                    "end":{
                        "iso":"2016-07-28T10:13:52.644%2B08:00"
                    }
                }
            }
        }
```

kmx-cli style is:
```
select
    device_name
from
    sensor_name
where
    ts>'2016-07-28T10:13:52.196+08:00'
and
    ts<'2016-07-28T10:13:52.644+08:00'
```

## Getting started

### Installation
```
git clone https://github.com/k2data/kmx-cli.git -b dev
python setup.py install
```

### Query data
The only thing you have to do is:
Use URL of your HTTP RESTful query as parameter for kmx-cli.
```
kmx_cli -u http://192.168.130.2/cloud/qa3/kmx/v2
```
or
```
kmx_cli --url http://192.168.130.2/cloud/qa3/kmx/v2
```
Now you are ready to go.

*Note: In Where predicate, there is only ONE keyword 'ts'. Timestamp, iso and relative time are all supported and can be mix used together.*
```
$ kmx_cli -u http://192.168.130.2/cloud/qa3/kmx/v2
URL input is: http://192.168.130.2/cloud/qa3/kmx/v2
KMX CLI is running ...
> select sensor_name from device_name where ts=1469672032196
http://192.168.130.2/cloud/qa3/kmx/v2/data/data-points?select=%7B%22sources%22:%20%7B%22device%22:%20%22device_sync_01_dWavQ%22,%20%22sensors%22:%20[%22DOUBLE_dt_sync_02_dWavQ%22],%20%22sampleTime%22:%20%7B%22timestamp%22:%20%221469672032196%22%7D%7D%7D
{
    "code": 0,
    "dataPoints": [
        {
            "device": "device_name",
            "sensor": "sensor_name",
            "timestamp": 1469672032196,
            "value": 0.0
        }
    ],
    "message": ""
}
```

Use 'bye' or 'exit' to quit kmx-cli
```
> bye
Exit KMX CLI ...
```

#### Relative time support
kmx-cli support relative time for human readable.
```
select sensor_name from device_name where ts>'now-1w' and ts<'now'
select sensor_name from device_name where ts>'now-1h' and ts<'now'
```
relative time format is:
```
^(now)(-)([0-9]+)([s,m,h,d,w]{1})$
```

#### Page and Size keyword support
```
select sensor_name
    from device_name
    where ts > '2015-04-24T20:10:00.000+08:00' and ts < '2015-05-01T07:59:59.000+08:00'
    page 3 size 40
```
*Note, Page and Size is not required, if Page or Size is not set, default value will be used.*

### query metadata

```
show device-types|devices [id]
```
example:
```
show device-types         # query all device-types
show devices deviceid     # query devices who's id = deviceid
```

### create metadata

#### create device-type
```
create device-types device_type_id(sensor1 valueType,sensor2 valueType, ......) tags(t1,t2,...) attributes(k1 v1,k2 v2,....)
```
* valueType is sensor's valueType and must be in [ STRING,DOUBLE,FLOAT,INT,LONG,BOOLEAN]

#### create devices
```
create devices device_id(device_type_id) tags(t1,t2,...) attributes(k1 v1,k2 v2,....)
```
* "tags" should be separated by ',';
* "attributes" should be separated by ',';
* attribute's key and value should be separated by space.
* attribute's key and value does not suppurt space inside it


### import csv data
```
import 'csvfile' into deviceType_id
```
csv file content example:
```
device,iso,sensor1,sensor2,sensor3,sensor4,sensor5,sensor6
d1,iso,DOUBLE,BOOLEAN,INT,LONG,FLOAT,STRING
d1,2016-01-01T12:34:56.789+08:00,34.56789,false,3456789,1451622896789,34.56789,s34.56789
d1,2016-01-01T12:34:57.789+08:00,34.57789,true,3457789,1451622897789,34.57789,s34.57789
```
##### csv file format :
1. the first and second are description of csv data file and it must be writed correctly
2. the first line should be like 'device,${time},sensor1,sensor2......'
3. the second line should be like '${deviceId},${time_format},valueType1,,valueType2......'
4. if ${time} is 'iso' or 'timestamp', ${time_format} in second line will be igored. Otherwise ${time_format} in second should match real format of the time from the third line
5. from the third line,it  be identified as a data line.you should fill in your data that match it description
* file path show be quoted in ''


if  the data items of a data line is less than description line,it will be dropped.
if  the data items of a data line is more than description line,it will be imported but redundant data will be discard.
In short,please make sure the data match it's description



### Batch execution
```
source 'path1','path2'...
```
* "path" can be file or dir.;
*  If input multiple paths, should be separated by ','


script file content example:
```
show devices;
show device-types;
select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts=1469672032196;
```