# Process a DX-Cluster spot and return Spot, Callsign, WWV and Comment as objects 
# Copyright (c) 2014 Tobias Wellnitz, DH1TW
	
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Please fork and contribute your improvements to the Github Repository
# at https://github.com/dh1tw/DX-Cluster-Parser

# This file contains the unit tests for the classes in spot_processing.py
# If you modify Classes it's useful to run the unit tests to make sure 
# nothing has broken.

# Execute the unit tests from command line: "python testing.py"

import sys
import re
import pytz
from pytz import timezone
from datetime import datetime, time, date, tzinfo
import time
import logging
from logging import StreamHandler
import atexit
import unittest
from spot_processing import Station, Spot, WWV, Comment
UTC = pytz.utc

rootlogger = "dxcsucker"

#Define a root logger which is needed for spot_processing Classes
def get_logger(name):
	logger = logging.getLogger(name)
	console_handler = StreamHandler()
	default_formatter = logging.Formatter("[%(levelname)s] [%(asctime)s] [%(module)s]: %(message)s","%d/%m/%Y %H:%M:%S")
	console_handler.setFormatter(default_formatter)
	logger.addHandler(console_handler)
	logger.setLevel(logging.CRITICAL) #adjust to the level of information you want to see
	return(logger)

logger = get_logger(rootlogger)

fixture_spot1 = "DX de CT3FW:     21004.8  HC2AO        599 TKS(CW)QSL READ,QRZ.COM    2132Z"

fixture_spot1_time = datetime.utcnow().replace( hour=21, minute=32, second=0, microsecond = 0, tzinfo=UTC)

fixture_spot2 = "DX de DL6NAA: 10368887.0  DL7VTX/B     55s in JO50VFjo62 never hrd B4 1505Z"
fixture_spot3 = "DX de CT3FW:     21004.8  IDIOT        599 TKS(CW)QSL READ,QRZ.COM    2132Z"
fixture_spot4 = "DX de OK1TEH:   144000.0  C0NTEST      -> www.darkside.cz/qrv.php     1328Z JO70"
fixture_spot5 = "DX de DK7UK:     50099.0  EA5/ON4CAU   JN48QT<ES>IM98 QRP 5W LOOP ANT 1206Z"
fixture_spot6 = "DX de UA3ZBK:    14170.0  UR8EW/QRP    POWER 2-GU81+SPYDER            1211Z"
fixture_spot7 = "DX de 9K2/K2SES  14205.0  DK0HY                                       0921Z" #missing semicolon
fixture_spot8 = "DX de DK1CS:9330368887.0  DL7VTX/B                                    1505Z"
fixture_spot9 = "DX de DH1TW:        23.0  DS1TW                                       1505Z"
fixture_spot10 = "DX de DH1TW    234.0  DS1TW                                          1505Z"
fixture_spot11 = "DX de DH1TW:       234.0  DS1TW                                       1505Z"
fixture_spot12 = "DX de DH1TW:     50105.0  ZD6DYA                                      1505Z"

fixture_wwv1 = "WWV de VE7CC <09>:   SFI=113, A=18, K=2, Minor w/G1 -> No Storms"
fixture_wwv2 = "WWV de VE7CC <12>:   SFI=113, A=18, K=2, No Storms -> No Storms"
fixture_wwv3 = "WWV de VE7CC <15>:   SFI=113, A=18, K=2, No Storms -> No Storms"
fixture_wwv4 = "WWV de VE1DX <18>:   SFI=113, A=18, K=2, No Storms -> No Storms"
fixture_wwv5 = "WWV de W0MU <21>:   SFI=118, A=8, K=2, No Storms -> Minor w/G1 "
fixture_wwv6 = "WWV de W0MU <00>:   SFI=118, A=9, K=3, No Storms -> Minor w/G1 "
fixture_wwv7 = "WWV de W0MU <03>:   SFI=118, A=9, K=4, No Storms -> Minor w/G1 "
fixture_wwv8 = "WWV de VE7CC <06>:   SFI=118, A=9, K=3, No Storms -> Minor w/G1 "
fixture_wwv9 = "WWV de W0MU <09>:   SFI=118, A=9, K=2, No Storms -> Minor w/G1 "
fixture_wwv10 = "WWV de W0MU <12>:   SFI=118, A=9, K=1, No Storms -> Minor w/G1"
fixture_wwv11 = "WCY de DK0WCY-2 <20> : K=3 expK=3 A=23 R=88 SFI=113 SA=eru GMF=min Au=no"
fixture_wwv12 = "WCY de DK0WCY-10 <20> : K=3 expK=3 A=23 R=88 SFI=113 SA=eru GMF=min Au=yes"
fixture_wwv_invalid_1 = "WWC de W0MU <12>:   SFI=118, A=9, K=1, No Storms -> Minor w/G1"
fixture_wwv_invalid_2 = "WWC de W0MU <12>:   SFI=118, A=XX, K=1,"
fixture_wwv_invalid_3 = "WWC de W0MU <12>:   SFI=118, A=, K=1,"
fixture_wwv_invalid_4 = "WWC de W0MU <12>:   SFI=118,A=5, K=1,"
fixture_wwv_invalid_5 = "WWC de W0MU <12>:   SFI=118, A=1215, K=1,"
fixture_wwv_invalid_6 = "WWC de W0MU <12>:   SFI=118, A=1215, K=1,"
fixture_comment_1 = "To ALL de IK8CNT: UA4WHX pse beaming south        "
fixture_comment_2 = "To ALL de DL5ML: to DX0HQ pse lsn for EU        "
fixture_comment_3 = 'TO ALL de DL5ML: "$%&*.* to DX0HQ pse lsn for EU        '
fixture_comment_invalid_1 = "ALL de DL5ML: to DX0HQ pse lsn for EU        "
fixture_comment_invalid_2 = "TO ALL de 222DL5ML: to DX0HQ pse lsn for EU        "
fixture_comment_invalid_3 = "TO ALL de DL5ML to DX0HQ pse lsn for EU        "
fixture_comment_invalid_4 = "TO ALL de: to DX0HQ pse lsn for EU        "



class TestSequenceFunctions(unittest.TestCase):
	
	def test_comment_all_properties_fixture_1(self):
		self.assertEqual(Comment(fixture_comment_1).station.call, "IK8CNT")
	#	self.assertEqual(Comment(fixture_comment_1).time, type(datetime.datetime))
		self.assertEqual(Comment(fixture_comment_1).text, "UA4WHX pse beaming south")
		self.assertEqual(Comment(fixture_comment_1).valid, True)

	def test_comment_all_properties_fixture_2(self):
		self.assertEqual(Comment(fixture_comment_2).station.call, "DL5ML")
		self.assertEqual(Comment(fixture_comment_2).text, "to DX0HQ pse lsn for EU")
		self.assertEqual(Comment(fixture_comment_2).valid, True)
		
	def test_comment_regex_fixture_3(self):
		self.assertEqual(Comment(fixture_comment_3).station.call, "DL5ML")
		self.assertEqual(Comment(fixture_comment_3).text, " $ & . to DX0HQ pse lsn for EU")

	def test_comment_invalid_input(self):
		self.assertRaises(Exception, Comment(fixture_comment_invalid_1))
		self.assertEqual(Comment(fixture_comment_invalid_1).valid, False)

	def test_comment_invalid_call_1(self):
		self.assertEqual(Comment(fixture_comment_invalid_2).valid, False)
		self.assertRaises(Exception, Comment(fixture_comment_invalid_2))

	def test_comment_invalid_no_semicolon(self):
		self.assertRaises(Exception, Comment(fixture_comment_invalid_3))
		self.assertEqual(Comment(fixture_comment_invalid_3).valid, False)
	
	def test_comment_invalid_call_2(self):
		self.assertEqual(Comment(fixture_comment_invalid_4).valid, False)
		self.assertRaises(Exception, Comment(fixture_comment_invalid_4))
	
	
	def test_wwv_all_properties_fixture_1(self):
		self.assertEqual(WWV(fixture_wwv1).station.call, "VE7CC")
		test_time = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=UTC)
		self.assertEqual(WWV(fixture_wwv1).time, test_time)
		self.assertEqual(WWV(fixture_wwv1).a, 18)
		self.assertEqual(WWV(fixture_wwv1).k, 2)
		self.assertEqual(WWV(fixture_wwv1).sfi, 113)
		self.assertEqual(WWV(fixture_wwv1).expk, None)
		self.assertEqual(WWV(fixture_wwv1).r, None)
		self.assertEqual(WWV(fixture_wwv1).aurora, False)
		self.assertEqual(WWV(fixture_wwv1).valid, True)
		
	def test_wwv_all_properties_fixture_5(self):
		self.assertEqual(WWV(fixture_wwv5).station.call, "W0MU")
		test_time = datetime.utcnow().replace(hour=21, minute=0, second=0, microsecond=0, tzinfo=UTC)
		self.assertEqual(WWV(fixture_wwv5).time, test_time)
		self.assertEqual(WWV(fixture_wwv5).a, 8)
		self.assertEqual(WWV(fixture_wwv5).k, 2)
		self.assertEqual(WWV(fixture_wwv5).sfi, 118)
		self.assertEqual(WWV(fixture_wwv5).expk, None)
		self.assertEqual(WWV(fixture_wwv5).r, None)
		self.assertEqual(WWV(fixture_wwv5).aurora, False)
		self.assertEqual(WWV(fixture_wwv5).valid, True)

	def test_wwv_all_properties_fixture_11(self):
		self.assertEqual(WWV(fixture_wwv11).station.call, "DK0WCY-2")
		test_time = datetime.utcnow().replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=UTC)
		self.assertEqual(WWV(fixture_wwv11).time, test_time)
		self.assertEqual(WWV(fixture_wwv11).a, 23)
		self.assertEqual(WWV(fixture_wwv11).k, 3)
		self.assertEqual(WWV(fixture_wwv11).sfi, 113)
		self.assertEqual(WWV(fixture_wwv11).expk, 3)
		self.assertEqual(WWV(fixture_wwv11).r, 88)
		self.assertEqual(WWV(fixture_wwv11).aurora, False)
		self.assertEqual(WWV(fixture_wwv11).valid, True)

	def test_wwv_aurora_fixture_12(self):
		self.assertEqual(WWV(fixture_wwv12).station.call, "DK0WCY-10")
		test_time = datetime.utcnow().replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=UTC)
		self.assertEqual(WWV(fixture_wwv12).aurora, True)
		self.assertEqual(WWV(fixture_wwv12).valid, True)


	def test_wwv_invalid_parameters_1(self):
		self.assertRaises(Exception, WWV(fixture_wwv_invalid_1))
		self.assertEqual(WWV(fixture_wwv_invalid_1).valid, False)

	def test_wwv_invalid_parameters_2(self):
		self.assertRaises(Exception, WWV(fixture_wwv_invalid_2))
		self.assertEqual(WWV(fixture_wwv_invalid_2).valid, False)
	
	def test_wwv_invalid_parameters_3(self):
		self.assertRaises(Exception, WWV(fixture_wwv_invalid_3))
		self.assertEqual(WWV(fixture_wwv_invalid_3).valid, False)
	
	def test_wwv_invalid_parameters_4(self):
		self.assertRaises(Exception, WWV(fixture_wwv_invalid_4))
		self.assertEqual(WWV(fixture_wwv_invalid_4).valid, False)

	def test_wwv_invalid_parameters_5(self):
		self.assertRaises(Exception, WWV(fixture_wwv_invalid_5))
		self.assertEqual(WWV(fixture_wwv_invalid_5).valid, False)

	def test_station_all_properties_with_a_valid_call(self):
		self.assertEqual(Station("HC2/DH1TW/P").prefix, "HC")
		self.assertEqual(Station("HC2/DH1TW/P").valid, True)
		self.assertEqual(Station("HC2/DH1TW/P").call, "HC2/DH1TW/P")
		self.assertEqual(Station("HC2/DH1TW/P").homecall, "DH1TW")
		self.assertEqual(Station("HC2/DH1TW/P").country, "Ecuador")
		self.assertEqual(Station("HC2/DH1TW/P").latitude, -1.4)
		self.assertEqual(Station("HC2/DH1TW/P").longitude, 78.4)
		self.assertEqual(Station("HC2/DH1TW/P").cqz, 10)
		self.assertEqual(Station("HC2/DH1TW/P").ituz, 12)
		self.assertEqual(Station("HC2/DH1TW/P").continent, "SA")
		self.assertEqual(Station("HC2/DH1TW/P").mm, False)
		self.assertEqual(Station("HC2/DH1TW/P").beacon, False)
		self.assertEqual(Station("HC2/DH1TW/P").am, False)
		
	def test_station_with_valid_calls(self):
		self.assertEqual(Station("DH1T").prefix, "DH")
		self.assertEqual(Station("DH1TW/P").prefix, "DH")
		self.assertEqual(Station("DH1TW/MM").prefix, False)
		self.assertEqual(Station("DH1TW/AM").prefix, False)
		self.assertEqual(Station("DH1TW/VP5").prefix, "VP5")
		self.assertEqual(Station("VP5/DH1TW").prefix, "VP5")
		self.assertEqual(Station("VP5/DH1TW/P").prefix, "VP5")
		self.assertEqual(Station("MM/DH1TW/P").prefix, "MM")
		self.assertEqual(Station("DH1TW/QRP").prefix, "DH")
		self.assertEqual(Station("DH1TW/QRPP").prefix, "DH")		
		self.assertEqual(Station("MM/DH1TW/QRP").prefix, "MM")
		self.assertEqual(Station("MM/DH1TW/QRPP").prefix, "MM")
		self.assertEqual(Station("MM/DH1TW/B").prefix, "MM")
		self.assertEqual(Station("MM/DH1TW/BCN").prefix, "MM")
		self.assertEqual(Station("EA1/DH1TW").prefix, "EA")
		self.assertEqual(Station("EA1/DH1TW/P").prefix, "EA")
		self.assertEqual(Station("DH1TW/EA1").prefix, "EA")
		self.assertEqual(Station("DH1TW/EA").prefix, "EA")
		self.assertEqual(Station("VP2E/AL1O/P").prefix, "VP2E")
		self.assertEqual(Station("VP2E/DL2001IRTA/P").prefix, "VP2E")
		self.assertEqual(Station("CD4300").prefix, "CD")
		self.assertEqual(Station("CD4300").country, "Chile")		
		self.assertEqual(Station("CD4300").homecall, "CD4300")
		self.assertEqual(Station("DH1TW/EA8/QRP").prefix, "EA8")
		self.assertEqual(Station("W0ERE/B").prefix, "W0")
		self.assertEqual(Station("W0ERE/B").valid, True)
		self.assertEqual(Station("ER/KL1A").prefix, "ER")
		self.assertEqual(Station("DL4SDW/HI3").prefix, "HI")
		self.assertEqual(Station("SV9/M1PAH/HH").prefix, 'SV9')
		self.assertEqual(Station("8J3XVIII").prefix, '8J')
		self.assertEqual(Station("DL4SDW/HI3").prefix, 'HI')
		self.assertEqual(Station("9A28HQ").prefix, '9A')
		self.assertEqual(Station("RU27TT").prefix, 'R')
		self.assertEqual(Station("UE90K").prefix, 'UE9')
		self.assertEqual(Station("DL2000ALMK").prefix, 'DL')
		self.assertEqual(Station("HF450NS").prefix, "HF")	
		self.assertEqual(Station("GB558VUL").prefix, "G")	
		self.assertEqual(Station("F/ON5OF").prefix, 'F')
		self.assertEqual(Station("OX1A/OZ1ABC").prefix, "OX")
		self.assertEqual(Station("OX1A/OZ").prefix, "OZ")
		self.assertEqual(Station("OZ5V").prefix, "OZ")
		self.assertEqual(Station("OV9DV").prefix, "OV")
		self.assertEqual(Station("CQ59HQ").prefix, "CQ")
		self.assertEqual(Station("RW3DQC/1/P").prefix, "R")
		self.assertEqual(Station("RW3DQC/1/P").homecall, "RW3DQC")
		self.assertEqual(Station("DB0SUE-10").prefix, "DB")
		self.assertEqual(Station("DK0WYC-2").prefix, "DK")
		self.assertEqual(Station("DK0WYC-2").valid, True)
		self.assertEqual(Station("G0KTD/P").prefix, "G")
	#	self.assertEqual(Station("ED8ZAB/RPT").prefix, "ED8")
	#	self.assertEqual(Station("HB9FAX/I").prefix, "I")
		
	def test_station_with_invalid_calls(self):
		self.assertEqual(Station("DH").valid, False)
		self.assertEqual(Station("DH1").valid, False)		
		self.assertEqual(Station("DH1TW/012").valid, False)
		self.assertEqual(Station("01A/DH1TW").valid, False)
		self.assertEqual(Station("01A/DH1TW/P").valid, False)
		self.assertEqual(Station("01A/DH1TW/MM").valid, False)
		self.assertEqual(Station("QSL").valid, False)
		self.assertEqual(Station("QRV").valid, False)
		self.assertEqual(Station("T0NTO").valid, False)
		self.assertEqual(Station("T0ALL").valid, False)
		self.assertEqual(Station("H1GHMUF").valid, False)
		self.assertEqual(Station("C1BBI").valid, False)
		self.assertEqual(Station("PU1MHZ/QAP").valid, False)
		self.assertEqual(Station("DU7/PA0").valid, False)
		self.assertEqual(Station("DIPLOMA").valid, False)		
		self.assertEqual(Station("CQAS").valid, False)
		self.assertEqual(Station("IK2SAV/P1").valid, False)
		self.assertEqual(Station("IKOFTA").valid, False)
		self.assertEqual(Station("SP2/SP3").valid, False)
		self.assertEqual(Station("CQ").valid, False)
		self.assertEqual(Station("RADAR").valid, False)
		self.assertEqual(Station("MUF/INFO").valid, False)
		self.assertEqual(Station("RAVIDEO").valid, False)
		self.assertEqual(Station("PIRATE").valid, False)
		self.assertEqual(Station("XE1/H").valid, False)
		self.assertEqual(Station("Z125VZ").valid, False)
		self.assertEqual(Station("ZD6DYA").prefix, False)		
		self.assertEqual(Station("ZD6DYA").valid, False)
		self.assertEqual(Station("F5BUU1").valid, False)
		self.assertEqual(Station("0").valid, False)
		self.assertEqual(Station("0123456789").valid, False)
		self.assertEqual(Station("CD43000").valid, False)	
		self.assertEqual(Station("GN").valid, False)	
		self.assertEqual(Station("GN").homecall, False)	
		self.assertEqual(Station("ARABS").homecall, False)	
		self.assertEqual(Station("2320900").valid, False)	
		self.assertEqual(Station("ITT9APL").valid, False)
	#	self.assertEqual(Station("EA5/G0K").valid, False)
		self.assertEqual(Station("MUF").valid, False)
	#	self.assertEqual(Station("EU5STATIONS").valid, False)

	def test_station_lighthouse(self):
		self.assertEqual(Station("DH1TW/LH").valid, True)
		self.assertEqual(Station("DH1TW/LH").prefix, "DH")
		self.assertEqual(Station("UR7GO/P/LH").valid, True)
		self.assertEqual(Station("UR7GO/P/LH").prefix, "UR")
		
	def test_station_portable(self):
		self.assertEqual(Station("MM/DH1TW/P").valid, True)
		self.assertEqual(Station("MM/DH1TW/P").prefix, "MM")
		
	def test_station_mobile(self):
		self.assertEqual(Station("VK3/DH1TW/M").valid, True)
		self.assertEqual(Station("VK3/DH1TW/M").prefix, "VK")	
		
	def test_station_number_appendix(self):
		self.assertEqual(Station("DH1TW/EA3").prefix, "EA")
		self.assertEqual(Station("YB9IR/3").prefix, "YB3")
		self.assertEqual(Station("UA9MAT/1").prefix, "U")		
		self.assertEqual(Station("W3LPL/5").prefix, "W5")
		self.assertEqual(Station("UA9KRM/3").prefix, "U")
		self.assertEqual(Station("UR900CC/4").prefix, "UR")
		
	def test_station_invalid_calls_with_special_characters(self):
		self.assertEqual(Station("DK()DK").valid, False)
		self.assertEqual(Station("DK/DK").valid, False)
		self.assertEqual(Station("'!$&/()@").valid, False)
		self.assertEqual(Station("").valid, False)
		
	def test_spot_frequency(self):
		self.assertEqual(Spot(fixture_spot1).frequency, 21004.8)
		self.assertEqual(Spot(fixture_spot2).frequency, 10368887.0)
		self.assertEqual(Spot(fixture_spot3).frequency, 21004.8)
		self.assertEqual(Spot(fixture_spot4).frequency, 144000.0)
		self.assertEqual(Spot(fixture_spot5).frequency, 50099.0)
		self.assertEqual(Spot(fixture_spot6).frequency, 14170.0)
	
	def test_spot_frequency_and_call_without_semicolon(self):
		self.assertEqual(Spot(fixture_spot7).frequency, 14205.0)
		self.assertEqual(Spot(fixture_spot7).spotter_station.call, '9K2/K2SES')
		self.assertEqual(Spot(fixture_spot7).dx_station.call, 'DK0HY')

	def test_spot_invalid_frequencies(self):
		self.assertRaises(Exception, Spot(fixture_spot8))
		
	def test_spot_complete_and_valid(self):
		self.assertEqual(Spot(fixture_spot1).valid, True)
		self.assertEqual(Spot(fixture_spot1).dx_station.valid, True)
		self.assertEqual(Spot(fixture_spot1).spotter_station.valid, True)
		self.assertEqual(Spot(fixture_spot1).frequency, 21004.8)
		self.assertEqual(Spot(fixture_spot1).time, fixture_spot1_time)
		self.assertEqual(Spot(fixture_spot1).band, 15)
	
	def test_station_beacon_flag(self):
		self.assertEqual(Station("DH1TW/BCN").beacon, True)
		self.assertEqual(Station("DH1TW/BCN").valid, True)
		self.assertEqual(Station("DH1TW/B").beacon, True)
		self.assertEqual(Station("DH1TW/B").valid, True)
		self.assertEqual(Station("VP2M/DH1TW/BCN").valid, True)
		self.assertEqual(Station("VP2M/DH1TW/BCN").beacon, True)
		self.assertEqual(Station("VP2M/DH1TW").beacon, False)
			
	def test_station_aerotime_mobile_flag(self):
		self.assertEqual(Station("DH1TW/AM").am, True)
		self.assertEqual(Station("DH1TW/AM").valid, False)
		self.assertEqual(Station("VP2M/DH1TW/AM").am, True)
		self.assertEqual(Station("VP2M/DH1TW/AM").valid, False)
		self.assertEqual(Station("VP2M/DH1TW").valid, True)
		self.assertEqual(Station("VP2M/DH1TW").am, False)

	def test_station_martime_mobile_flag(self):
		self.assertEqual(Station("DH1TW/MM").mm, True)
		self.assertEqual(Station("DH1TW/MM").valid, False)
		self.assertEqual(Station("DH1TW/MM").prefix, False)
		self.assertEqual(Station("VP2M/DH1TW/MM").mm, True)
		self.assertEqual(Station("VP2M/DH1TW/MM").valid, False)
		self.assertEqual(Station("VP2M/DH1TW").valid, True)
		self.assertEqual(Station("VP2M/DH1TW").mm, False)
		self.assertEqual(Station("R7GA/MM").valid, False)
		self.assertEqual(Station("R7GA/MM").prefix, False)
		self.assertEqual(Station("R7GA/MM").mm, True)

if __name__ == "__main__": 
	#unittest.main()
	suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
	unittest.TextTestRunner(verbosity=2).run(suite)