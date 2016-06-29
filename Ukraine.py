# -*- coding: utf-8  -*-
########################
## AmpersandBot  code ##
##   by T. H. Kelly   ##
## aka  PinkAmpersand ##
########################

################################################################
# A few things have  been  tweaked  since  the test run, so if #
# there's any glaring mistakes  in here, it's probably because #
# I haven't had the chance to test things out since then. Some #
# of the possible  mistakes   wouldn't   come  up  until a few #
# hundred edits into a run,  so  I'll  have to wait to get the #
# bot    flag    to     find     out     if     they    exist. #
################################################################

import pywikibot
import urllib.request
from urllib.request import urlopen
import json

total = 0
blcont = "start"
	
# following part possibly still buggy. only thing that didn't 
# work in test run. has been modified since, in a way that 
# hopefully will work. not super important, but would like to fix.
	
def log(a):
	file = open("log.txt", "w")
	file.write(a+" updated \n")
	file.close() 
	
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
		def defineAs(a): # function for setting descriptions
			item.editDescriptions(descriptions={'en': a}, summary=(u'added [en] description "' + a + '", using P17, P31, and P131 values')))
		# various steps to weed through the ones we don't want and pick out the ones we do
		if ic:
			if "P31" in ic:
				p31val = str(ic['P31'][0].getTarget())
				p17val = str(ic["P17"][0].getTarget())
				# yes, in theory this skips items with desired P31 but no P17 at all.
				# but something's probably amiss with any item like that, so probably
				# best to avoid it.
				# TODO: throw in logging system for such items; could be interesting 
				# cases to check out manually
				if p31val == "[[wikidata:Q21672098]]" and p17val == "[[wikidata:Q212]]":
					if not "en" in id:
						if "P131" in ic:
							p131val = ic["P131"][0].getTarget()
							p131label = p131val.get()["labels"]["en"]
							level2c = p131val.claims
							if "P131" in level2c:
								level2val = level2c["P131"][0].getTarget()
								level2label = level2val.get()["labels"]["en"]
								defineAs("village in " + p131label + ", " + level2label + ", Ukraine")
								log(title) # for consultation after a run
								print("updated " + title) # marker in cmd line for updated items
							else:
								defineAs("village in " + p131label + ", Ukraine")
								log(title)
								print("updated " + title)
						else:
							defineAs("Ukrainian village")
							log(title)
							print("updated " + title)					
						total += 1
				else:
					print(title + " already described") # marker in cmd line for non-updated items
					
# The framework of the script
while blcont and total <= 100: # stops script when a desired number of edits have been performed, or when there are no more to be made
	if blcont == "start":
		cont_param = ""
	else:
		cont_param = "&continue=-||&blcontinue=" + blcont
	# get JSON from API and make useable
	# TODO: move to predefined function, if it's not too hard.
	# would be useful for adapting script to other tasks
	API = urlopen(u"https://www.wikidata.org/w/api.php?action=query&list=backlinks&bltitle=Q21672098&bllimit=500&indexpageids=&format=json" + cont_param).read()
	API_decode = API.decode(encoding="utf-8", errors="strict")
	API_JSON = json.loads(API_decode)
	
	if API_JSON: # marker in cmd line for new batches of JSON from API
		print("API_JSON found")
		if "query" in API_JSON: 
			Ukraine() # actually execute the whole damn thing
		# load next batch of JSON results if extant	
		if "continue" in API_JSON:
			cont = API_JSON.get("continue")
			if cont["continue"] == "-||":
				blcont = cont["blcontinue"]
		else:
			blcont = "" # stop once all of the JSON from the API has been processed