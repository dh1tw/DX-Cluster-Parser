# Description
The main purpose of this library is decoding & converting all messages from a DX Cluster into structured objects. However it can also be used to check individual callsigns only. Callsign lookup is performed through [AD1C's Country files](http://www.country-files.com/cty/).
All Classes are checked by an extensive set of Unit Tests.

## Content
**spot_processing.py** contains the following four classes:

1. Station(string)
2. Spot(string)
3. WWV(string)
4. Comment(string)

**cty.py** contains one class which loads the Country File:
* load_cty(filename)

**testing.py** contains the Unit Tests for the four classes in spot_processing.py

## General Requirements
The library works under Python 2.7 and does not require any additional external libraries.
Not sure if it will work properly with Python 3.x. 

A copy of the [AD1C's Country File](http://www.country-files.com/cty/) is included in .plist format. But make sure it the latest one.

## spot_processing.py
This gives you a brief description of the Classes in the module spot_processing.py.
### Station(string)
This Class will automatically try to decode a String (which should contain the callsign) and return an object with the attributes below. Lets use the following example:

```python
from spot_processing import Station

stn = Station("EA4/DH1TW/M")
```

The object "stn" from above's example contains the following attributes:
* stn.valid = True (is the callsign valid?)
* stn.call = "EA4/DH1TW/M"
* stn.prefix = "EA"
* stn.homecall = "DH1TW"
* stn.country = "Spain"
* stn.latitude = 40.37
* stn.longitude = 4.88
* stn.cqz = 14 (CQ Zone)
* stn.ituz = 37 (ITU Zone)
* stn.continent = "EU"
* stn.offset = -1.0 (Offset to UTC)
* stn.mm = False (is Martime Mobile?)
* stn.am = False (is Aeronautic Mobile?)
* stn.beacon = False (is a beacon station?)

### Spot(string)
This Class will automatically try to decode the entire DX Spot and return an object with the attributes below. Example:

```python
from spot_processing import Spot, Station

fixture_Spot = "DX de UA3ZBK:    14170.0  UR8EW/QRP    POWER 2-GU81+SPYDER            1211Z"
obj = Spot(fixture_Spot)
```

The object "obj" from above's example contains the following attributes:
* obj.raw_spot = "DX de UA3ZBK:    14170.0  UR8EW/QRP    POWER 2-GU81+SPYDER            1211Z"
* obj.valid = True (Is this spot valid?)
* obj.dx_call = "UR8EW/QRP"
* obj.dx_station = (object type "Station" for UR8EW/QRP)
* obj.spotter_call = "UA3ZBK" 
* obj.spotter_station = (object type "Station" for UA3ZBK)
* obj.frequency = 14170.0
* obj.time = datetime.datetime(2014, 1, 25, 12, 11, tzinfo=<UTC>) (timestamp with current time)
* obj.comment = "POWER 2-GU81+SPYDER           "
* obj.mode = "USB"
* obj.band = 20
* obj.locator = ""

### WWV(string)
This Class will automatically try to decode a Space Weather information and generate an object with the attributes below. It works with WWV and WCY announcements. Example:

```python
from spot_processing import WWV, Station

fixture_WWV = "WWV de W0MU <21>:   SFI=118, A=8, K=2, No Storms -> Minor w/G1 "
obj = WWV(fixture_WWV)
```

The object "obj" from above's example contains the following attributes:
* obj.station = (object type "Station" for W0MU)
* obj.time = datetime.datetime(2014, 1, 25, 21, 0, tzinfo=<UTC>) (timestamp with current time)
* obj.a = 8
* obj.sfi = 118
* obj.k = 2
* obj.expk = None
* obj.r = None
* obj.aurora = False
* obj.valid = True


### Comment(string)
This Class will automatically try to decode a DX Cluster Comment and generate an object with the attributes below. Example:

```python
from spot_processing import Comment, Station

fixture_comment = "To ALL de IK8CNT: UA4WHX pse beaming south        "
obj = Comment(fixture_comment)
```

The object "obj" from above's example contains the following attributes:
* obj.station = (object type "Station" for IK8CNT)
* obj.time = datetime.datetime(2014, 1, 25, 21, 0, tzinfo=<UTC>) (timestamp with current time)
* obj.text = 'UA4WHX pse beaming south'
* obj.valid = True


## Unit Testing
When you decide to modify / improve the code, you should update the Unit tests and run them frequently. This will help you whenever your change breaks something which worked before. It's very easy to add, modify & run python unit tests.
### Example
```shell
python testing.py
```
A successfull run will look like this:
```shell
test_comment_all_properties_fixture_1 (__main__.TestSequenceFunctions) ... ok
test_comment_all_properties_fixture_2 (__main__.TestSequenceFunctions) ... ok
test_comment_invalid_call_1 (__main__.TestSequenceFunctions) ... ok
test_comment_invalid_call_2 (__main__.TestSequenceFunctions) ... ok
test_comment_invalid_input (__main__.TestSequenceFunctions) ... ok
test_comment_invalid_no_semicolon (__main__.TestSequenceFunctions) ... ok
test_comment_regex_fixture_3 (__main__.TestSequenceFunctions) ... ok
test_spot_complete_and_valid (__main__.TestSequenceFunctions) ... ok
test_spot_frequency (__main__.TestSequenceFunctions) ... ok
test_spot_frequency_and_call_without_semicolon (__main__.TestSequenceFunctions) ... ok
test_spot_invalid_frequencies (__main__.TestSequenceFunctions) ... ok
test_station_aerotime_mobile_flag (__main__.TestSequenceFunctions) ... ok
test_station_all_properties_with_a_valid_call (__main__.TestSequenceFunctions) ... ok
test_station_beacon_flag (__main__.TestSequenceFunctions) ... ok
test_station_invalid_calls_with_special_characters (__main__.TestSequenceFunctions) ... ok
test_station_lighthouse (__main__.TestSequenceFunctions) ... ok
test_station_martime_mobile_flag (__main__.TestSequenceFunctions) ... ok
test_station_mobile (__main__.TestSequenceFunctions) ... ok
test_station_number_appendix (__main__.TestSequenceFunctions) ... ok
test_station_portable (__main__.TestSequenceFunctions) ... ok
test_station_with_invalid_calls (__main__.TestSequenceFunctions) ... ok
test_station_with_valid_calls (__main__.TestSequenceFunctions) ... ok
test_wwv_all_properties_fixture_1 (__main__.TestSequenceFunctions) ... ok
test_wwv_all_properties_fixture_11 (__main__.TestSequenceFunctions) ... ok
test_wwv_all_properties_fixture_5 (__main__.TestSequenceFunctions) ... ok
test_wwv_aurora_fixture_12 (__main__.TestSequenceFunctions) ... ok
test_wwv_invalid_parameters_1 (__main__.TestSequenceFunctions) ... ok
test_wwv_invalid_parameters_2 (__main__.TestSequenceFunctions) ... ok
test_wwv_invalid_parameters_3 (__main__.TestSequenceFunctions) ... ok
test_wwv_invalid_parameters_4 (__main__.TestSequenceFunctions) ... ok
test_wwv_invalid_parameters_5 (__main__.TestSequenceFunctions) ... ok

----------------------------------------------------------------------
Ran 31 tests in 0.058s

OK
```

## Known issues
* Callsign recognition is very good, but not perfect;



