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
title = u"rich"
page = pywikibot.Page(site,title)
text = page.text.lower()

def getEtymology():
	def parseEtymology(template):
		etymSplit = etymology.split("{{" + template + "|")
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
			else:
				strDict["level " + str(t)] = {} # create placeholder sub-dict
				strDict["level " + str(t)][strSplit[1]] = strSplit[2] # old lang as key, word in old lang as value, w/i level-based keys
			t += 1
			
		if template == "cog":
			return strDict
		elif "level 1" in strDict:
			return(strDict["level 1"]) # only the 1st level really seems useful for Wikidata, but parsing all levels may be useful for other purposes
		
	if "===etymology===" in English:
		EnSplit = English.split("===etymology===")
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
			except IndexError:
				pass
			else:
				if key == "audio":
					# get lang code of audio
					lang = string.split("{{" + template + "|")[1].split("}}")[0].split("|")[param].replace("audio (","").replace(")","")
					pronDict["audio"][lang] = value
				else:
					pronDict[key] = value
				
		pronSplit = pronunciation.split("* ")
		pronDict["accents"] = {}
		pronDict["audio"] = {}
		
		for string in pronSplit:
			try:
				accents = string.split("{{a|")[1].split("}}")[0].split("|")
			except IndexError:
				try:
					IPAPron = string.split("{{ipa|")[1].split("}}")[0].split("|")[0]
				except(IndexError,KeyError):
					pass
				else:
					pronDict["accents"]["unknown/all"] = {}
					pronDict["accents"]["unknown/all"]["ipa-pron"] = IPAPron # for when {{ipa}} is given w/o {{a}}
			else:
				for accent in accents:
					pronDict["accents"][accent] = {}
					try:
						enPron = string.split("{{enpr|")[1].split("}}")[0]
					except IndexError:
						pass
					else:
						pronDict["accents"][accent]["en-pron"] = enPron
					try:
						IPAPron = string.split("{{ipa|")[1].split("}}")[0].split("|")[0]
					except(IndexError,KeyError):
						pass
					else:
						pronDict["accents"][accent]["ipa-pron"] = IPAPron
				
			try:
				syllables = string.split("{{hyph")[1].split("}}")[0].split("|")[1:]
			except IndexError:
				pass
			else:
				pronDict["hyphenation"] = []
				for syllable in syllables:
					if not "=" in syllable: # ignore named parameters
						pronDict["hyphenation"].append(syllable)
			
			tryKeyValue("audio","audio",1)
			tryKeyValue("rhymes","rhymes",1)
			tryKeyValue("homophones","homophones",2)
			
	if "===pronunciation===" in English:
		EnSplit = English.split("===pronunciation===")
		pronunciation = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		pronDict = {}
		parsePronunciation()
		if not pronDict["accents"]: # avoid {}s in dict
			del pronDict["accents"]
		if not pronDict["audio"]:
			del pronDict["audio"]
		return pronDict
		
def getAltForms():
	def parseAltForms():
		AFSplit = altForms.split("* {{l|")
		for string in AFSplit:
			strSplit = string.split("|")
			try:
				strClean = re.sub("\}\}.*","",strSplit[1],flags=re.S)
			except IndexError:
				pass
			else:
				AFList.append(strClean)
		
	if "===alternative forms===" in English:
		EnSplit = English.split("===alternative forms===")
		altForms = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		AFList = []
		parseAltForms()
		if AFList:
			return AFList

def getDerived(form):
	def parseDerived():
		derivSplit = derivs.split("|")
		for string in derivSplit:
			if not "{{der" in string and not "=" in string:
				if "|" in string:
					strSplit = string.split("|")
					try:
						strClean = re.sub("\}\}.*","",strSplit[2],flags=re.S)
					except IndexError:
						pass
					else:
						derivedList.append(strClean)
				elif "[[" in string:
					strClean = re.sub("\]\].*","",string.strip("["),flags=re.S)
					derivedList.append(strClean)
				else:
					strClean = re.sub("[\}]*\n","",string,flags=re.S)
					derivedList.append(strClean)
	
	if "===" + form + "===" in English:
		EnSplit = English.split("===" + form + "===")
		formSection = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		if "====derived terms====" in formSection:
			formSectSplit = formSection.split("====derived terms====")
			derivs = re.split(r"\n={4}[^=]*={4}\n",formSectSplit[1])[0]
			derivedList = []
			parseDerived()
			if derivedList:
				return derivedList
	
if "==english==" in text:
	textSplit = text.split("==english==")
	English = re.split(r"\n={2}[^=]*={2}\n",textSplit[1])[0]
	
	masterDict = {}
	if getEtymology() and getEtymology() is not None: # avoid <None>s and {}s/[]s in dict
		masterDict["etymology"] = getEtymology()
	if getPronunciation() and getPronunciation() is not None:
		masterDict["pronunciation"] = getPronunciation()
	if getAltForms() and getAltForms() is not None:
		masterDict["alternative forms"] = getAltForms()
	masterDict["derived-terms"] = {}
	if getDerived("noun") and getDerived("noun") is not None:
		masterDict["derived-terms"]["from-noun"] = getDerived("noun")
	if getDerived("verb") and getDerived("verb") is not None:
		masterDict["derived-terms"]["from-verb"] = getDerived("verb")
	if getDerived("adjective") and getDerived("adjective") is not None:
		masterDict["derived-terms"]["from-adj"] = getDerived("adjective")
	if getDerived("adverb") and getDerived("adverb") is not None:
		masterDict["derived-terms"]["from-adv"] = getDerived("adverb")
	print(title)
	print(masterDict)
else:
	print("No English section")
