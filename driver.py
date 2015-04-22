from gensim import corpora, models, similarities
import nltk
import string
import re
from nltk.stem import PorterStemmer
import sys
import langid
from nltk import cluster
import operator
import collections
import os

stemmer= PorterStemmer()

def read_file(f):
	text= open(f, "r").read()
	stopset= set(nltk.corpus.stopwords.words("english"))
	tokens = re.split(r'\s', text)
	tokens = filter(None, tokens)
	tokens = map(lambda x: x.strip(".!?,:;()[]<>"), tokens)
	tokens = map(lambda x: x.lower(), tokens)
	tokens = [stemmer.stem(t) for t in tokens if not t in stopset and re.match(r'[A-Za-z]+$', t) and len(t) > 2]
	return ' '.join(tokens)

	

def create_apt_cache(directory):
	d= collections.defaultdict(list)
	document_list=[]
	handle_list= []
	for root, dirs, files in os.walk(directory):

		folder=""
		try:
			folder= root.split("/")[1]
		except:
			print "Error Tokenizing Directory"

		if not folder== "" and not folder == ".git" and not folder=="ScreenShots":

			for f in files:
				path = directory + "/" + folder + "/" + f
				html= read_file(path)
				document_list.append(html)
				handle_list.append( (str(folder)+str("/")+str(f)) )
				d[folder].append(f)
	return d, document_list, handle_list

d, documents, handles= create_apt_cache("reports_txt")

# stop_set= set(nltk.corpus.stopwords.words("english"))

# texts = [[word for word in document.lower().split() if word not in stop_set] for document in documents]
# all_tokens = sum(texts, [])

# tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
# tokens_digit= set(word for word in set(all_tokens) if word.isdigit())
# texts = [[word for word in text if word not in tokens_once] for text in texts]
# texts = [[word for word in text if word not in tokens_digit] for text in texts]



# dictionary= corpora.Dictionary(texts)
# dictionary.save('apt_dictionary.dict')
dictionary = corpora.Dictionary.load('apt_dictionary.dict')


# corpus = [dictionary.doc2bow(text) for text in texts]
# corpora.MmCorpus.serialize('apt_corpus.mm', corpus)
corpus = corpora.MmCorpus('apt_corpus.mm')

tfidf = models.TfidfModel(corpus)

corpus_tfidf = tfidf[corpus]

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=20)

corpus_lsi = lsi[corpus_tfidf]
topics= lsi.print_topics(20)
print "*************************** Top 20 Topics ****************************************"
for t in topics:
	print t.split("+")
print "**********************************************************************************"
print "\n"


def get_similar_reports(document):

	vec_bow = dictionary.doc2bow(document.lower().split())
	vec_lsi = lsi[vec_bow] # convert the query to LSI space

	index = similarities.MatrixSimilarity(lsi[corpus])

	sims = index[vec_lsi] # perform a similarity query against the corpus

	sims = sorted(enumerate(sims), key=lambda item: -item[1])
	print "Similarity", "\t", "Report"
	count =0
	for s in sims[:10]: #start from 1 because the 0th report would be the itself
		if count ==0:
			print s[1], "\t\t", handles[s[0]]
		else:
			print s[1], "\t", handles[s[0]]
		count+=1



for i in range(len(documents)):
	print "*************************** "+ str(handles[i])+" ****************************************"

	print get_similar_reports(documents[i])
	print "***********************************************************************************************"
	print "\n"


