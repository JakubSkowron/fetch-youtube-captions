#!/usr/bin/env python3
from glob import glob
from operator import add
import string
import xml.etree.ElementTree as ElementTree
from itertools import islice

words_dict = {}


def add_global_phrase(phrase):
    words_dict[phrase] = words_dict.get(phrase, 0) + 1


for filename in glob("xml/*.xml"):
    with open(filename, "r") as xml_file:
        # For some reason the YouTube subtitle XML has double escaped values
        # like &amp;quot; or &amp;#39; in the <text>  elements
        def unescapeEntities(text):
            # HACK
            return next(ElementTree.fromstring("<dummy>" + text + "</dummy>").itertext(), "")

        xml_tree = ElementTree.parse(xml_file)
        xml_root = xml_tree.getroot()

        word_list = []
        for text in xml_root.itertext():
            text = unescapeEntities(text)
            for word in text.split():
                word = word.strip(string.punctuation +
                                  string.digits + '…»«“”€')
                word_list.append(word.lower())

        # returns iterable of tuples
        def make_tuples(n):
            iters = [islice(word_list, i, None) for i in range(n)]
            return zip(*iters)

        for n in range(5):
            for tup in make_tuples(n+1):
                if all(tup):
                    add_global_phrase(' '.join(tup))

# remove rare phrases
item_filter = filter(lambda x: x[1] >= 3, words_dict.items())
phrases = sorted(item_filter, key=lambda x: x[1], reverse=True)
for phrase, count in islice(phrases, 0, 10000):
    print(phrase)
