#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, re, xbmcgui#, datetime
from neverwise import Util


class ServizioPubblico(object):

  _handle = int(sys.argv[1])
  _params = Util.urlParametersToDict(sys.argv[2])

  def __init__(self):

    # Visualizzazione del menu.
    if len(self._params) == 0:
      categs = []
      categs.append(['Santoro', 'r', '/canali/santoro'])
      categs.append(['Vauro', 'r', '/canali/vauro'])
      categs.append(['Travaglio', 'r', '/canali/travaglio'])
      categs.append(['Dragoni', 'r', '/canali/dragoni'])
      categs.append(['Puntate', 'e', '/puntate'])
      categs.append(['Argomenti', 't', '/argomenti'])
      categs.append(['Gli inviati', 'n', '/gli-inviati'])
      items = []
      for title, paramId, page in categs:
        li = Util.createListItem(title, streamtype = 'video', infolabels = { 'title' : title })
        items.append([{ 'id' : paramId, 'page' : page }, li, True, True])
      Util.addItems(self._handle, items)
    else:
      util = Util(self._createPage(self._params['page']))
      if not util._responseError:

        # Archivi (santoro, vauro, travaglio, dragoni e argomenti).
        if self._params['id'] == 'i':
          self._showArchiveList(util.getBSHtml(), self._params['id'])

        # Puntate.
        elif self._params['id'] == 'e':
          response = util.getBSHtml().find('div', 'col-xs-8 right-border')
          self._showList(response.renderContents(), self._params['id'])

        # Argomenti.
        elif self._params['id'] == 't':
          response = util.getHtml()
          categs = re.compile('<div class="col-xs-12 single-argomento"> <a href="(.+?)" title="(.+?)".+?<img.+?src="(.+?)".+?<div class="post-content">(.+?)</div>').findall(response)
          items = []
          for link, title, img, descr in categs:
            title = Util.normalizeText(title)
            if title.lower().find('fatto quotidiano') == -1:
              li = Util.createListItem(title, thumbnailImage = self._normalizeImage(img), streamtype = 'video', infolabels = { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(descr)) })
              items.append([{ 'id' : 'r', 'page' : link }, li, True, True])
          self._showNextPage(response, self._params['id'], items)
          Util.addItems(self._handle, items)

        # Gli inviati.
        elif self._params['id'] == 'n':
          response = re.compile('<div class="post-[0-9]+ persone.+?">.+?<a href="(.+?)" title="(.+?)"> <img.+?src="(.+?)"').findall(util.getHtml())
          items = []
          for link, title, img in response:
            title = Util.normalizeText(title)
            li = Util.createListItem(title, thumbnailImage = self._normalizeImage(img), streamtype = 'video', infolabels = { 'title' : title })
            items.append([{ 'id' : 'e', 'page' : link }, li, True, True])
          Util.addItems(self._handle, items)

        # Ricerca categID.
        elif self._params['id'] == 'r':
          categid = re.compile('\?cat_id=([0-9]+)"').findall(util.getHtml())[0]
          link = self._GetSPPage('/?p=15546&cat_id={0}'.format(categid))
          if categid == '2': # Per evitare di mangiarsi un video adotto questo barbatrucco.
            link = self._GetSPPage('/?p=15526&cat_id=2')
          response = Util(link).getBSHtml(True)
          if response != None:
            self._showArchiveList(response, 'i')

        # Riproduzione del video.
        elif self._params['id'] == 'v':
          urlParam = re.compile('<div class="meride-video-container" data-embed="(.+?)" data-customer="(.+?)" data-nfs="(.+?)"').findall(util.getHtml())
          if len(urlParam) > 0:
            urlParam = urlParam[0]
            tide = re.compile('<h3 class="entry-title">(.+?)</h3>.+?<p>(.+?)</p>').findall(util.getHtml())[0]
            response = Util('http://mediasp.meride.tv/embedproxy.php/{0}/folder1/{1}/desktop'.format(urlParam[1], urlParam[0])).getHtml(True)
            if response != None:
              urls = re.compile('<video.+?<iphone><!\[CDATA\[(.+?)]]></iphone><mp4><!\[CDATA\[(.+?)]]></mp4><poster><!\[CDATA\[(.+?)]]></poster>').findall(response)[0]
              title = Util.normalizeText(tide[0])
              try:
                Util.playStream(self._handle, title, urls[2], urls[0], 'video', { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(tide[1])) })
              except:
                Util.playStream(self._handle, title, urls[2], urls[1], 'video', { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(tide[1])) })
          else:
            Util.showVideoNotAvailableDialog()
      else:
        Util.showConnectionErrorDialog()


  def _GetSPPage(self, link):
    return 'http://www.serviziopubblico.it{0}'.format(link)


  def _createPage(self, link):
    if link[0:1] == '/':
      return self._GetSPPage(link)
    else:
      return self._GetSPPage('/{0}'.format(link))


  def _normalizeImage(self, image):
    subImg = image[image.rfind('-'):image.rfind('.')]
    result = self._createPage(image.replace(subImg, ''))
    if re.match('[0-9]+x[0-9]+', subImg) == None:
      result = self._createPage(image)
    return result


  def _showNextPage(self, html, urlId, items):
    nextPage = re.compile('<span class="current">.+?href="(.+?)".+?([0-9]+)</a>').findall(html)
    if len(nextPage) > 0:
      items.append([{ 'id' : urlId, 'page' : Util.normalizeText(nextPage[0][0]) }, Util.createItemPage(Util.normalizeText(nextPage[0][1])), True, True])


  def _showList(self, html, urlId):
    videos = re.compile('<div class="post-[0-9]+ (post|puntate).+?">.+?href="(.+?)" title="(.+?)".+?<img.+?src="(.+?)".+?</h4></a>(.+?)</div>.+?<div class="foot-post-loop">(.+?)<div class="social-share"').findall(html)
    items = []
    for unuse, link, title, img, descr, media in videos:
      if media.strip() == '<div class="icon-post flaticon-facetime"></div>':
        title = Util.normalizeText(title)
        li = Util.createListItem(title, thumbnailImage = self._normalizeImage(img), streamtype = 'video', infolabels = { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(descr)) }, isPlayable = True)
        items.append([{ 'id' : 'v', 'page' : link }, li, False, True])
    self._showNextPage(html, urlId, items)
    Util.addItems(self._handle, items)


  def _showArchiveList(self, html, urlId):
    seeMore = html.find('div', 'see-more-container')
    html = html.find('div', 'col-xs-8 right-border').renderContents()
    if seeMore != None:
      html = html.replace(seeMore.renderContents(), '')
    self._showList(html, urlId)


# Entry point.
#startTime = datetime.datetime.now()
sp = ServizioPubblico()
del sp
#print '{0} azione {1}'.format(Util._addonName, str(datetime.datetime.now() - startTime))
