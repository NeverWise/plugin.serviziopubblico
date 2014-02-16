#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 1.0.1 (24/11/2013)
# Servizio Pubblico
# La trasmissione nasce dall'interruzione in RAI dello storico talk-show politico Annozero ed e' contrassegnata da accese polemiche sulla liberta' d'informazione in Italia, in particolare con riferimento al controllo della RAI da parte dei partiti politici.
# By NeverWise
# <email>
# <web>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################
import sys, re, xbmcgui, xbmcplugin, tools#, datetime


def createCategPage(idCateg):
  link = 'http://www.serviziopubblico.it/?p=15546&cat_id=' + idCateg
  if idCateg == '2': # Per evitare di mangiarsi un video adotto questo barbatrucco.
    link = 'http://www.serviziopubblico.it/?p=15526&cat_id=2'
  return link


def createPage(link):
  result = 'http://www.serviziopubblico.it/' + link
  if link[0:1] == '/':
    result = 'http://www.serviziopubblico.it' + link
  return result


def normalizeImage(image):
  subImg = image[image.rfind('-'):image.rfind('.')]
  result = createPage(image.replace(subImg, ''))
  if re.match('[0-9]+x[0-9]+', subImg) == None:
    result = createPage(image)
  return result


def showNextPage(html, urlId):
  nextPage = re.compile('<span class="current">.+?href="(.+?)".+?([0-9]+)</a>').findall(html)
  if len(nextPage) > 0:
    title = tools.getTranslation(idPlugin, 30001) + ' ' + nextPage[0][1] + ' >' # Pagina.
    tools.addDir(handle, title, '', '', 'video', { 'title' : title, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : urlId, 'page' : createPage(tools.normalizeText(nextPage[0][0])) })


def showList(html, urlId):
  videos = re.compile('<div class="post-[0-9]+ (post|puntate).+?">.+?href="(.+?)" title="(.+?)".+?<img.+?src="(.+?)".+?</h4></a>(.+?)</div>.+?<div class="foot-post-loop">(.+?)<div class="social-share"').findall(html)
  for unuse, link, title, img, descr, media in videos:
    if media.strip() == '<div class="icon-post flaticon-facetime"></div>':
      title = tools.normalizeText(title)
      tools.addDir(handle, title, normalizeImage(img), '', 'video', { 'title' : title, 'plot' : tools.normalizeText(tools.stripTags(descr)), 'duration' : -1, 'director' : '' }, { 'id' : 'v', 'page' : createPage(link) })
  showNextPage(html, urlId)
  xbmcplugin.endOfDirectory(handle)


def showArchiveList(html, urlId):
  seeMore = html.find('div', 'see-more-container')
  html = html.find('div', 'col-xs-8 right-border').renderContents()
  if seeMore != None:
    html = html.replace(seeMore.renderContents(), '')
  showList(html, urlId)


# Entry point.
#startTime = datetime.datetime.now()

handle = int(sys.argv[1])
params = tools.urlParametersToDict(sys.argv[2])
idPlugin = 'plugin.serviziopubblico'

if len(params) == 0: # Visualizzazione del menu.
  categs = []
  categs.append(['Santoro', 'r', 'http://www.serviziopubblico.it/canali/santoro'])
  categs.append(['Vauro', 'r', 'http://www.serviziopubblico.it/canali/vauro'])
  categs.append(['Travaglio', 'r', 'http://www.serviziopubblico.it/canali/travaglio'])
  categs.append(['Dragoni', 'r', 'http://www.serviziopubblico.it/canali/dragoni'])
  categs.append(['Puntate', 'e', 'http://www.serviziopubblico.it/puntate'])
  categs.append(['Argomenti', 't', 'http://www.serviziopubblico.it/argomenti'])
  categs.append(['Gli inviati', 'n', 'http://www.serviziopubblico.it/gli-inviati'])
  for title, paramId, page in categs:
    tools.addDir(handle, title, '', '', 'video', { 'title' : title, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : paramId, 'page' : page })
  xbmcplugin.endOfDirectory(handle)
else:
  response = tools.getBSResponseUrl(params['page'])
  if response != None:
    if params['id'] == 'i': # Archivi (santoro, vauro, travaglio, dragoni e argomenti)
      showArchiveList(response, params['id'])
    elif params['id'] == 'e': # Puntate.
      response = response.find('div', 'col-md-8 right-border')
      showList(response.renderContents(), params['id'])
    elif params['id'] == 't': # Argomenti.
      response = response.renderContents()
      categs = re.compile('<div class="col-sm-12 single-argomento"> <a href="(.+?)" title="(.+?)".+?<img.+?src="(.+?)".+?<div class="post-content">(.+?)</div>').findall(response)
      for link, title, img, descr in categs:
        title = tools.normalizeText(title)
        if title.lower().find('fatto quotidiano') == -1:
          tools.addDir(handle, title, normalizeImage(img), '', 'video', { 'title' : title, 'plot' : tools.normalizeText(tools.stripTags(descr)), 'duration' : -1, 'director' : '' }, { 'id' : 'r', 'page' : createPage(link) })
      showNextPage(response, params['id'])
      xbmcplugin.endOfDirectory(handle)
    elif params['id'] == 'n': # Gli inviati.
      response = re.compile('<div class="post-[0-9]+ persone.+?">.+?<a href="(.+?)" title="(.+?)"> <img.+?src="(.+?)"').findall(response.renderContents())
      for link, title, img in response:
        title = tools.normalizeText(title)
        tools.addDir(handle, title, normalizeImage(img), '', 'video', { 'title' : title, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : 'e', 'page' : createPage(link) })
      xbmcplugin.endOfDirectory(handle)
    elif params['id'] == 'r': # Ricerca categID.
      categid = re.compile('\?cat_id=([0-9]+)"').findall(response.renderContents())[0]
      response = tools.getBSResponseUrl(createCategPage(categid))
      if response != None:
        showArchiveList(response, 'i')
    elif params['id'] == 'v': # Riproduzione del video.
      response = response.renderContents()
      urlParam = re.compile('<div class="meride-video-container" data-embed="(.+?)" data-customer="(.+?)" data-nfs="(.+?)"').findall(response)
      if len(urlParam) > 0:
        urlParam = urlParam[0]
        tide = re.compile('<h3 class="entry-title">(.+?)</h3>.+?<p>(.+?)</p>').findall(response)[0]
        response = tools.getResponseUrl('http://mediasp.meride.tv/embedproxy.php/' + urlParam[1] + '/folder1/' + urlParam[0] + '/desktop')
        if response != None:
          urls = re.compile('<video.+?<iphone><!\[CDATA\[(.+?)]]></iphone><mp4><!\[CDATA\[(.+?)]]></mp4><poster><!\[CDATA\[(.+?)]]></poster>').findall(response)[0]
          title = tools.normalizeText(tide[0])
          li = tools.createListItem(title, urls[2], '', 'video', { 'title' : title, 'plot' : tools.normalizeText(tools.stripTags(tide[1])), 'duration' : -1, 'director' : '' })
          try:
            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream(urls[0], li)
          except:
            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream(urls[1], li)
      else: # Messaggio d'errore "Video non disponibile".
        xbmcgui.Dialog().ok('Servizio Pubblico', tools.getTranslation(idPlugin, 30002))

#print 'Servizio pubblico azione ' + str(datetime.datetime.now() - startTime)
