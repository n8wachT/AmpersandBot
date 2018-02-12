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

max = 10
total = 0
	
# following part possibly still buggy. only thing that didn't 
# work in test run. has been modified since, in a way that 
# hopefully will work. not super important, but would like to fix.
	
def log(a,b,c):
	with open("C:\\Users\\Tom\\Desktop\\python\\AmpersandBot\\" + a + ".txt", "a") as file:
		file.write(b + " " + c + " \n")
	
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
		# various steps to weed through the ones we don't want and pick out the ones we do
		if ic:
			if "P31" in ic:
				p31val = str(ic["P31"][0].getTarget())
				p17val = str(ic["P17"][0].getTarget())
				if p31val == "[[wikidata:Q21672098]]":
					if p17val == "[[wikidata:Q212]]":
						if id.get("en"):
							badDescs = ("Ukrainian village","village in Ukraine","village of Ukraine","administrative territorial entity of Ukraine")
							if id.get("en") in badDescs:
								updateItem(item,ic,il,title)
							else:
								print(title + " already properly described and labeled") # marker in cmd line for non-updated items
						else:
						 updateItem(item,ic,il,title)
						
					else:
						log("P17errors",title,"")
						print("P17error: " + title)

def updateItem(item,ic,il,title):
	def defineAs(a): # function for setting descriptions
		item.editDescriptions(descriptions={'en': a}, summary=(u'added [en] description "' + a + '", using P17, P31, and P131 values'))
	def labelAs(a): # function for setting labels
		item.editLabels(labels={'en': a}, summary=(u'set [en] label to "' + a + '" based on automated romanization of Ukrainian label'))
	if "P131" in ic:
		p131val = ic["P131"][0].getTarget()
		if "en" in p131val.get()["labels"]:
			p131label = p131val.get()["labels"]["en"]
			level2c = p131val.claims
			if "P131" in level2c:
				level2val = level2c["P131"][0].getTarget()
				if "en" in level2val.get()["labels"]:
					level2label = level2val.get()["labels"]["en"]
					if total < max:
						global total
						total += 1
						defineAs("village in " + p131label + ", " + level2label + ", Ukraine")
						log("updates",title,"description") # for consultation after run
						print("updated " + title + " description (#" + str(total) + ")") # marker in cmd line for updated items
					else:
						sys.exit("total reached: " + str(max))
				else:
					log("lvl2noEn",title,"")
					print("lvl2noEn: " + title)
			else:
				log("nolvl2",title,"")
				print("nolvl2: " + title)
		else:
			log("p131noEn",title,"")
			print("p131noEn: " + title)
	else:
		log("noP131",title,"")
		print("noP131: " + title)
	if not "en" in il and "uk" in il:
		try:
			ukval = il["uk"]
			ukroman = unidecode(ukval)
			if total < max:
				global total
				total += 1
				labelAs(ukroman)
				log("updates",title,"label")
				print("updated " + title + " label (#" + str(total) + ")")
			else:
				sys.exit("total reached: " + str(max))
		except pywikibot.data.api.APIError:
			log("dupeErrors",title,"")
			print("dupeError: " + title)

# The framework of the script

# get JSON from API and make usable
# TODO: move to predefined function, if it's not too hard.
# would be useful for adapting script to other tasks
blcont = "&"
while blcont:
	token = urlopen(u"https://www.wikidata.org/w/api.php?action=query&meta=tokens&format=json&type=login")
	token_read = token.read()
	token_str = str(token_read)
	token_replace = token_str.replace("'",'"')
	token_sr = token_replace.strip('b"').replace('}"','}')
	token_j = json.loads(token_sr)
	token_j2 = token_j["query"]["tokens"]["logintoken"]
	login_url = u"https://www.wikidata.org/w/api.php?&action=clientlogin&username=AmpersandBot&password=hunter2&assert=bot&loginreturnurl=http://tomkel.ly&logintoken="
	def login():
		urlopen(login_url + token_j2)
	login()
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
