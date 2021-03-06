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
    sensor_name
from
    device_name
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
    sensor_name
from
    device_name
where
    ts>'2016-07-28T10:13:52.196+08:00'
and
    ts<'2016-07-28T10:13:52.644+08:00'
```

## Getting started

### Installation
```
git clone https://github.com/k2data/kmx-cli.git -b dev
./kmx-cli/install.sh
```

## Query data
The only thing you have to do is:
Use URL of your HTTP RESTful query as parameter for kmx-cli.
```
kmx -u http://192.168.130.2/cloud/qa3/kmx/v2
```
or
```
kmx --url http://192.168.130.2/cloud/qa3/kmx/v2
```
Now you are ready to go.

*Note: In Where predicate, there is only ONE keyword 'ts'. Timestamp, iso and relative time are all supported and can be mix used together.*
```
$ kmx -u http://192.168.130.2/cloud/qa3/kmx/v2
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

And, you can use SELECT * to query all sensors:
```
select * from device_id where ts='now'
```

And, you can select all providing no where predicate
```
select sensor_id1,sensor_id2 from device_id
```
or query by only providing start time or end time
```
select sensor_id1,sensor_id2 from device_id where ts>'now-1w'
select sensor_id1,sensor_id2 from device_id where ts<'now-1d'
```

Use 'bye' or 'exit' to quit kmx-cli
```
> bye
Exit KMX CLI ...
```

### Relative time support
kmx-cli support relative time for human readable.
```
select sensor_name from device_name where ts>'now-1w' and ts<'now'
select sensor_name from device_name where ts>'now-1h' and ts<'now'
```
relative time format is:
```
^(now)(-)([0-9]+)([s,m,h,d,w]{1})$
```

### Page and Size keyword support
```
select sensor_name
    from device_name
    where ts > '2015-04-24T20:10:00.000+08:00' and ts < '2015-05-01T07:59:59.000+08:00'
    page 3 size 40
```
*Note, Page and Size is not required, if Page or Size is not set, default value will be used.*


### Limit support
```
select sensor_name
    from device_name
    limit 400
```

### Order by time support
```
select sensor_name
    from device_name
    order by time desc
```
*Note, currently only time column support order by*

### dynamic data statistic
statistic depends pandas,you must install pandas first
```
sudo apt-get install python-pandas
```
use describe/hist,plot/boxplot to statistic data from data range query
```
select describe(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>1469672032196 and ts<1469672032644;
select hist(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>'2015-07-28 10:13' and ts<'2016-07-28';
select plot(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196%2B08:00' and ts<'2016-07-28T10:13:52.644%2B08:00';
select boxplot(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ where ts>'2016-07-28T10:13:52.196+08:00' and ts<'2016-07-28T10:13:52.644+08:00';
select scatter(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ order by time desc limit 1000;
select step(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ order by time desc limit 1000;
select bar(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ order by time desc limit 1000;
select fill(DOUBLE_dt_sync_02_dWavQ) from device_sync_01_dWavQ order by time desc limit 1000;
```

### export dynamic data
```
select <sensorId>[,<sensorId>...] from <deviceId> [where ts={<timestamp> |'<iso>' | 'relative_time_expr'}]  [page <m> ] [size <n>] into '<outfile_path>'
select * from <deviceId> [where ts={<timestamp> |'<iso>' | 'relative_time_expr'}] [page <m> ] [size <n>] into '<outfile_path>'

```

## Query metadata

```
show {devicetype|device} id
show {devicetypes|devices} [like xxx]|[where key=value]
```
example:
```
show devicetypes         # query all device-types
show devices             # query all devices
show device deviceid     # query devices who's id = deviceid
show devices where devicetype=xxx # qurey all devices whoese deviceTypeId = xxx
show devices like xxx    # query all devices match xxx, wildcard:_,%,*
```

## Create metadata

### Create deviceType
```
create deviceType deviceTypeId(sensor1 valueType,sensor2 valueType, ......) tags(t1,t2,...) attributes(k1 v1,k2 v2,....)
```
* valueType is sensor's valueType and must be in [ STRING,DOUBLE,FLOAT,INT,LONG,BOOLEAN]

### Create device
```
create device device_id(device_type_id) tags(t1,t2,...) attributes(k1 v1,k2 v2,....)
```
* "tags" should be separated by ',';
* "attributes" should be separated by ',';
* attribute's key and value should be separated by space.
* attribute's key and value does not suppurt space inside it

## Drop metadata

### drop devicetype
```
drop devicetype device_type_id [,device_type_id]
```

### drop device
```
drop device device_id [,device_id]
```

## update metadata
### update deviceType
```
update devicetype set tags =(x , xx , xxx), attributes = (k1 v1, "k2" v2) where id='{device_type_id}'',
update devicetype set tags =(x, "xx" , 'xxx'), attributes = ('k1' "v1", "k2" v2) where id="device_type_id",
update devicetype set tags = (x,"xx",'xxx'), attributes=('k1' "v1", "k2" v2) where id=device_type_id,
```
* tags and attributes should be separated by ',' and enclosed with brackets;
* attribute's key and value should be separated by space.
* attribute's key and value does not suppurt space inside it

### update device
```
update device set deviceTypeId={device_type_id} ,tags =(x , 'xx' , "xxx"), attributes = (k1 v1, "k2" v2,'k3' 'v3') where id =device_id
update device set deviceTypeId={'device_type_id}' ,tags =(x , 'xx' , "xxx"), attributes = (k1 v1, "k2" v2,'k3' 'v3') where id ='{device_id}'
update device set deviceTypeId={"device_type_id"} ,tags =(x , 'xx' , "xxx"), attributes = (k1 v1, "k2" v2,'k3' 'v3') where id ="{device_id}""

```
* tags and attributes should be separated by ',' and enclosed with brackets;
* attribute's key and value should be separated by space.


## import csv data
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
### csv file format :
1. the first and second are the descriptions of csv file and it must be written correctly
2. the first line should be like 'device,${time},sensor1,sensor2......'
3. the second line should be like '${deviceId},${time_format},valueType1,,valueType2......'
4. if ${time} is 'iso' or 'timestamp', ${time_format} in second line will be igored. Otherwise ${time_format} in second should match real format of the time from the third line
5. from the third line,it  be identified as a data line.you should fill in your data that match it description
* file path show be quoted in ''


if  the data items of a data line is less than description line,it will be dropped.
if  the data items of a data line is more than description line,it will be imported but redundant data will be discard.
In short,please make sure the data match it's description



## Batch mode
```
source path [,path]...
```
* path can be file or dir.
* in script file ,the line start with '#' or '--' will not be executed.
* in script file ,the 'source' command will be ignored.



script file content example:
```
show devices;
#show device-types;
--select DOUBLE_dt_sync_02_dWavQ from device_sync_01_dWavQ where ts=1469672032196;
```

## Switch URL in context
You can switch URL in kmx-cli, just type "url <new_url>" like:
```
Query URL: http://218.56.128.30:16805/kmx/v2
[rui@127.0.0.1] > url http://192.168.130.2/cloud/qa3/kmx/v2
New URL: http://192.168.130.2/cloud/qa3/kmx/v2
```

## Execute shell command in kmx-cli
Use "!" as suffix to indicate this command is a shell one.
```
[rui@127.0.0.1] > !pwd
/home/pc/PycharmProjects/kmx-cli
```

## Browse command history
Use "history" to browse execution history.
```
[rui@127.0.0.1] > history
show devicetypes
show devices where devicetype = A1
show devices like C302D_
show devices like C302D%
show devices like %302D%
show device C302DE
select oilLevel from C302DE where ts > 'now-1h' and ts < 'now'
select oilLevel,oilTemperature from C302DE where ts > 'now-1h' and ts < 'now'
select oilLevel,oilTemperature from C302DE where ts > 'now-1d' and ts < 'now'
```

For more SQL syntax : https://github.com/k2data/kmx-cli/blob/dev/syntax.md
