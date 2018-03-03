# -*- coding: utf-8  -*-
########################
## AmpersandBot  code ##
##   VillageBot  v2   ##
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
import itertools
import datetime

max = 70
total = 0
	
def log(a,b,c):
	with open("C:\\Users\\Tom\\Desktop\\python\\AmpersandBot\\VillageBot\\" + a + ".txt", mode="a") as file:
		file.write("[[" + b + "]]" + c + "\n")
	
# the function at the script's core:
	
def village():
	# parse layers of JSON to get to the links themselves
	query = API_JSON.get("query")
	backlinks = query.get("backlinks")
	# the loop that does the actual heavy lifting
	for link in backlinks:
		title = link["title"]
		site = pywikibot.Site("wikidata", "wikidata")
		repo = site.data_repository()
		page = pywikibot.Page(repo,title)
		item = pywikibot.ItemPage(repo, title)
		item.get()
		ic = item.claims
		id = item.descriptions
		il = item.labels
		ia = item.aliases
		if "P31" in ic:
			try:
				p31val = str(ic["P31"][0].getTarget()) # get value of "instance of"
			except (KeyError): # in case no P31
				log("noP31",title,"")
				print("no P31 value: " + title)
			if p31val == "[[wikidata:Q532]]": # is it a village?
				labelItem(page,title,item,il,ia)
				if id.get("en"): # is there an English-language description?
					if re.match("^village *(in|of)* *(Antigua (&|and) Barbuda|The Bahamas|Bosnia (& |and )?Herzegovina|(Cape|Cabo) Verde|Central African Republic|(the |la )?République centrafricaine|(the )?Republic of (the )?Congo|(the )?Democratic Republic of (the )?Congo|Costa Rica|(the )?Czech Republic|(the )?Dominican Republic|East Timor|Timor Leste|El Salvador|Equatorial Guinea|The Gambia|Guinea Bissau|Ivory Coast|C[oô]te d'?Ivoire|(Former Yugoslav )?Republic of Macedonia|(the )?Republic of Ireland|North Korea|South Korea|(the )?Marshall Islands|The Netherlands|New Zealand|Papua New Guinea|The Philippines|(the )?Russian Federation|(St\.?|Saint) Kitts( (&|and) Nevis)?|(St\.?|Saint) Lucia|(St\.?|Saint) Vincent ((and|&) the Grenadines)?|San Marino|S[aã]o Tom[eé]( (and|&) Pr[ií]ncipe)?|Saudi Arabia|Sierra Leone|(the )?Solomon Islands|South Africa|South Sudan|Sri Lanka|Trinidad (and|&) Tobago|(the )?United Arab Emirates|(the )?United Kingdom|(the )?United States( of America)?|(the )?Vatican( City)?|[a-z])*$",id.get("en"),re.I): # is the description basic?
						describeItem(item,ic,il,title)
					else:
						print(title + " description not changed") # marker in cmd line for no description update
				else:
					describeItem(item,ic,il,title)
			else:
				log("P31errors",title,"")
				print("P31 error (not a village): " + title)
				
def describeItem(item,ic,il,title):
	def describeAs(a,b): # function for setting descriptions
		global total
		if total < max:
			try:
				total += 1
				item.editDescriptions(descriptions={'en': a}, summary=(u'([[WD:Requests_for_permissions/Bot/AmpersandBot_2|TRIAL RUN]]: block if malfunctioning) Added English description "' + a + '", using P31 and P131 values'))
				log("updates",title,"description") # for consultation after run
				print("updated " + title + " description " + b + ": " + a + "(#" + str(total) + ")") # marker in cmd line for updated items	
				global described
				described = "yes"
			except pywikibot.exceptions.OtherPageSaveError:
				log("APIErrors",title,"while describing")
				print("APIError: " + title)
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
					describeAs("village in " + parent_label,"at parent level")
			if described == "no":
				if "P131" in parent_c: # does *that* entity have a parent entity listed?
					gparent = parent_c["P131"][0].getTarget() # the grandparent entity
					gparent_c = gparent.get()["claims"]
					gparent_P31 = gparent_c["P31"]
					if "en" in gparent.get()["labels"]: # does the grandparent entity have an English label?
						gparent_label = gparent.get()["labels"]["en"]
						for value in gparent_P31:
							if str(value.getTarget()) == "[[wikidata:Q3624078]]":
								if parent_label in gparent_label or gparent_label in parent_label:
									log("wordMatch",title,"at grandparent level")
									print("Entities share strings at grandparent level: " + title)
									described = "skipped"
								else:
									describeAs("village in " + parent_label + ", " + gparent_label,"at grandparent level")
						if described == "no":
							if "P131" in gparent_c:
								g2parent = gparent_c["P131"][0].getTarget() # the great-grandparent entity
								g2parent_c = g2parent.get()["claims"]
								g2parent_P31 = g2parent_c["P31"]
								if "en" in g2parent.get()["labels"]:
									g2parent_label = g2parent.get()["labels"]["en"]
									for value in g2parent_P31:
										if str(value.getTarget()) == "[[wikidata:Q3624078]]":
											if parent_label in gparent_label or parent_label in g2parent_label or gparent_label in parent_label or gparent_label in g2parent_label or g2parent_label in parent_label or g2parent_label in gparent_label:
												log("wordMatch",title,"at great-grandparent level")
												print("Entities share strings at great-grandparent level: " + title)
												described = "skipped"
											else:
												describeAs("village in " + parent_label + ", " + gparent_label + ", " + g2parent_label,"at grandparent level")
									if described == "no":
										if "P131" in g2parent_c:
											g3parent = g2parent_c["P131"][0].getTarget() # the great-great-grandparent entity
											g3parent_c = g3parent.get()["claims"]
											g3parent_P31 = g3parent_c["P31"]
											if "en" in g3parent.get()["labels"]:
												g3parent_label = g3parent.get()["labels"]["en"]
												for value in g3parent_P31:
													if str(value.getTarget()) == "[[wikidata:Q3624078]]":
														if gparent_label in g2parent_label or gparent_label in g3parent_label or g2parent_label in gparent_label or g2parent_label in g3parent_label or g3parent_label in gparent_label or g3parent_label in g2parent_label:
															log("wordMatch",title,"at great-great-grandparent level")
															print("Entities share strings at great-great-grandparent level: " + title)
															described = "skipped"
														else:
															describeAs("village in " + gparent_label + ", " + g2parent_label + ", " + g3parent_label,"at great-great-grandparent level")
												if described == "no":
													if "P131" in g3parent_c:
														g4parent = g3parent_c["P131"][0].getTarget() # the great-great-grandparent entity
														g4parent_c = g4parent.get()["claims"]
														g4parent_P31 = g4parent_c["P31"]
														if "en" in g4parent.get()["labels"]:
															g4parent_label = g4parent.get()["labels"]["en"]
															for value in g4parent_P31:
																if str(value.getTarget()) == "[[wikidata:Q3624078]]":
																	if g2parent_label in g3parent_label or g2parent_label in g4parent_label or g3parent_label in g2parent_label or g3parent_label in g4parent_label or g4parent_label in g2parent_label or g4parent_label in g3parent_label:
																		log("wordMatch",title,"at thrice-great-grandparent level")
																		print("Entities share strings at thrice-great-grandparent level: " + title)
																		described = "skipped"
																	else:
																		describeAs("village in " + g2parent_label + ", " + g3parent_label + ", " + g4parent_label,"at thrice-great-grandparent level")
															if described == "no":
																log("moreThan5Levels",title,"")
																print("Country >5 levels deep: " + title)
														else:
															log("noEnglish",title,"thrice-great-grandparent entity")
															print("No English label for " + title + "'s thrice-great-grandparent entity")
													else:
														log("endsEarly",title,"ends at thrice-great-grandparent entity")
														print("No county reachable from thrice-great-grandparent entity: " + title)
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
		
def labelItem(page,title,item,il,ia):
	def setData(a,b,c,d):
		global total
		if total < max:
			old_ec = page.revision_count()
			item.editEntity(a,summary=b)
			page.purge()
			new_ec = page.revision_count()
			if not new_ec == old_ec:
				total += 1
				if c == "dab":
					print("Updated " + title + " labels and aliases (dab): " + d + " (#" + str(total) + ")")
					log("updates",title,"labels and aliases (dab)")
				elif c == "unanimity":
					log("updates",title,"labels and aliases (unanimity)")
					print("Updated " + title + " labels and aliases (unanimity): " + d + " (#" + str(total) + ")")
			else:
				if c == "dab":
					print(title + " labels and aliases not changed (dab)")
				elif c == "unanimity":
					print(title + " labels and aliases not changed (unanimity)")
		else:
			sys.exit("max number of edits reached")
	try:
		lda1 = '{"labels": {'
		lda2 = '"aliases": {'
		for lang in il:
			if re.search(",| \(", il[lang]):
				ilr = re.sub("(,| \().*","",il[lang])
				lda1 = lda1 + '"' + lang + '": "' + ilr + '", '
				lda2 = lda2 + '"' + lang + '": ["' + il[lang] + '", "' + unidecode(il[lang]) + '"], '
		lda3 = lda1.rstrip(", ") + "}, " # create dict of lang values and labels
		lda4 = lda2.rstrip(", ") + "}}" 
		lda5 = lda3 + lda4
		setData(json.loads(lda5),u"([[WD:Requests_for_permissions/Bot/AmpersandBot_2|TRIAL RUN]]: block if malfunctioning) Removed disambiguation from labels & set old labels as aliases","dab",lda3)
		latlangs = ("en","to","tet","tum","tn","tpi","wa","wo","war","yo","ts","st","io","bi","kbp","prg","kri","ie","kab","gn","ia","jam","hil","kr","lij","pam","lad","ltg","ln","mh","jbo","ku","mi","pih","olo","nov","tw","vo","ang","din","ha","atj","pdc","pfl","nb","nn","fo","kw","kl","nds","stq","fy","ik","ace","aa","ak","frr","rup","ast","bar","ext","ee","szl","ksh","ve","vec","vep","vro","eo","fr","de","vot","cho","ceb","co","bjn","map-bms","bm","ch","chy","ny","cbk-zam","fj","hz","fur","ff","gag","ht","kaa","rw","ig","rn","ki","ho","csb","liv","kg","krj","arn","lmo","nap","pap","om","pag","nso","se","sg","sat","scn","sc","srn","jv","sn","sm","ss","tl","li","gsw","sgs","pcd","nds-nl","mus","eml","de-at","vmf","zea","aln","lfn","roa-tara","su","tay","jut","pdt","gor","sr-el","simple","crh-latn","tt-latn","is","la","fi","ay","qu","ca","nl","sw","frc","gcr","ro","mg","en-ca","en-gb","eu","cs","sv","da","id","sq","lb","sk","sl","et","lv","lt","ga","mt","an","ms","tk","az","gl","cy","gd","zu","br","gv","rm","rmy","xh","za","hsb","so","dsb","sma","nah","na","nv","oc","af","sco","frp","pms","nrm","mwl","min","ruq") # list of all WD-supported langs using Latin script
		il_list = []
		for lang in latlangs:
			if lang in il:
				il_list.append(il[lang])
		split = "no"
		if len(il_list) > 1:
			try:
				a = 1
				while a:
					if il_list[0] == il_list[a]:
						a += 1
					else:
						split = "yes"
						break
			except IndexError:
				pass
		if split == "no":
			newLabel = il_list[0]
			ldb1 = '{"labels": {'
			for lang in latlangs:
				if not lang in il:
					ldb1 = ldb1 + '"' + lang + '": "' + newLabel + '", '
			ldb2 = ldb1.rstrip(", ") + "}"
			if not unidecode(newLabel) == newLabel:
				ias = str(ia).strip("{").rstrip("}").replace("'",'"') # old aliases so they don't get deleted
				ldb3 = ldb2 + ', " aliases' + '": {' + ias + ", " # another dict, but this time add aliases too
				for lang in latlangs:
					ldb3 = ldb3 + '"' + lang + '": ["' + unidecode(newLabel) + '"], '
				ldb4 = ldb3.rstrip(", ") + "}}"
			else:
				ldb4 = ldb2 + "}"
			setData(json.loads(ldb4),u"([[WD:Requests_for_permissions/Bot/AmpersandBot_2|TRIAL RUN]]: block if malfunctioning) Set all Latin-script languages' labels to match ones already used","unanimity",newLabel)
		elif split == "yes":
			log("LatSplit",title,"")
			print(title + " Latin-script labels not unanimous")
	except pywikibot.exceptions.OtherPageSaveError:
		log("APIErrors",title,"while labeling/aliasing")
		print("APIError: " + title)

# The framework of the script:

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
