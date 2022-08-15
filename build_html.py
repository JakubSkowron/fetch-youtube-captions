#!/usr/bin/env python3
from itertools import islice
import sys
import urllib.parse
import re

header = """\
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Expressions françaises</title>
  <style>
  body {
    color: black;
    padding-top: 3em;
  }
  .row {
    text-align: center;
  }
  .row:hover {
    background-color: #eee;
  }
  .row.selected {
    background-color: #e7e7e7;
  }
  .row span.number {
    display: inline-block;
    text-align: right;
    min-width: 3em;
    margin-right: 0.5em;
    font-size: smaller;
  }
  .row span.phrase {
    display: inline-block;
    min-width: 30%;
    font-family: sans-serif;
    font-size: larger;
    text-align: center;
  }
  a.big {
    display: inline-block;
    color: gray;
    text-decoration: none;
    margin-left: 0.5em;
    margin-right: 0.5em;
  }
  .phrase a {
    color: black;
    text-decoration: none;
  }
  .phrase a:hover {
    background-color: #ddd;
  }
  button {
    padding: 0.5ex;
    font-size: larger;
  }
  button#random {
    position: fixed;
    left: 1ex;
    top: 1ex;
  }
  span.percent {
    display: inline-block;
    font-size: x-small;
    min-width: 3em;
    text-align: right;
  }
  #navbar {
    display: inline-block;
    position: fixed;
    top: 1ex;
    right: 1ex;
    font-size: larger;
  }
  </style>
  <script>
  function jumpToRandom() {
    let rows = document.querySelectorAll('.row');
    let row = rows[ Math.floor( Math.random()*rows.length ) ];
    row.classList.add("selected");
    row.scrollIntoView({behaviour:"smooth", block:"center"});
  }
  </script>
</head>
<body>
<button id="random" onclick="jumpToRandom()">🎲au hasard</button>
"""


row_template = '''\
<div class="row" id="row{n}">
<span class="number">{n}</span><span class="phrase">{phrase_html}</span>
<a class="big" href="https://translate.google.com/?sl=fr&tl=en&text={gtranslate}" target="_blank" rel="noopener noreferrer" title="Google Translate: {phrase}">🇫🇷→🇬🇧</a>
<a class="big" href="https://youglish.com/pronounce/{youglish}/french" target="_blank" rel="noopener noreferrer" title="{phrase}">🇫🇷YouGlish</a>
<span class="percent">{percent:.1f}%</span>
</div>
'''

wiki_link_html = '<a href="https://fr.wiktionary.org/wiki/{quoted}#Fran%C3%A7ais" target="_blank" rel="noopener noreferrer" title="🇫🇷Wiktionnaire: {raw}">{raw}</a>'

# TODO: How to get pronunciations from wiktionary through api.php
# https://fr.wiktionary.org/w/api.php?format=json&action=query&export&titles=command%C3%A9|plus
# https://fr.wiktionary.org/w/api.php?format=xml&action=query&export&exportnowrap&titles=command%C3%A9|plus

# Replaces all matches using functor


def transform_matched(regex, functor, text):
    matches = list(re.finditer(regex, text))
    res = text[:matches[0].start()]
    for m1, m2 in zip(matches, islice(matches, 1, None)):
        s = text[m1.start():m1.end()]
        res += functor(s)
        res += text[m1.end():m2.start()]

    s = text[matches[-1].start():matches[-1].end()]
    res += functor(s)
    res += text[matches[-1].end():]
    return res


max_phrase_length = 5
for n in range(1, max_phrase_length+1):
    in_filename = "stat{}.txt".format(n)
    with open(in_filename, "r") as in_file:
        out_filename = "index{}.html".format(n)
        print("Writing", out_filename)
        with open(out_filename, "w") as out_file:
            print(header, file=out_file)
            print('<div id="navbar">', file=out_file)
            if n > 1:
                print('<button onclick="location.href=\'index{}.html\'">plus courtes</button>'.format(n-1), file=out_file)
            if n < max_phrase_length:
                print('<button onclick="location.href=\'index{}.html\'">plus longues</button>'.format(n+1), file=out_file)
            print('</div>', file=out_file)
            first_count = None
            for i, phrase in enumerate(in_file):
                phrase, count = phrase.strip().split('\t')
                count = int(count)
                if not first_count:
                    first_count = count
                wiki = urllib.parse.quote(phrase.replace(' ', '_'))
                quoted = urllib.parse.quote(phrase)
                html = transform_matched(
                    "\w+'?", lambda x: wiki_link_html.format(quoted=urllib.parse.quote(x), raw=x), phrase)
                percent = 100*count/first_count
                print(row_template.format(n=i+1, phrase=phrase, phrase_html=html,
                      wiki=wiki, youglish=quoted, gtranslate=quoted, percent=percent), file=out_file)

            print("""\
      </body>
      </html>
      """, file=out_file)
