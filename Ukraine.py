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

max = 15000
total = 0
	
def log(a,b,c):
	with open("C:\\Users\\Tom\\Desktop\\python\\AmpersandBot\\" + a + ".txt", "a") as file:
		file.write("[[" + b + "]] " + c + " \n")
	
# the function at the script's core
	
def Ukraine():
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
		# various steps to weed through the ones we don't want and pick out the ones we do:
		if "P31" in ic:
			p31val = str(ic["P31"][0].getTarget()) # get value of "instance of"
			p17val = str(ic["P17"][0].getTarget()) # "   "     "  "country"
			if p31val == "[[wikidata:Q21672098]]" and p17val == "[[wikidata:Q212]]": # is it an administrative entity, and is it in Ukraine?
				if id.get("en"): # is there an English-language description?
					badDescs = ("Ukrainian village","village in Ukraine","village of Ukraine","administrative territorial entity of Ukraine")
					if id.get("en") in badDescs: # is the description basic?
						defineItem(item,ic,il,title)
					else:
						print(title + " already properly described") # marker in cmd line for no description update
				else:
				 defineItem(item,ic,il,title)
				
			else:
				log("P17errors",title,"")
				print("P17error: " + title)
		if not "en" in il and "uk" in il: # is there a Ukrainian label, but not an English one?
			labelItem(item,il,title)
		else:
			print(title + " already properly labeled") # marker in cmd line for no label update

def defineItem(item,ic,il,title):
	def defineAs(a): # function for setting descriptions
		item.editDescriptions(descriptions={'en': a}, summary=(u'added [en] description "' + a + '", using P17, P31, and P131 values'))
	if "P131" in ic: # does the item have a parent entity listed?
		p131val = ic["P131"][0].getTarget() # the parent entity
		if "en" in p131val.get()["labels"]: # does the entity have an English label?
			p131label = p131val.get()["labels"]["en"] # the English label of the parent entity
			level2c = p131val.claims # claims taken from the parent entity
			if "P131" in level2c: # does *that* entity have a parent entity listed?
				level2val = level2c["P131"][0].getTarget() # the grandparent entity
				level3c = level2val.get()["claims"] # claims taken from the grandparent entity (doing it the other way doesn't work, for w/e reason)
				if str(level3c["P31"][0].getTarget()) == "[[wikidata:Q3348196]]": # is the grandparent entity an oblast of Ukraine
					if "en" in level2val.get()["labels"]: # and does it have an English label?
						level2label = level2val.get()["labels"]["en"]
						global total
						if total < max:
							total += 1
							try:
								defineAs("village in " + p131label + ", " + level2label + ", Ukraine")
								log("updates",title,"description") # for consultation after run
								print("updated " + title + " description (#" + str(total) + ")") # marker in cmd line for updated items	
							except pywikibot.exceptions.OtherPageSaveError:
								log("dupeErrors",title,"")
								print("dupeError: " + title)
						else:
							sys.exit("total reached: " + str(max))
					else:
						log("lvl2noEn",title,"")
						print("lvl2noEn: " + title)
				else:
					log("notOblast",title,"")
					print ("notOblast: " + title)
			else:
				log("nolvl2",title,"")
				print("nolvl2: " + title)
		else:
			log("p131noEn",title,"")
			print("p131noEn: " + title)
	else:
		log("noP131",title,"")
		print("noP131: " + title)
def labelItem(item,il,title):
	def labelAs(a): # function for setting labels
		item.editLabels(labels={'en': a}, summary=(u'set [en] label to "' + a + '" based on automated romanization of Ukrainian label'))
	try:
		ukval = il["uk"]
		ukroman = unidecode(ukval)
		ukroman_fixed = ukroman.replace("'","") # rm 's because Ukrainian Nat'l Syst. doesn't use them anymore
		global total
		if total < max:
			total += 1
			labelAs(ukroman_fixed)
			log("updates",title,"label")
			print("updated " + title + " label (#" + str(total) + ")")
		else:
			sys.exit("total reached: " + str(max))
	except pywikibot.exceptions.OtherPageSaveError:
		log("dupeErrors",title,"")
		print("dupeError: " + title)

# The framework of the script

# get JSON from API and make usable
# TODO: move to predefined function, if it's not too hard.
# would be useful for adapting script to other tasks
blcont = "&"
while blcont:
	API = urlopen(u"https://www.wikidata.org/w/api.php?action=query&list=backlinks&bltitle=Q21672098&bllimit=5000&indexpageids=&format=json" + blcont).read()
	API_decode = API.decode(encoding="utf-8", errors="strict")
	API_JSON = json.loads(API_decode)

	if API_JSON:
		if "query" in API_JSON: 
			print ("query success")
			Ukraine() # actually execute the whole damn thing
		# load next batch of JSON results if extant	
		if "continue" in API_JSON:
			cont = API_JSON.get("continue")
			if cont["continue"] == "-||":
				blcont = "&continue=-||&blcontinue=" + cont["blcontinue"]
				print("loading next page of API")
			else:
				sys.exit("API completely processed")
