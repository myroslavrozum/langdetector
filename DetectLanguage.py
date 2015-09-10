import webapp2
import cgi
import os
import jinja2
from Spider import Spider
from LangTools import LangDetector


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DetectLanguage(webapp2.RequestHandler):
  def post(self):
    lds = []
    distances = {}
    url = cgi.escape(self.request.get('content'))
    languageFullNames = LangDetector.SupportedLanguages
    spider = Spider(url)
  
    out = spider.result#[0:1000] + '...'
    jamesBond = LangDetector(spider.result, spider.encoding)

    for lang in languageFullNames.iterkeys():
      data = LangDetector.restore_trigrammes(lang)
      encoding = 'UTF-8'
      dump_trigrammes = False
      if not data:  
        spider = Spider(lang)
        data = spider.result
        dump_trigrammes = True
        encoding = spider.encoding
      
      langDetector = LangDetector(data, encoding)
      langDetector.language = lang
      if dump_trigrammes: langDetector.dumpTrigrammes()
      lds.append(langDetector)
  
    for ld in lds:
      jamesBond.calculateDistances(ld.trigrammes)
      distances[ld.language] =  jamesBond.totalDistance
  
    out += '<br><br>'
    for w in sorted(distances, key=distances.get, reverse=False)[0:2]:
      out += "<b>Distance to %s : %f</b><br>" % (languageFullNames[w], distances[w])
 
    detected_lang = min(distances, key=distances.get)
    lang = languageFullNames[detected_lang]
    #out += "==============> Language is %s<br>" % lang
 
    template_values = {
      'detected_language' : detected_lang,
      'log' : out,
      'supported_languages' : LangDetector.SupportedLanguages
    }
    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(template_values))
