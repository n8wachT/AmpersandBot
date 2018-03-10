# -*- coding: utf-8  -*-
########################
## AmpersandBot  code ##
##   WiktionaryBot    ##
##   by T. H. Kelly   ##
## aka  PinkAmpersand ##
########################

import pywikibot
import re

site = pywikibot.Site("en","wiktionary")
page = pywikibot.Page(site,u"welcome")
text = page.text

def getEtymology():
	def parseEtymology(template):
		etymSplit = etymology.lower().split("{{" + template + "|")
		del etymSplit[0] # del all text before first call of template
		strDict = {}
		t = 1
		
		for string in etymSplit:
			if re.search(r"\. ",string):
				del etymSplit[etymSplit.index(string) + 1:] # limit to 1 sentence of template calls
			strClean = re.sub(r"\}\}.*","",string,flags=re.S) # rm end brackets and all following text
			strSplit = strClean.split("|")
			if template == "cog":
				strDict[strSplit[0]] = strSplit[1] # other lang as key, word in other lang as value
				print(strDict[strSplit[0]])
			else:
				strDict["level " + str(t)] = {} # create placeholder sub-dict
				strDict["level " + str(t)][strSplit[1]] = strSplit[2] # old lang as key, word in old lang as value, w/i level-based keys
			t += 1
			
		if template == "cog":
			return strDict
		elif "level 1" in strDict:
			return(strDict["level 1"]) # only the 1st level really seems useful for Wikidata, but parsing all levels may be useful for other purposes
		
	if "===Etymology===" in English:
		EnSplit = English.split("===Etymology===")
		etymology = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0] # all of the text between ===Etymology=== and the next section
		if not "\n\n" in etymology: # if it's more than one graf, there's probably nuances this script will miss
			etymDict = {} # create dict of main forms of etymology
			if parseEtymology("inh") is not None:
				etymDict["inherited"] = parseEtymology("inh")
			if parseEtymology("bor") is not None:
				etymDict["borrowed"] = parseEtymology("bor")
			if parseEtymology("der") is not None:
				etymDict["derived"] = parseEtymology("der")
			# etymDict["cognate"] = parseEtymology("cog") # has both false positives and false negatives
			return etymDict
		else:
			print("multi-graf etymology")
			
def getPronunciation():
	def parsePronunciation():
		def tryKeyValue(template,key,param):
			try:
				value = string.split("{{" + template + "|")[1].split("}}")[0].split("|")[param - 1] # get a specific parameter
				if key == "ipa-pron":
					pronDict["accents"][accent]["ipa-pron"] = value
				elif key == "audio":
					# get lang code of audio
					lang = string.split("{{" + template + "|")[1].split("}}")[0].replace("audio (","").replace(")","")
					pronDict["audio"][lang] = value
				else:
					pronDict[key] = value
			except (IndexError, KeyError):
				pass
				
		pronSplit = pronunciation.lower().split("* ")
		pronDict["accents"] = {}
		pronDict["audio"] = {}
		
		for string in pronSplit:
			try:
				accent = string.split("{{a|")[1].split("}}")[0] # get the text between "{{a|" and "}}"
				enPron = string.split("{{enpr|")[1].split("}}")[0]
				pronDict["accents"][accent] = {}
				pronDict["accents"][accent]["en-pron"] = enPron
			except IndexError:
				pass
				
			tryKeyValue("ipa","ipa-pron",1)
			tryKeyValue("audio","audio",1)
			tryKeyValue("rhymes","rhymes",1)
			tryKeyValue("homophones","homophones",2)
			
	if "===Pronunciation===" in English:
		EnSplit = English.split("===Pronunciation===")
		pronunciation = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		pronDict = {}
		parsePronunciation()
		return pronDict

if "==English==" in text:
	textSplit = text.split("==English==")
	English = re.split(r"\n={2}[^=]*={2}\n",textSplit[1])[0]
	
	masterDict = {}
	if getEtymology() is not None:
		masterDict["etymology"] = getEtymology()
	if getPronunciation() is not None:
		masterDict["pronunciation"] = getPronunciation()
	print(masterDict)
else:
	print("No English section")
