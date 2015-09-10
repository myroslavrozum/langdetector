#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import webapp2
import os
import jinja2

from LangTools import LangDetector
from Spider import Spider
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Train(webapp2.RequestHandler):
  def get(self):
    out = ''
    
    for lang in LangDetector.SupportedLanguages.iterkeys():
      out += self.train_language(lang)

    template_values = {
      'log' : out,
      'supported_languages' : LangDetector.SupportedLanguages
    }
    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(template_values))

  def train_language(self, lang):
    out = ''
    ld_orig = None

    spider = Spider(lang)
    data = spider.result
    encoding = spider.encoding
    ld_new = LangDetector(data, encoding)
    ld_new.language = lang

    data = LangDetector.restore_trigrammes(lang)
    if data:
      ld_orig = LangDetector(data, 'UTF-8')
      ld_orig.language = lang

      number_of_trigrammes = len(ld_orig.trigrammes)
      avg_freq = sum(ld_orig.trigrammes.values()) / number_of_trigrammes
      min_freq = min(ld_orig.trigrammes.values())
      dispersion = sum(( abs(avg_freq - x)  for x in ld_orig.trigrammes.itervalues() )) / number_of_trigrammes
      low_freq_values = len([ x for x in ld_orig.trigrammes.itervalues() if x < (avg_freq - dispersion) ])
      out += "%s: Total values %d,  avg frequency: %f, dispersion %f, LF items %d<br>" % (lang,
                                                                                        number_of_trigrammes,
                                                                                        avg_freq,
                                                                                        dispersion,
                                                                                        low_freq_values)
    else:
      out += 'No data for %s<br>' % lang

    for trigramme in ld_new.trigrammes.iterkeys():
      if not ld_orig:
        continue
      original_frequency = ld_orig.trigrammes.get(trigramme, 0.0)
      new_frequency = ld_new.trigrammes.get(trigramme, 0.0)
      result_frequency = (original_frequency + new_frequency) / 2.0
      ld_new.trigrammes[trigramme] = result_frequency

    #Add old trigrammes if there were not present in a collection
    if ld_orig:
      for trigramme in ld_orig.trigrammes.iterkeys():
        if(not ld_new.trigrammes.has_key(trigramme)):
          ld_new.trigrammes[trigramme] = ld_orig.trigrammes[trigramme]
    
    ld_new.dumpTrigrammes()
    return out

