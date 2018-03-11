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
title = u"harp"
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
				strDict["level-" + str(t)] = {} # create placeholder sub-dict
				strDict["level-" + str(t)][strSplit[1]] = strSplit[2] # old lang as key, word in old lang as value, w/i level-based keys
			t += 1
			
		if template == "cog":
			return strDict
		elif "level 1" in strDict:
			return(strDict["level-1"]) # only the 1st level really seems useful for Wikidata, but parsing all levels may be useful for other purposes
		
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
				etymDict["derived terms"] = parseEtymology("der")
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
					if re.search(r"audio \(.*\)",string):
						lang = string.split("{{" + template + "|")[1].split("}}")[0].split("|")[param].replace("audio (","").replace(")","")
					else:
						lang = "unknown/all"
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
		
def getLinkedTerms1(type,template):
	def parseLinkedTerms():
		termSplit = terms.split("* {{" + template + "|")
		for string in termSplit:
			strSplit = string.split("|")
			try:
				strClean = re.sub("\}\}.*","",strSplit[1],flags=re.S)
			except IndexError:
				pass
			else:
				termList.append(strClean)
		
	if "===" + type + "===" in English:
		EnSplit = English.split("===" + type + "===")
		terms = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		termList = []
		parseLinkedTerms()
		if termList:
			return termList

def getLinkedTerms2(type,abbr,form):
	def parseLinkedTerms():
		def appendTerm(string):
			strClean2 = re.sub(r" *\[+","",string,flags=re.S)
			strClean3 = re.sub(r"[\}\]<\n].*","",strClean2,flags=re.S)
			if strClean3 and not ("{{" + abbr or "lang=" or "title=" or "{{checksense") in strClean3: # clean up params
				if "|" in strClean3:
					strSplit2 = strClean3.split("|")
					try:
						termList.append(strSplit2[2])
					except IndexError:
						pass	
				else:
					termList.append(strClean3)
		if "{{" + abbr in terms:
			termSplit = terms.split("\n|")
		elif "*" in terms:
			termSplit = terms.split("*")
		else:
			raise Exception(type)
		for string in termSplit:
			strClean1 = re.sub("<!--.*-->","",string)
			if ", " in strClean1:
				strSplit1 = strClean1.split(", ")
				for substring in strSplit1:
					appendTerm(substring)
			else:
				appendTerm(strClean1)
	
	if "===" + form + "===" in English:
		EnSplit = English.split("===" + form + "===")
		formSection = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		if "====" + type + "====" in formSection:
			formSectSplit = formSection.split("====" + type + "====")
			terms = re.split(r"\n={4}[^=]*={4}\n",formSectSplit[1])[0]
			termList = []
			parseLinkedTerms()
			if termList:
				return termList
	
if "==english==" in text:
	textSplit = text.split("==english==")
	English = re.split(r"\n={2}[^=]*={2}\n",textSplit[1])[0]
	
	masterDict = {}
	
	masterDict["etymology"] = getEtymology()
	masterDict["pronunciation"] = getPronunciation()
	
	masterDict["alternative forms"] = getLinkedTerms1("alternative forms","l")
	
	masterDict["derived-terms"] = {}
	masterDict["derived-terms"]["from-noun"] = getLinkedTerms2("derived terms","der","noun")
	masterDict["derived-terms"]["from-verb"] = getLinkedTerms2("derived terms","der","verb")
	masterDict["derived-terms"]["from-adj"] = getLinkedTerms2("derived terms","der","adjective")
	masterDict["derived-terms"]["from-adv"] = getLinkedTerms2("derived terms","der","adverb")
	
	masterDict["related-terms"] = {}
	masterDict["related-terms"]["to-noun"] = getLinkedTerms2("related terms","rel","noun")
	masterDict["related-terms"]["to-verb"] = getLinkedTerms2("related terms","rel","verb")
	masterDict["related-terms"]["to-adj"] = getLinkedTerms2("related terms","rel","adjective")
	masterDict["related-terms"]["to-adv"] = getLinkedTerms2("related terms","rel","adverb")
	
	masterDict["hyponyms"] = {}
	masterDict["hyponyms"]["of-noun"] = getLinkedTerms2("hyponyms","hyp","noun") # no template for it, so just use a string that will never occur
	masterDict["hyponyms"]["of-verb"] = getLinkedTerms2("hyponyms","hyp","verb")
	masterDict["hyponyms"]["of-adj"] = getLinkedTerms2("hyponyms","hyp","adjective")
	masterDict["hyponyms"]["of-adv"] = getLinkedTerms2("hyponyms","hyp","adverb")
	
	masterDict["anagrams"] = getLinkedTerms1("anagrams","anagrams")
	
	for entry in list(masterDict): # delete []s, {}s, and Nones
		try:
			for subentry in list(masterDict[entry]):
				if not masterDict[entry][subentry] or masterDict[entry][subentry] is None:
					del masterDict[entry][subentry]
		except (KeyError,TypeError):
			pass
		if not masterDict[entry] or masterDict[entry] is None:
			del masterDict[entry]
			
	print(title)
	print(masterDict)
else:
	print("No English section")
