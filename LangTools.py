# Copyright 2012 Google Inc. All Rights Reserved.

"""One-line documentation for LangTools module.

Different NLP operations, such as - determine language from text, etc.
"""

__author__ = 'rozum@google.com (Myroslav Rozum)'

import re
import json
from google.appengine.ext import db

class Frequencies(db.Model):
  language = db.StringProperty(required = True)
  frequencies = db.TextProperty()


class LangDetector:
  SupportedLanguages = {'en':'English', 'ua':'Ukrainian', 'fr':'French',
                       'ru':'Russian', 'de':'German', 'es':'Spanish',
                       'pl':'Polish', 'eo':'Esperanto', 'zh':'Chineese',
                        'ar':'Arabic', 'pt':'Portuguese'}
  def __init__(self, data, encoding):
    # data = codecs.getdecoder(encoding)(data)[0]
    self.trigrammes = {}
    self.distances = {}
    self.encoding = encoding
    self.totalDistance = 0.0
    self.language = ''

    if type(data).__name__ == 'dict':
      self.trigrammes = data
    else:
      self.data = re.sub(ur'[\d\(\)\[\]\-]', '', data)
      self.detectTrigrammes()

  def detectTrigrammes(self):
    i = 0

    while i < len(self.data):
      trigramme = self.data[i:i+3]
      self.trigrammes[trigramme] = self.trigrammes.get(trigramme, 0) + 1
      i += 1

    numberOftrigrammes = float(len(self.trigrammes))
    for key in self.trigrammes.iterkeys():
      frequency = self.trigrammes[key] / numberOftrigrammes
      self.trigrammes[key] = frequency

  @staticmethod
  def restore_trigrammes(language):
    if not language: return

    data = db.GqlQuery("SELECT * FROM Frequencies WHERE language = :lang",
                                  lang = language)
    if data.count() > 0:
      return json.loads(data[0].frequencies)
    return 

  def dumpTrigrammes(self):
    if not self.language:
      return

    f = None

    serialized_data = json.dumps(self.trigrammes)
    data = db.GqlQuery("SELECT * FROM Frequencies WHERE language = :lang",
                                     lang = self.language)
    if data.count() > 0:
      f = data[0]
      f.frequencies = serialized_data
    else:
      f = Frequencies(language = self.language,
                    frequencies = serialized_data)
    f.put()

  def calculateDistances(self,model):
    for key in self.trigrammes.iterkeys():
      frequency = model.get(key, 0)
      self.distances[key] = abs(self.trigrammes[key] - frequency)

    self.totalDistance = sum(self.distances.itervalues())

def main():
  pass

if __name__ == '__main__':
  main
