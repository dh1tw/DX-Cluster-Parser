#!/usr/bin/python
# Filename: spot_processing.py

import re
import pytz
from pytz import timezone
from datetime import datetime, time, date, tzinfo
from cty import load_cty
import logging
import os.path

#------------------CONSTANTS --------------------
UTC = pytz.utc
root_logger = "dxcsucker"

def get_configured_logger(name):
	logger = logging.getLogger(name)
	if (len(logger.handlers) == 0):
		# This logger has no handlers, so we can assume it hasn't yet been configured
		# (Configure logger)
		
		#Define Formatters
		formatter_simple="[%(levelname)s] [%(module)s]: %(message)s"
		formatter_verbose=("[%(levelname)s] [%(asctime)s] [%(module)s]: %(message)s","%d/%m/%Y %H:%M:%S")

		#Define & Configure Handlers
		console_handler = logging.StreamHandler() #outputs to the console
		console_handler.setLevel(logging.DEBUG) #adjust level to your needs
		file_handler = logging.FileHandler("spot_processing.log") #outputs into this file
		file_handler.setLevel(logging.ERROR) #adjust logging level to your needs

		#Instanciate Root logger
		logger = logging.getLogger()

		#Assign Formatter to Handler
		console_handler.setFormatter(logging.Formatter(formatter_simple))
		file_handler.setFormatter(logging.Formatter(formatter_verbose))
		
		#Assign Handler to Logger
		logger.addHandler(console_handler)
		logger.addHandler(file_handler)
		
		return logger
		
	else: #return root logger
		return logger
		


class Station(object):
	#------------------Constructor --------------------
	def __init__(self, call):
	#	super(Station, self).__init__()
		self._logger = get_configured_logger(root_logger)
		self._logger.propagate = True #send all log events to higher logger which has a handler
		
		self.valid = None
		self.call = None
		self.prefix = None
		self.homecall = None
		self.country = None
		self.latitude = None
		self.longitude = None
		self.cqz = None
		self.ituz = None
		self.continent = None
		self.offset = None
		self.mm = False
		self.am = False
		self.beacon = False
		self.call = call.rstrip().lstrip().upper()
		self.homecall = self.obtain_homecall(self.call)
		if not self.homecall:
			self.valid = False
			self._logger.warning("Busted Homecall: '"+ str(self.homecall) + "' of " + self.call + " could not be decoded")
		else:
			self.prefix = self.obtain_prefix(self.call)
			if not self.prefix:
				self.valid = False
				if not self.mm and not self.am:
					self._logger.warning("Busted Prefix: '"+ str(self.prefix) + "' of " + self.call + " could not be decoded")
			else:
				cty_info = self.lookup_cty_info(self.prefix)
				if not cty_info:
					self.valid = False
					self._logger.warning("Busted: No Country Info found for " + self.call )
					
				else:
					self.country = cty_info['country']
					self.latitude = cty_info['latitude']
					self.longitude = cty_info['longitude']
					self.cqz = cty_info['cqz']
					self.ituz = cty_info['ituz']
					self.continent = cty_info['continent']
					self.offset = cty_info['offset']
					self.valid = True

	#------------------STATIC Variables --------------------
	dxcc = ""
	try: 
		if os.path.isfile("./dxcsucker/cty.plist"):
			dxcc = load_cty("./dxcsucker/cty.plist") #Load Country File
		elif os.path.isfile("cty.plist"):
			dxcc = load_cty("cty.plist") #Load Country File
		else:
			self._logger.critical("CTY.PLIST could not be loaded!")
			raise Exception("cty.plist not found!")
	except Exception as e:
		self._logger.exception("CTY.PLIST could not be loaded!")
		
	#------------------Class Methods --------------------		
	def __iterate_prefix(self, call):
		"""truncate call until it corresponds to a Prefix in the database"""
		prefix = call
		while (prefix in Station.dxcc) != True: 
			if len(prefix) == 0:
				break
			else:
				prefix = prefix.replace(' ','')[:-1]
		return(prefix)

	def obtain_homecall(self, raw_call):
		"""verify call and strip off any /ea1 vp5/ /qrp etc"""
		try:
			raw_call = raw_call.upper()
			#--------identify Homecall in case the callsign has an appendix (e.g. call: DH1TW/VP5, homecall: DH1TW) ------------
			homecall = re.search('[\d]{0,1}[A-Z]{1,2}\d([A-Z]{1,4}|\d{3,3}|\d{1,3}[A-Z])[A-Z]{0,5}', raw_call, re.I)
			if homecall:
				homecall = homecall.group(0)
			else:
				return(False)
			return(homecall)
		except Exception as e:
			self._logger.debug(str(e))
			return(False)
	
	
	def obtain_prefix(self, call):
		try:
			entire_call = call.upper()
			#self._logger.debug("obtain_prefix(): call " + call)
			if re.search('[/A-Z0-9\-]{3,15}', entire_call, re.I):  #make sure the call has at least 3 characters
				
				if re.search('\-\d{1,3}$', entire_call, re.I): #cut off any -10 / -02 appendixes
					call = re.sub('\-\d{1,3}$', '', entire_call)
				
				if re.search('/[A-Z0-9]{2,4}/[A-Z0-9]{1,4}$', call):
					call = re.sub('/[A-Z0-9]{1,4}$', '', call) # cut off 2. appendix DH1TW/HC2/P -> DH1TW/HC2

				if re.search('/[A-Z0-9]{2,4}$', call):  # case call/xxx, but ignoring /p and /m or /5
					appendix = re.search('/[A-Z0-9]{1,4}$', call)
					appendix = re.sub('/', '', appendix.group(0))
					self._logger.debug("obtain_prefix(): appendix: " + appendix)
					
					if appendix == 'MM': 				# special case Martime Mobile
						self.mm = True
						self._logger.debug("obtain_prefix(): return False (case /MM)")
						return(False)
					elif appendix == 'AM':				# special case Aeronautic Mobile
						self._logger.debug("obtain_prefix(): return False (case /AM)")
						self.am = True
						return(False)
					elif appendix == 'QRP':			# special case QRP
						call = re.sub('/QRP', '', call)
						prefix = self.__iterate_prefix(call)
						self._logger.debug("obtain_prefix(): prefix: "+ str(prefix) + " (case /QRP)")
					elif appendix == 'QRPP':			# special case QRPP
						call = re.sub('/QRPP', '', call)
						prefix = self.__iterate_prefix(call)
						self._logger.debug("obtain_prefix(): prefix: "+ str(prefix) + " (case /QRPP)")
					elif appendix == 'BCN': #filter all beacons
						call = re.sub('/BCN', '', call)
						prefix = self.__iterate_prefix(call)
						self.beacon = True
						self._logger.debug("obtain_prefix(): prefix: "+ str(prefix) + " (case /BCN)")
					elif appendix == "LH": #Filter all Lighthouses
						call = re.sub('/LH', '', call)
						prefix = self.__iterate_prefix(call)
						self._logger.debug("obtain_prefix(): prefix: "+ str(prefix) + " (case /LH)")
					else:
						prefix = self.__iterate_prefix(re.sub('/', '', appendix))   #check if the appendix is a valid country prefix
						self._logger.debug("obtain_prefix(): prefix: " + str(prefix) + " using appendix: " + appendix )
				
				elif re.search('/[A-Z0-9]$', call):  # case call/p or /b /m or /5 etc.
					appendix = re.search('/[A-Z0-9]$', call)
					appendix = re.sub('/', '', appendix.group(0))
					if appendix == 'B':			#special case Beacon
						call = re.sub('/B', '', call)
						prefix = self.__iterate_prefix(call)
						self.beacon = True
						self._logger.debug("obtain_prefix(): prefix: "+ str(prefix) + " (case /B)")
					elif re.search('\d$', appendix):
						area_nr = re.search('\d$', appendix).group(0)
						call = re.sub('/\d$', '', call)
						call = re.sub('[\d]+',area_nr, call)
						prefix = self.__iterate_prefix(call)
					else:
						prefix = self.__iterate_prefix(call)
						self._logger.debug("obtain_prefix(): appendix: " + appendix)
				
				elif re.match('^[\d]{0,1}[A-Z]{1,2}\d([A-Z]{1,4}|\d{3,3}|\d{1,3}[A-Z])[A-Z]{0,5}$', call, re.I):  # normal callsigns
					prefix = self.__iterate_prefix(call)
					self._logger.debug("obtain_prefix(): Prefix found: " + str(prefix) )
				
				else:
					if re.search('^[A-Z0-9]{1,4}/', entire_call):  # case xxxx/call
						pfx = re.search('^[A-Z0-9]{1,4}/', entire_call)
						pfx = re.sub('/', '', pfx.group(0))
						prefix = self.__iterate_prefix(pfx)
						self._logger.debug("obtain_prefix(): country prefix " + pfx)
					else:
						return(False)
						self._logger.debug("obtain_prefix(): returning False; Invalid callsign " + call )

				#--------identify Prefix of Callsign ------------

				if re.search('^[A-Z0-9]{1,4}/', entire_call):  # case xxxx/call
					if re.search('^[A-Z0-9]{4}/', entire_call) and len(entire_call) < 8:
						pass
					else:
						pfx = re.search('^[A-Z0-9]{1,4}/', entire_call)
						pfx = re.sub('/', '', pfx.group(0))
						prefix = self.__iterate_prefix(pfx)
						self._logger.debug("obtain_prefix(): country prefix " + pfx)
					
				if  prefix == '': #in 
					self._logger.debug("obtain_prefix(): return False; No Prefix found for " + call )
					return(False)

				return(prefix) #everything went well - return prefix
					
			else:
				return(False)
				self._logger.debug("obtain_prefix(): return False; No Prefix found for " + call )
		except Exception as e:
			self._logger.warning(str(e))
			self._logger.warning("obtain_prefix(): Exception with call:" +call )
			return(False)
			
	def lookup_cty_info(self, prefix):
		#--------Lookup Prefix in Country Database / File and the variables ------------	
		if prefix: 	# if Country information found, fill the variables
			try:
				info = {
				'latitude': Station.dxcc[prefix]['Latitude'],
				'longitude': Station.dxcc[prefix]['Longitude'],
				'cqz': Station.dxcc[prefix]['CQZone'],
				'ituz': Station.dxcc[prefix]['ITUZone'],
				'country': Station.dxcc[prefix]['Country'],
				'continent': Station.dxcc[prefix]['Continent'],
				'offset': Station.dxcc[prefix]['GMTOffset']
				}
				return(info)

			except KeyError as e: #catching remaining invalid prefixes like call/023 or call/1C0 
				self._logger.debug("LookUpCall() - Could not identify prefix of " + prefix + "; "+ str(e))
				self._logger.debug(call_info)
				return(False)

			except Exception as e:
				self._logger.debug("LookUpCall() exception"+ str(e))
				self._logger.debug(call_info)
				return(False)

		else: 	# busted call
			return(False)


class Spot(object):
	"""Split up a DXCluster line and return the individual fields"""
	def __init__(self, raw_spot):
		#super(Spot, self).__init__()
		self._logger = get_configured_logger(root_logger)
		self._logger.propagate = True #send all log events to higher logger which has a handler
		self.raw_spot = raw_spot
		self.valid = None
		self.dx_call = None
		self.spotter_call = None
		self.spotter_station = None
		self.frequency = None
		self.time = None
		self.comment = ""
		self.mode = None
		self.band = None
		self.locator = None
		if self.__process_spot(raw_spot):
			self.dx_station = Station(self.dx_call)
			self.spotter_station = Station(self.spotter_call)
			if self.dx_station.valid & self.spotter_station.valid:
				self.valid = True
			else:
				self.valid = False
		else: self.valid = False

	def convert_freq_to_band(self, freq):
		"""converts a frequency into the band and looks up the mode"""
		band = 0
		mode = "unknown"
		if ((freq >=135) and (freq <=138)): 
			band = 2190
			mode = "CW"
		elif ((freq >=1800) and (freq <=2000)): 
			band = 160
			if ((freq >=1800) and (freq <=1838)):
				mode = "CW"
			elif ((freq >1838) and (freq <=1840)):
				mode = "DIGITAL"
			elif ((freq >1840) and (freq <=2000)):
				mode = "LSB"
		elif ((freq >=3500) and (freq <=4000)): 
			band = 80
			if ((freq >=3500) and (freq <=3580)):
				mode = "CW"
			elif ((freq >3580) and (freq <=3600)):
				mode = "DIGITAL"
			elif ((freq >3600) and (freq <=4000)):
				mode = "LSB"
		elif ((freq >=5000) and (freq <=5500)): 
			band = 60
		elif ((freq >=7000) and (freq <=7300)): 
			band = 40
			if ((freq >=7000) and (freq <=7040)):
				mode = "CW"
			elif ((freq >7040) and (freq <=7050)):
				mode = "DIGITAL"
			elif ((freq >7050) and (freq <=7300)):
				mode = "LSB"
		elif ((freq >=10100) and (freq <=10150)): 
			band = 30
			if ((freq >=10100) and (freq <=10140)):
				mode = "CW"
			elif ((freq >10140) and (freq <=10150)):
				mode = "DIGITAL"
		elif ((freq >=14000) and (freq <=14350)): 
			band = 20
			if ((freq >=14000) and (freq <=14070)):
				mode = "CW"
			elif ((freq >14070) and (freq <=14099)):
				mode = "DIGITAL"
			elif ((freq >14100) and (freq <=14350)):
				mode = "USB"
		elif ((freq >=18068) and (freq <=18268)): 
			band = 17
			if ((freq >=18068) and (freq <=18095)):
				mode = "CW"
			elif ((freq >18095) and (freq <=18110)):
				mode = "DIGITAL"
			elif ((freq >18110) and (freq <=18268)):
				mode = "USB"
		elif ((freq >=21000) and (freq <=21450)): 
			band = 15
			if ((freq >=21000) and (freq <=21070)):
				mode = "CW"
			elif ((freq >21070) and (freq <=21150)):
				mode = "DIGITAL"
			elif ((freq >21150) and (freq <=21450)):
				mode = "USB"
		elif ((freq >=24890) and (freq <=24990)): 
			band = 12
			if ((freq >=24890) and (freq <=24915)):
				mode = "CW"
			elif ((freq >24915) and (freq <=24930)):
				mode = "DIGITAL"
			elif ((freq >24930) and (freq <=24990)):
				mode = "USB"
		elif ((freq >=28000) and (freq <=29700)): 
			band = 10
			if ((freq >=28000) and (freq <=28070)):
				mode = "CW"
			elif ((freq >28070) and (freq <=28190)):
				mode = "DIGITAL"
			elif ((freq >28300) and (freq <=29700)):
				mode = "USB"
		elif ((freq >=50000) and (freq <=54000)): 
			band = 6
			if ((freq >=50000) and (freq <=50100)):
				mode = "CW"
			elif ((freq >50100) and (freq <=50500)):
				mode = "USB"
			elif ((freq >50500) and (freq <=51000)):
				mode = "DIGITAL"
		elif ((freq >=70000) and (freq <=71000)): 
			band = 4
			mode = "unknown"
		elif ((freq >=144000) and (freq <=148000)): 
			band = 2
			if ((freq >=144000) and (freq <=144150)):
				mode = "CW"
			elif ((freq >144150) and (freq <=144400)):
				mode = "USB"
			elif ((freq >144400) and (freq <=148000)):
				mode = "unknown"
		elif ((freq >=220000) and (freq <=226000)): 
			band = 1.25 #1.25m
			mode = "unknown"
		elif ((freq >=420000) and (freq <=470000)): 
			band = 0.7 #70cm
			mode = "unknown"
		elif ((freq >=902000) and (freq <=928000)): 
			band = 0.33 #33cm US
			mode = "unknown"
		elif ((freq >=1200000) and (freq <=1300000)): 
			band = 0.23 #23cm
			mode = "unknown"
		elif ((freq >=2390000) and (freq <=2450000)): 
			band = 0.13 #13cm
			mode = "unknown"
		elif ((freq >=3300000) and (freq <=3500000)): 
			band = 0.09 #9cm
			mode = "unknown"
		elif ((freq >=5650000) and (freq <=5850000)): 
			band = 0.053 #5.3cm
			mode = "unknown"
		elif ((freq >=10000000) and (freq <=10500000)): 
			band = 0.03 #3cm
			mode = "unknown"
		elif ((freq >=24000000) and (freq <=24050000)): 
			band = 0.0125 #1,25cm
			mode = "unknown"
		elif ((freq >=47000000) and (freq <=47200000)): 
			band = 0.0063 #6,3mm
			mode = "unknown"
		else:
			band = 0
			mode = "unknown"
		return(band, mode)
		
	def __process_spot(self, raw_string):
		"""Chop Line from DX-Cluster into pieces and return a dict with the spot data"""
		try:
			spotter_call_temp = re.match('[A-Za-z0-9\/]+[:$]', raw_string[6:15])
			if spotter_call_temp:
				self.spotter_call = re.sub(':', '', spotter_call_temp.group(0))
			else:
				self._logger.debug("Missing Semicolon ?!")
				self.spotter_call = re.sub('[^A-Za-z0-9\/]+', '', raw_string[6:15])

			frequency_temp = re.search('[0-9\.]{5,12}', raw_string[10:25])
			if frequency_temp: 
				self.frequency = float(frequency_temp.group(0))
			else:
				self._logger.debug("RegEx for Frequency didn't work")
				self.frequency = float(re.sub('[^0-9\.]+', '', raw_string[16:25]))
				self._logger.error("__process_spot(): Frequency incorrect; "+frequency_temp)
				raise Exception("Could not decode frequency")

			self.dx_call = re.sub('[^A-Za-z0-9\/]+', '', raw_string[26:38])
			self.comment = re.sub('[^\sA-Za-z0-9\.,;\#\+\-!\?\$\(\)@\/]+', ' ', raw_string[39:69])
			time_temp = re.sub('[^0-9]+', '', raw_string[70:74])
			self.time = datetime.utcnow().replace(hour=int(time_temp[0:2]), minute=int(time_temp[2:4]), second=0, microsecond = 0, tzinfo=UTC)
			self.locator = re.sub('[^A-Za-z0-9]+', '', raw_string[75:80])
			self.band, self.mode = self.convert_freq_to_band(self.frequency)
			return(True)
		except Exception as e:
			self._logger.error(str(e)) 
			self._logger.exception("Problem in Spot Processing")
			return(False)
			

class WWV(object):
	
	#------------------Constructor --------------------
	def __init__(self, raw_wwv):
	#	super(Station, self).__init__()
		self._logger = get_configured_logger(root_logger)
		self._logger.propagate = True #send all log events to higher logger which has a handler
		self.station = None
		self.time = None
		self.a = None
		self.sfi = None
		self.k = None
		self.expk = None
		self.r = None
		self.aurora = False
		self.valid = False
		self.counter = 0
		if self.__process_wwv(raw_wwv):
			self.valid = True
		
	def __process_wwv(self, wwv):
		"""Chop Line from DX-Cluster into pieces and return WWV data"""
		try:
			if re.match('^WWV', wwv) or re.search('^WCY', wwv):
				if re.search('\s[\-A-Z0-9/]{3,10}\s', wwv[6:20], re.I):
					station =  re.search('\s[\-A-Z0-9/]{3,10}\s', wwv[6:20], re.I).group(0)
					station = station.lstrip().rstrip()
					station = Station(station)
					if station:
						self.station = station
					else:
						raise Exception("Callsign wrong")
						
				if re.search('<[\d]{2}>', wwv):
					time_temp = re.search('<[\d]{2}>', wwv).group(0)
					time_temp = re.search('[\d]{2}', time_temp).group(0)
					time_temp = int(time_temp)
					self.time = datetime.utcnow().replace(hour=time_temp, minute=0, second=0, microsecond=0, tzinfo=UTC)

				if re.search('A=\d{1,3}', wwv):
					temp = re.search('A=\d{1,3}', wwv).group(0)
					temp = re.sub('A=', '', temp)
					self.a = int(temp)
				else:
					raise Exception("could not decode A")
					
				if re.search('SFI=\d{1,3}', wwv):
					temp = re.search('SFI=\d{1,3}', wwv).group(0)
					temp = re.sub('SFI=', '', temp)
					self.sfi = int(temp)
				else:
					raise Exception("could not decode SFI")
					
				if re.search('\sK=\d{1,3}', wwv):
					temp = re.search('\sK=\d{1,3}', wwv).group(0)
					temp = re.sub('\sK=', '', temp)
					self.k = int(temp)
				else:
					raise Exception("could not decode K")

				if re.search('expK=\d{1,3}', wwv):
					temp = re.search('expK=\d{1,3}', wwv).group(0)
					temp = re.sub('expK=', '', temp)
					self.expk = int(temp)
					
				if re.search('R=\d{1,3}', wwv):
					temp = re.search('R=\d{1,3}', wwv).group(0)
					temp = re.sub('R=', '', temp)
					self.r = int(temp)
					
				if re.search('Au=\S{2,3}', wwv):
					temp = re.search('Au=\S{2,3}', wwv).group(0)
					temp = re.sub('Au=', '', temp)
					if temp == "no":
						self.aurora = False
					elif temp == "yes":
						self.aurora = True
				
				self._logger.info("Stored WWV successfully")
				self._logger.info(self.station.call + " " + self.time.strftime("%d.%m.%Y %H:%M:%S") + " A:" + str(self.a) + " SFI:" + str(self.sfi) + " K:" + str(self.k) + " expK:" + str(self.expk) + " R:" + str(self.r) + " Aurora:" + str(self.aurora))
				return(True)
			else:
				raise Exception("missing starting letters 'WWV'")
		except Exception as e:
			self._logger.error(str(e)) 
			self._logger.error("Problem in WWV Processing")
			return(False)



class Comment(object):
	#------------------Constructor --------------------
	def __init__(self, raw_comment):
	#	super(Station, self).__init__()
		self._logger = get_configured_logger(root_logger)
		self._logger.propagate = True #send all log events to higher logger which has a handler

		self.station = None
		self.time = None
		self.text = None
		self.valid = False
		if self.__process_comment(raw_comment):
			self.valid = True
	
	def __process_comment(self, comment):
		"""Chop Line from DX-Cluster into pieces and return Comment data"""
		try:
			if re.match('^To ALL de', comment, re.I):
				if re.search('de [\-A-Z0-9/]{4,15}', comment[6:20], re.I):
					station = re.search('de [\-A-Z0-9/]{4,15}', comment[6:20], re.I).group(0)
					station = re.sub('de ','', station)
					station = station.upper()
					self.station = Station(station)
					if not self.station.valid:
						raise Exception("Callsign invalid")
				else:
					raise Exception("Callsign invalid")

				self.time = datetime.utcnow().replace(tzinfo = UTC)
				self.text = "hi"
				if re.search(':[\S\s]+', comment):
					text = re.search(':[\S\s]+', comment).group(0)
					text = re.sub(': ', '', text)
					text = re.sub('[^A-Za-z0-9\.,@&\?;\-\#\+!\$\(\)\/]+', ' ', text) #sanitize input
					text = text.rstrip() #chop off tailing whitespaces
					self.text = text
				else:
					raise Exception("Comment text not processible; Missing semicolon?")
				
				self._logger.debug("Comment successfully processed")
				self._logger.debug(self.station.call + " " + self.time.strftime("%d.%m.%Y %H:%M:%S") + " " + self.text)
				return(True)
				
			else:
				raise Exception("missing starting letters 'TO ALL'")
		
		except Exception as e:
			self._logger.error(str(e))
			self._logger.error("Problem in Comment Processing")
			return(False)