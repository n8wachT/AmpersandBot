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
title = #u"your entry here"
page = pywikibot.Page(site,title)
text = page.text

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
		
	if "===Etymology===" in English:
		EnSplit = English.split("===Etymology===")
		etymology = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0] # all of the text between ===Etymology=== and the next section
		if not "\n\n" in etymology: # if it's more than one graf, there's probably nuances that this script will miss
			etymDict = {} # create dict of main forms of etymology
			etymDict["inherited-from"] = parseEtymology("inh") # empty content is removed later
			etymDict["borrowed-from"] = parseEtymology("bor")
			etymDict["derived-from"] = parseEtymology("der")
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
				if key == "audio": # get lang code of audio
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
				try: # for when {{IPA}} is given w/o {{a}}
					IPAPron = string.split("{{IPA|")[1].split("}}")[0].split("|")[0]
				except(IndexError,KeyError):
					pass
				else:
					pronDict["accents"]["unknown/all"] = {}
					pronDict["accents"]["unknown/all"]["ipa-pron"] = IPAPron
				try: # for when {{enPR}} is given w/o {{a}}
					enPron = string.split("{{enPR|")[1].split("}}")[0].split("|")[0]
				except(IndexError,KeyError):
					pass
				else:
					pronDict["accents"]["unknown/all"] = {}
					pronDict["accents"]["unknown/all"]["en-pron"] = enPron
			else:
				for accent in accents: # give English pronunciation and/or IPA for a given accent
					pronDict["accents"][accent] = {}
					try:
						enPron = string.split("{{enPR|")[1].split("}}")[0]
					except IndexError:
						pass
					else:
						pronDict["accents"][accent]["en-pron"] = enPron
					try:
						IPAPron = string.split("{{IPA|")[1].split("}}")[0].split("|")[0]
					except(IndexError,KeyError):
						pass
					else:
						pronDict["accents"][accent]["ipa-pron"] = IPAPron
				
			try: # make list out of contents of {{hyph}}
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
			
	if "===Pronunciation===" in English:
		EnSplit = English.split("===Pronunciation===")
		pronunciation = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		pronDict = {}
		parsePronunciation()
		return pronDict
		
def getLinkedTerms1(type,template): # for first-level lists
	def parseLinkedTerms():
		termSplit = terms.split("* {{" + template + "|") # split bullet pts
		for string in termSplit:
			strSplit = string.split("|") # split template params
			try:
				strClean = re.sub("\}\}.*","",strSplit[1],flags=re.S) # rm }} and everything after it
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

def getLinkedTerms2(type,abbr,form): # for second-level lists
	def parseLinkedTerms():
		def appendTerm(string):
			strClean2 = re.sub(r" *\[+","",string,flags=re.S) # rm leading space and [s
			strClean3 = re.sub(r"[\}\]\n].*","",strClean2,flags=re.S) # rm trailing }, ], and \n, plus following chars
			if strClean3 and not ("{{" + abbr or "lang=" or "title=" or "{{checksense") in strClean3: # clean up params
				if "|" in strClean3:
					strSplit2 = strClean3.split("|") # split template params
					try:
						termList.append(strSplit2[2])
					except IndexError:
						pass	
				else:
					termList.append(strClean3)
		if "{{" + abbr in terms: # for lists using templates
			termSplit = terms.split("\n|")
		elif "*" in terms: # for lists using bullets
			termSplit = terms.split("*")
		else:
			raise Exception(type) # are there other kinds of lists? let's find out
		for string in termSplit:
			strClean1 = re.sub("<!--.*-->","",string) # rm HTML comments
			if ", " in strClean1: # multiple values in line?
				strSplit1 = strClean1.split(", ") # then run function once for each val
				for substring in strSplit1:
					appendTerm(substring)
			else:
				appendTerm(strClean1) # otherwise, just run function once
	
	if "===" + form + "===" in English: # usual level-3 header check
		EnSplit = English.split("===" + form + "===")
		formSection = re.split(r"\n={3}[^=]*={3}\n",EnSplit[1])[0]
		if "====" + type + "====" in formSection: # in this case, followed by a level-4 check
			formSectSplit = formSection.split("====" + type + "====")
			terms = re.split(r"\n={4}[^=]*={4}\n",formSectSplit[1])[0]
			termList = []
			parseLinkedTerms()
			if termList:
				return termList
	
if "==English==" in text:
	textSplit = text.split("==English==")
	English = re.split(r"\n={2}[^=]*={2}\n",textSplit[1])[0]
	
	masterDict = {}
	
	masterDict["etymology"] = getEtymology()
	masterDict["pronunciation"] = getPronunciation()
	
	masterDict["alternative forms"] = getLinkedTerms1("alternative forms","l")
	
	masterDict["derived-terms"] = {}
	masterDict["derived-terms"]["from-noun"] = getLinkedTerms2("Derived terms","der","Noun")
	masterDict["derived-terms"]["from-verb"] = getLinkedTerms2("Derived terms","der","Verb")
	masterDict["derived-terms"]["from-adj"] = getLinkedTerms2("Derived terms","der","Adjective")
	masterDict["derived-terms"]["from-adv"] = getLinkedTerms2("Derived terms","der","Adverb")
	
	masterDict["related-terms"] = {}
	masterDict["related-terms"]["to-noun"] = getLinkedTerms2("Related terms","rel","Noun")
	masterDict["related-terms"]["to-verb"] = getLinkedTerms2("Related terms","rel","Verb")
	masterDict["related-terms"]["to-adj"] = getLinkedTerms2("Related terms","rel","Adjective")
	masterDict["related-terms"]["to-adv"] = getLinkedTerms2("Related terms","rel","Adverb")
	
	masterDict["hyponyms"] = {}
	masterDict["hyponyms"]["of-noun"] = getLinkedTerms2("Hyponyms","hyp","Noun")
	masterDict["hyponyms"]["of-verb"] = getLinkedTerms2("Hyponyms","hyp","Verb")
	masterDict["hyponyms"]["of-adj"] = getLinkedTerms2("Hyponyms","hyp","Adjective")
	masterDict["hyponyms"]["of-adv"] = getLinkedTerms2("Hyponyms","hyp","Adverb")
	
	masterDict["anagrams"] = getLinkedTerms1("Anagrams","anagrams")
	
	for entry in list(masterDict): # delete []s, {}s, and Nones
		try: # do it to subentries first, since that will cause some entries to empty out
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
