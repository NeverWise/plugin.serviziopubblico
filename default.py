#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, re, xbmcgui, xbmcplugin#, datetime
from neverwise import Util


class ServizioPubblico:

  __handle = int(sys.argv[1])
  __params = Util.urlParametersToDict(sys.argv[2])
  __idPlugin = 'plugin.serviziopubblico'
  __namePlugin = 'Servizio Pubblico'
  __itemsNumber = 0

  def __init__(self):

    # Visualizzazione del menu.
    if len(self.__params) == 0:
      categs = []
      categs.append(['Santoro', 'r', self.__GetSPPage('/canali/santoro')])
      categs.append(['Vauro', 'r', self.__GetSPPage('/canali/vauro')])
      categs.append(['Travaglio', 'r', self.__GetSPPage('/canali/travaglio')])
      categs.append(['Dragoni', 'r', self.__GetSPPage('/canali/dragoni')])
      categs.append(['Puntate', 'e', self.__GetSPPage('/puntate')])
      categs.append(['Argomenti', 't', self.__GetSPPage('/argomenti')])
      categs.append(['Gli inviati', 'n', self.__GetSPPage('/gli-inviati')])
      for title, paramId, page in categs:
        Util.addItem(self.__handle, title, '', '', 'video', { 'title' : title }, None, { 'id' : paramId, 'page' : page }, True)
        self.__itemsNumber += 1
    else:
      util = Util(self.__params['page'])
      if not util.hasErrors():

        # Archivi (santoro, vauro, travaglio, dragoni e argomenti).
        if self.__params['id'] == 'i':
          self.__showArchiveList(util.getBSHtml(), self.__params['id'])

        # Puntate.
        elif self.__params['id'] == 'e':
          response = util.getBSHtml().find('div', 'col-xs-8 right-border')
          self.__showList(response.renderContents(), self.__params['id'])

        # Argomenti.
        elif self.__params['id'] == 't':
          response = util.getHtml()
          categs = re.compile('<div class="col-xs-12 single-argomento"> <a href="(.+?)" title="(.+?)".+?<img.+?src="(.+?)".+?<div class="post-content">(.+?)</div>').findall(response)
          for link, title, img, descr in categs:
            title = Util.normalizeText(title)
            if title.lower().find('fatto quotidiano') == -1:
              Util.addItem(self.__handle, title, self.__normalizeImage(img), '', 'video', { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(descr)) }, None, { 'id' : 'r', 'page' : self.__createPage(link) }, True)
            self.__itemsNumber += 1
          self.__showNextPage(response, self.__params['id'])

        # Gli inviati.
        elif self.__params['id'] == 'n':
          response = re.compile('<div class="post-[0-9]+ persone.+?">.+?<a href="(.+?)" title="(.+?)"> <img.+?src="(.+?)"').findall(util.getHtml())
          for link, title, img in response:
            title = Util.normalizeText(title)
            Util.addItem(self.__handle, title, self.__normalizeImage(img), '', 'video', { 'title' : title }, None, { 'id' : 'e', 'page' : self.__createPage(link) }, True)
            self.__itemsNumber += 1

        # Ricerca categID.
        elif self.__params['id'] == 'r':
          categid = re.compile('\?cat_id=([0-9]+)"').findall(util.getHtml())[0]
          response = Util(self.__createCategPage(categid)).getBSHtmlDialog(self.__namePlugin)
          if response != None:
            self.__showArchiveList(response, 'i')

        # Riproduzione del video.
        elif self.__params['id'] == 'v':
          urlParam = re.compile('<div class="meride-video-container" data-embed="(.+?)" data-customer="(.+?)" data-nfs="(.+?)"').findall(util.getHtml())
          if len(urlParam) > 0:
            urlParam = urlParam[0]
            tide = re.compile('<h3 class="entry-title">(.+?)</h3>.+?<p>(.+?)</p>').findall(util.getHtml())[0]
            response = Util('http://mediasp.meride.tv/embedproxy.php/{0}/folder1/{1}/desktop'.format(urlParam[1], urlParam[0])).getHtmlDialog(self.__namePlugin)
            if response != None:
              urls = re.compile('<video.+?<iphone><!\[CDATA\[(.+?)]]></iphone><mp4><!\[CDATA\[(.+?)]]></mp4><poster><!\[CDATA\[(.+?)]]></poster>').findall(response)[0]
              title = Util.normalizeText(tide[0])
              li = Util.createListItem(title, urls[2], '', 'video', { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(tide[1])) })
              try:
                xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(urls[0], li)
              except:
                xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(urls[1], li)
          else:
            xbmcgui.Dialog().ok(self.__namePlugin, Util.getTranslation(self.__idPlugin, 30001)) # Messaggio d'errore "Video non disponibile".
      else:
        Util.showConnectionErrorDialog(self.__namePlugin)

    if self.__itemsNumber > 0:
      xbmcplugin.endOfDirectory(self.__handle)


  def __GetSPPage(self, link):
    return 'http://www.serviziopubblico.it{0}'.format(link)


  def __createCategPage(self, idCateg):
    if idCateg == '2': # Per evitare di mangiarsi un video adotto questo barbatrucco.
      return self.__GetSPPage('/?p=15526&cat_id=2')
    else:
      return self.__GetSPPage('/?p=15546&cat_id={0}'.format(idCateg))


  def __createPage(self, link):
    if link[0:1] == '/':
      return self.__GetSPPage(link)
    else:
      return self.__GetSPPage('/{0}'.format(link))


  def __normalizeImage(self, image):
    subImg = image[image.rfind('-'):image.rfind('.')]
    result = self.__createPage(image.replace(subImg, ''))
    if re.match('[0-9]+x[0-9]+', subImg) == None:
      result = self.__createPage(image)
    return result


  def __showNextPage(self, html, urlId):
    if self.__itemsNumber > 0:
      nextPage = re.compile('<span class="current">.+?href="(.+?)".+?([0-9]+)</a>').findall(html)
      if len(nextPage) > 0:
        pageNum = Util.normalizeText(nextPage[0][1])
        Util.AddItemPage(self.__handle, pageNum, '', '', { 'title' : pageNum }, { 'id' : urlId, 'page' : self.__createPage(Util.normalizeText(nextPage[0][0])) })


  def __showList(self, html, urlId):
    videos = re.compile('<div class="post-[0-9]+ (post|puntate).+?">.+?href="(.+?)" title="(.+?)".+?<img.+?src="(.+?)".+?</h4></a>(.+?)</div>.+?<div class="foot-post-loop">(.+?)<div class="social-share"').findall(html)
    for unuse, link, title, img, descr, media in videos:
      if media.strip() == '<div class="icon-post flaticon-facetime"></div>':
        title = Util.normalizeText(title)
        Util.addItem(self.__handle, title, self.__normalizeImage(img), '', 'video', { 'title' : title, 'plot' : Util.normalizeText(Util.trimTags(descr)) }, None, { 'id' : 'v', 'page' : self.__createPage(link) }, True)
        self.__itemsNumber += 1
    self.__showNextPage(html, urlId)


  def __showArchiveList(self, html, urlId):
    seeMore = html.find('div', 'see-more-container')
    html = html.find('div', 'col-xs-8 right-border').renderContents()
    if seeMore != None:
      html = html.replace(seeMore.renderContents(), '')
    self.__showList(html, urlId)


# Entry point.
#startTime = datetime.datetime.now()
sp = ServizioPubblico()
del sp
#print '{0} azione {1}'.format(self.__namePlugin, str(datetime.datetime.now() - startTime))
