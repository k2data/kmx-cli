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
                "device": "device_sync_01_dWavQ",
                "sensors": ["DOUBLE_dt_sync_02_dWavQ"],
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
    DOUBLE_dt_sync_02_dWavQ
from
    device_sync_01_dWavQ
where
    timestamp=1469672032196
```

## KMX Data Range Query
KMX data range query is more complicate:
```
http://192.168.130.2/cloud/qa3/kmx/v2/data/data-points?
    select=
        {
            "sources":{
                "device":"device_sync_01_dWavQ",
                "sensors":[
                    "DOUBLE_dt_sync_02_dWavQ"
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
    DOUBLE_dt_sync_02_dWavQ
from
    device_sync_01_dWavQ
where
    iso>'2016-07-28T10:13:52.196%2B08:00'
and
    iso<'2016-07-28T10:13:52.644%2B08:00'
```

## Getting started

### Installation
```
git clone https://github.com/k2data/kmx-cli.git -b dev
python setup.py install
```

### Give it a try
The only thing you have to do is:
Use URL of your HTTP RESTful query as parameter for kmx-cli.
```
kmx_cli -u http://192.168.130.2/cloud/qa3/kmx/v2
```
or
```
kmx_cli --url http://192.168.130.2/cloud/qa3/kmx/v2```
```
Now you are ready to go.
```
$ kmx_cli -u http://192.168.130.2/cloud/qa3/kmx/v2
URL input is: http://192.168.130.2/cloud/qa3/kmx/v2
KMX CLI is running ...
> select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where timestamp=1469672032196
http://192.168.130.2/cloud/qa3/kmx/v2/data/data-points?select=%7B%22sources%22:%20%7B%22device%22:%20%22device_sync_01_dWavQ%22,%20%22sensors%22:%20[%22DOUBLE_dt_sync_02_dWavQ%22],%20%22sampleTime%22:%20%7B%22timestamp%22:%20%221469672032196%22%7D%7D%7D
{
    "code": 0,
    "dataPoints": [
        {
            "device": "device_sync_01_dWavQ",
            "sensor": "DOUBLE_dt_sync_02_dWavQ",
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

### query metadata
support query metadata from 2016.08.03

```
show device-types|devices [id]
```
example:
```
show device-types         # query all device-types
show devices deviceid     # query devices who's id = deviceid
```

### create metadata
support create metadata from 2016.08.03

#### create device-type
```
create device-types id(s1 valueType,s2 valueType, ......)
```
id is your deviceTypeId
s1,s2,....sn are sensorId
valueType is sensor's valueType and must be in [ STRING,DOUBLE,FLOAT,INT,LONG,BOOLEAN]

#### create devices
```
create devices id(deviceTypeId) tags(t1,t2,...) attributes(k1 v1,k2 v2,....)
```
id is your deviceId
deviceTypeId is the deviceType that the device related to.
tags should be separated by ,
attributes must be separated by , . attribute's key and value separated by space


