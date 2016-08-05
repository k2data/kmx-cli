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


