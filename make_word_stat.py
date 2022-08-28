#!/usr/bin/env python3
from glob import glob
from operator import add
import string
import xml.etree.ElementTree as ElementTree
from itertools import islice

max_phrase_length = 5
count_threshold = 0.002
max_phrases = 10000

words_dict = {}

def add_global_phrase(phrase):
    words_dict[phrase] = words_dict.get(phrase, 0) + 1


for filename in glob("xml/*.xml"):
    print("Reading", filename)
    with open(filename, "r") as xml_file:
        # For some reason the YouTube subtitle XML has double escaped values
        # like &amp;quot; or &amp;#39; in the <text>  elements
        def unescapeEntities(text):
            # HACK
            return next(ElementTree.fromstring("<dummy>" + text + "</dummy>").itertext(), "")

        xml_tree = ElementTree.parse(xml_file)
        xml_root = xml_tree.getroot()

        word_list = []
        for text in xml_root.itertext():  # TODO: phrases spanning two lines of text
            text = unescapeEntities(text)
            text = text.lower()
            # TODO: make this exceptions more robust:
            # check if there are whitespaces before and after, and collapse whitespaces in between
            text = text.replace("il y a", "il+y+a")  # '+' means we want to count it as one word
            text = text.replace("il n'y a", "il+n'y+a")
            text = text.replace("il y en a", "il+y+en+a")
            text = text.replace("parce que", "parce+que")
            text = text.replace("qu'est ce", "qu'est-ce")
            text = text.replace("est ce qu", "est-ce qu")
            text = text.replace("[musique]", "")
            text = text.replace("[rires]", "")
            text = text.replace("[applaudissements]", "")
            for word in text.split():
                word = word.strip(string.punctuation +
                                  string.digits + '…»«“”€–')
                word = word.replace("+", " ")
                word_list.append(word)

        # returns iterable of tuples
        def make_tuples(n):
            iters = [islice(word_list, i, None) for i in range(n)]
            return zip(*iters)

        for n in range(1, max_phrase_length+1):
            for tup in make_tuples(n):
                if all(tup):
                    add_global_phrase(tup)

# remove rare phrases
filtered = filter(lambda x: x[1] >= 5, words_dict.items())
phrases = sorted(filtered, key=lambda x: x[1], reverse=True)

for n in range(1, max_phrase_length+1):
    filename = 'stat{}.txt'.format(n)
    print("Writing", filename)
    with open(filename, 'w') as output_file:
        filtered = filter(lambda x: len(x[0]) >= n, phrases)
        for phrase, count in islice(filtered, max_phrases):
            print(' '.join(phrase), count, sep='\t', file=output_file)
