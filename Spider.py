# Copyright 2012 Google Inc. All Rights Reserved.

"""One-line documentation for Spider module.

crawler for detectLanguage
"""

__author__ = 'rozum@google.com (Myroslav Rozum)'
#import urllib2
from google.appengine.api import urlfetch
from BeautifulSoup import *
import re

class Spider:
  url_dictionary =  {
    'en' : 'http://en.wikipedia.org/wiki/Special:Random',
    'ru' : 'http://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0',
    'ua' : 'http://uk.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B5%D1%86%D1%96%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0:%D0%92%D0%B8%D0%BF%D0%B0%D0%B4%D0%BA%D0%BE%D0%B2%D0%B0_%D1%81%D1%82%D0%BE%D1%80%D1%96%D0%BD%D0%BA%D0%B0',
    'fr' : 'http://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard',
    'de' : 'http://de.wikipedia.org/wiki/Spezial:Zuf%C3%A4llige_Seite',
    'es' : 'http://es.wikipedia.org/wiki/Especial:Aleatoria',
    'pl' : 'http://pl.wikipedia.org/wiki/Specjalna:Losowa_strona',
    'eo' : 'http://eo.wikipedia.org/wiki/Speciala%C4%B5o:Hazarda_pa%C4%9Do',
    'zh' : 'http://zh.wikipedia.org/wiki/Special:%E9%9A%8F%E6%9C%BA%E9%A1%B5%E9%9D%A2',
    'ar' : 'http://fa.wikipedia.org/wiki/%D9%88%DB%8C%DA%98%D9%87:%D8%B5%D9%81%D8%AD%D9%87_%D8%AA%D8%B5%D8%A7%D8%AF%D9%81%DB%8C',
    'pt' : 'http://pt.wikipedia.org/wiki/Especial:Aleat%C3%B3ria'
    }

  def __init__(self, data):
    self.result = ''
    self.content = ''
    self.encoding = 'UTF-8'

    if data.startswith('http://'):
      url = data
    elif data in self.url_dictionary.keys():
      url = self.get_url_by_lang(data)
      self.lang = data
    else:
      self.result = data
      self.content = data
      return
    
    result = urlfetch.fetch(url)
    charset = re.match(r'.*charset=(.+)', result.headers.get('Content-Type', ''))
    if charset:
      self.encoding = charset.group(1)
    else:
      self.encoding = 'UTF-8'

    self.content = result.content.decode(self.encoding)
    soup = BeautifulSoup(self.content)
    body = soup.body
 
    for tag in ('style', 'script', 'ul', 'a', 'noindex'):
      [ s.extract() for s in body(tag) ]
  
    for comment in body.findAll(text=lambda text:isinstance(text, Comment)):
      comment.extract()

    result = ''.join([ t for t in body(text=True) if t != '\n' ]).strip()
    self.result = re.sub(r'\s+', ' ', result)

  def get_url_by_lang(self, lang):
    return self.url_dictionary.get(lang, self.url_dictionary['en'])

    print tag.strings

def main():
  spider = Spider('ru')
  print spider.content

if __name__ == '__main__':
  main()
