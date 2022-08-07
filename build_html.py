#!/usr/bin/env python3
import sys
import urllib.parse

print("""\
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Expressions françaises</title>
  <style>
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
    min-width: 12em;
    font-family: sans-serif;
    font-size: larger;
    text-align: center;
  }
  .row a {
    display: inline-block;
    color: gray;
    text-decoration: none;
    margin-left: 0.5em;
    margin-right: 0.5em;
  }
  button#random {
    position: fixed;
    left: 1ex;
    top: 1ex;
    padding: 1ex
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
""")


def wiki_encode(phrase):
    return phrase.replace(" ", "_")


row_format = '''\
<div class="row" id="row{n}">
<span class="number">{n}</span><span class="phrase">{phrase}</span>
<a href="https://fr.wiktionary.org/wiki/{wiki}#Fran%C3%A7ais" target="_blank" rel="noopener">🇫🇷Wiktionnaire</a>
<a href="https://en.wiktionary.org/wiki/{wiki}#French" target="_blank" rel="noopener">🇬🇧Wiktionary</a>
<a href="https://youglish.com/pronounce/{youglish}/french" target="_blank" rel="noopener">🇫🇷YouGlish</a>
<a href="https://translate.google.com/?sl=fr&tl=en&text={gtranslate}" target="_blank" rel="noopener">🇫🇷🇬🇧Google Translate</a>
</div>
'''

# TODO: How to get pronunciations from wiktionary through api.php
# https://fr.wiktionary.org/w/api.php?format=json&action=query&export&titles=command%C3%A9|plus
# https://fr.wiktionary.org/w/api.php?format=xml&action=query&export&exportnowrap&titles=command%C3%A9|plus

with open(sys.argv[1], "r") as input_file:
    for i, phrase in enumerate(input_file):
        phrase = phrase.strip()
        wiki = urllib.parse.quote(phrase.replace(' ', '_'))
        quoted = urllib.parse.quote(phrase)
        print(row_format.format(n=i+1, phrase=phrase,
              wiki=wiki, youglish=quoted, gtranslate=quoted))

print("""\
</body>
</html>
""")
