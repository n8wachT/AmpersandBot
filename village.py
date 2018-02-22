# -*- coding: utf-8  -*-
########################
## AmpersandBot  code ##
##   by T. H. Kelly   ##
## aka  PinkAmpersand ##
########################

import pywikibot
import requests
import urllib.request
from urllib.request import urlopen
import json
import unidecode
from unidecode import unidecode
import sys
import re

max = 50
total = 0
	
def log(a,b,c):
	with open("C:\\Users\\Tom\\Desktop\\python\\AmpersandBot\\VillageBot\\" + a + ".txt", "a") as file:
		file.write("[[" + b + "]]" + c + "\n")
	
# the function at the script's core
	
def village():
	# parse layers of JSON to get to the links themselves
	query = API_JSON.get("query")
	backlinks = query.get("backlinks")
	# the loop that does the actual heavy lifting
	for link in backlinks:
		title = link["title"]
		site = pywikibot.Site("wikidata", "wikidata")
		repo = site.data_repository()
		item = pywikibot.ItemPage(repo, title)
		ic = item.get()["claims"]
		id = item.get()["descriptions"]
		il = item.get()["labels"]
		if "P31" in ic:
			try:
				p31val = str(ic["P31"][0].getTarget()) # get value of "instance of"
			except (KeyError): # in case no P31
				log("noP31",title,"")
				print("no P31 value: " + title)
			if p31val == "[[wikidata:Q532]]": # is it a village?
				if id.get("en"): # is there an English-language description?
					if re.match("^village *(in|of)* *(Antigua (&|and) Barbuda|Bosnia (& |and )?Herzegovina|Central African Republic|(the|la )République centrafricaine|Republic of (the )?Congo|Democratic Republic of (the )?Congo|Costa Rica|(the )?Czech Republic|(the )?Dominican Republic|East Timor|Timor Leste|El Salvador|Equatorial Guinea|Guinea Bissau|Ivory Coast|C[oô]te d'?Ivoire|(the )?Republic of Ireland|North Korea|South Korea|(the )?Marshall Islands|Papua New Guinea|(Former Yugoslav )?Republic of Macedonia|(the )?Russian Federation|(St\.?|Saint) Kitts( (&|and) Nevis)?|(St\.?|Saint) Lucia|(St\.?|Saint) Vincent ((and|&) the Grenadines)?|San Marino|S[aã]o Tom[eé]( (and|&) Pr[ií]ncipe)?|Saudi Arabia|Sierra Leone|Solomon Islands|South Africa|South Sudan|Sri Lanka|Trinidad (and|&)Tobago|United Arab Emirates|United Kingdom|United States( of America)?|Vatican( City)?|[a-z])*$",id.get("en"),re.I): # is the description basic?
						describeItem(item,ic,il,title)
					else:
						print(title + " already properly described") # marker in cmd line for no description update
				else:
					describeItem(item,ic,il,title)
			else:
				log("P31errors",title,"")
				print("P31 error (not a village): " + title)

def describeItem(item,ic,il,title):
	def describeAs(a): # function for setting descriptions
		global total
		if total < max:
			total += 1
			try:
				item.editDescriptions(descriptions={'en': a}, summary=(u'([[WD:Requests_for_permissions/Bot/AmpersandBot_2|TRIAL RUN]]: block if malfunctioning) Added English description "' + a + '", using P31 and P131 values'))
				log("updates",title,"description") # for consultation after run
				print("updated " + title + " description (#" + str(total) + ")") # marker in cmd line for updated items	
			except pywikibot.exceptions.OtherPageSaveError:
				log("dupeErrors",title,"")
				print("dupeError: " + title)
		else:
			sys.exit("max number of edits reached")
	if "P131" in ic: # does the item have a parent entity listed?
		parent = ic["P131"][0].getTarget() # the parent entity
		parent_c = parent.get()["claims"]
		parent_P31 = parent_c["P31"]
		if "en" in parent.get()["labels"]: # does the parent entity have an English label?
			parent_label = parent.get()["labels"]["en"] # the English label of the parent entity
			global described
			described = "no"
			for value in parent_P31:
				if str(value.getTarget()) == "[[wikidata:Q3624078]]":
					describeAs("village in " + parent_label)
					described = "yes"
			if not described == "yes" and "P131" in parent_c: # does *that* entity have a parent entity listed?
				gparent = parent_c["P131"][0].getTarget() # the grandparent entity
				gparent_c = gparent.get()["claims"]
				gparent_P31 = gparent_c["P31"]
				if "en" in gparent.get()["labels"]: # does the grandparent entity have an English label?
					gparent_label = gparent.get()["labels"]["en"]
					for value in gparent_P31:
						if str(value.getTarget()) == "[[wikidata:Q3624078]]":
							describeAs("village in " + parent_label + ", " + gparent_label)
							described = "yes"
					if not described == "yes" and "P131" in gparent_c:
						g2parent = gparent_c["P131"][0].getTarget() # the great-grandparent entity
						g2parent_c = g2parent.get()["claims"]
						g2parent_P31 = g2parent_c["P31"]
						if "en" in g2parent.get()["labels"]:
							g2parent_label = g2parent.get()["labels"]["en"]
							for value in g2parent_P31:
								if str(value.getTarget()) == "[[wikidata:Q3624078]]":
									describeAs("village in " + parent_label + ", " + gparent_label + ", " + g2parent_label)
									described = "yes"
							if not described == "yes" and "P131" in g2parent_c: 
								g3parent = g2parent_c["P131"][0].getTarget() # the great-great-grandparent entity
								g3parent_c = g3parent.get()["claims"]
								g3parent_P31 = g3parent_c["P31"]
								if "en" in g3parent.get()["labels"]:
									g3parent_label = g3parent.get()["labels"]["en"]
									for value in g3parent_P31:
										if str(value.getTarget()) == "[[wikidata:Q3624078]]":
											describeAs("village in " + gparent_label + ", " + g2parent_label + ", " + g3parent_label)
											described = "yes"
									if not described == "yes":
										log("moreThan4Levels",title,"")
										print("Country >4 levels deep: " + title)
								else:
									log("noEnglish", title, "great-great-grandparent entity")
									print("No English label for " + title + "'s great-great-grandparent entity")
							else:
								log("endsEarly",title,"ends at great-grandparent entity")
								print("No country reachable from great-grandparent entity: " + title)
						else:
							log("noEnglish", title, "great-grandparent entity")
							print("No English label for " + title + "'s great-grandparent entity")
					else:
						log("endsEarly",title,"ends at grandparent entity")
						print("No country reachable from grandparent entity: " + title)
				else:
					log("noEnglish", title, "grandparent entity")
					print("No English label for " + title + "'s grandparent entity")
			else:
				log("endsEarly",title,"ends at parent entity")
				print("No country reachable from " + title + "'s parent entity")
		else:
			log("noEnglish",title,"parent entity")
			print("No English label for " + title + "'s parent entity")
	else:
		log("noP131",title,"")
		print("No parent entity: " + title)

# The framework of the script

blcont = "&"
while blcont:
	API = urlopen(u"https://www.wikidata.org/w/api.php?action=query&list=backlinks&bltitle=Q532&bllimit=5000&indexpageids=&blnamespace=0&format=json" + blcont).read()
	API_decode = API.decode(encoding="utf-8", errors="strict")
	API_JSON = json.loads(API_decode)

	if API_JSON:
		if "query" in API_JSON: 
			print ("query success")
			village() # actually execute the whole damn thing
		# load next batch of JSON results if extant	
		if "continue" in API_JSON:
			cont = API_JSON.get("continue")
			if cont["continue"] == "-||":
				blcont = "&continue=-||&blcontinue=" + cont["blcontinue"]
				print("loading next page of API")
			else:
				sys.exit("API completely processed")
		else:
			sys.exit("API completely processed")
