#!/usr/bin/python
# Filename: cty.py

def load_cty(filename):
	""" Load Country Information from plist file (http://www.country-files.com/cty/history.htm)"""
	try:
		import plistlib
		country_list = plistlib.readPlist(filename)
		return(country_list)
	except:
		return(False)

# End of cty.py
