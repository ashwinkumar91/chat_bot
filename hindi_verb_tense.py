import codecs
import nltk
from nltk.corpus import indian
import re
import sys 

def hasNumbers(inputString):
	return bool(re.search(r'\d', inputString))

def getVerbTag(line):
	verb = ''
	tag = ''
	hin = nltk.corpus.indian.tagged_words()
	if line not in '\t':
		line = line.split()
		verb = line[len(line)-1]
		verb = verb.replace(".","")
		verb = verb.replace("\n","")
		if not hasNumbers(verb):
			for h in hin:
				tag = h[0]
				tag = h[0]
				if verb == tag:
					return h[1]
	else:
		return 'NA'
	
if __name__ == '__main__':
	f = codecs.open(sys.argv[1], encoding='utf-8')
	for line in f:
		getVerbTag(line)

