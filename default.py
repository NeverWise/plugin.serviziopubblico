#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 1.0.0 (24/11/2013)
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
import sys, re, xbmcplugin, tools#, datetime


def CreateLink(idCateg):
  link = 'http://www.serviziopubblico.it/articolo/dettaglio/3956/page/1?cat_id=' + idCateg
  if idCateg == '2': # Per evitare di mangiarsi un video adotto questo barbatrucco.
    link = 'http://www.serviziopubblico.it/articolo/dettaglio/3910/page/1?cat_id=2'
  return link


def getCategIdFromLink(link):
  index = link.rfind('=') + 1
  result = None
  if index > 0: result = link[index:]
  return result


def showNextPageDir(inputString, pattern, idParams):
  nextPage = re.compile(pattern).findall(inputString)
  if len(nextPage) > 0:
    title = tools.getTranslation(idPlugin, 30001) + ' ' + nextPage[0][1] + ' >' # Pagina.
    tools.addDir(handle, title, '', '', 'video', { 'title' : title, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : idParams, 'page' : nextPage[0][0] })


# Entry point.
#startTime = datetime.datetime.now()

handle = int(sys.argv[1])
params = tools.urlParametersToDict(sys.argv[2])
idPlugin = 'plugin.serviziopubblico'

if len(params) == 0: # Visualizzazione del menu.
  response = tools.getResponseUrl('http://www.serviziopubblico.it')
  menu = re.compile('<nav class="menu-principale">(.+?)</nav>').findall(response)
  if len(menu) > 0: # Menù standard.
    menu = re.compile('<a title="(.+?)" href="(.+?)">').findall(menu[0])
    for name, link in menu:
      name = tools.normalizeText(name)
      paramId = 's'
      if link.find('/argomenti') > -1:
        paramId = 'f'
      categId = getCategIdFromLink(link)
      if categId != None:
        link = CreateLink(categId)
      tools.addDir(handle, name, '', '', 'video', { 'title' : name, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : paramId, 'page' : link })
  else: # Al giovedì il menù standard non è più accessibile ed è sostituito con la diretta.
    img = re.compile('<meta property="og:image" content="(.+?)"/>').findall(response)[0]
    descr = re.compile('<meta property="og:description" content="(.+?)"/>').findall(response)[0]
    descr += ' ' + re.compile('<div class="ospiti-puntata"><h1>(.+?)</h1>').findall(response)[0] + ':'
    guests = re.compile('<td><img class="lazy" title="(.+?)" alt="').findall(response)
    for guest in guests:
      descr += ' ' + guest + ','
    descr = descr[:-1] + '.'
    url = re.compile('<input type="hidden" id="url_streaming_iphone" value="(.+?)"/>').findall(response)[0]
    #url = 'http://splive_hls-lh.akamaihd.net/i/spbak2_1@146270/master.m3u8'
    tools.addLink(handle, tools.getTranslation(idPlugin, 30002), img, '', 'video', { 'title' : 'Servizio Pubblico', 'plot' : tools.normalizeText(descr), 'duration' : -1, 'director' : '' }, url) # Diretta.
  xbmcplugin.endOfDirectory(handle)
else:
  response = tools.getResponseUrl(params['page'])
  pages = re.compile('<p class="pagination">(.+?)</p>').findall(response)[0]
  if params['id'] == 'f': # Argomenti.
    categs = re.compile('<div class="canale-evidenza"><div class="main-titolo-canale-evidenza"><a.+?href="(.+?)">(.+?)</a></div><div class="immagine-canale-evidenza"><img.+?src="(.+?)"/></div><div class="titolo-canale-evidenza"><a.+?>(.+?)</a></div><div class="sottotitolo-canale-evidenza">(.+?)</div>').findall(response)
    for link, title, img, descr, descr2 in categs:
      categId = getCategIdFromLink(link)
      if categId != '38': # Esclusione dei video del fatto quotidiano.
        title = tools.normalizeText(title)
        descr = tools.normalizeText(tools.stripTags(descr)) + '\r\n' + tools.normalizeText(tools.stripTags(descr2))
        tools.addDir(handle, title, img, '', 'video', { 'title' : title, 'plot' : descr, 'duration' : -1, 'director' : '' }, { 'id' : 's', 'page' : CreateLink(categId) })
    showNextPageDir(pages, '</strong><a href="(.+?)>(.+?)</a>', 'f')
    xbmcplugin.endOfDirectory(handle)
  elif params['id'] == 's': # Video di una sezione e puntate.
    categId = getCategIdFromLink(params['page'])
    regExPage = '</strong><a href="(.+?)>(.+?)</a>'
    if categId == None:
      regExPage = '<a class="active" href=".+?">.+?</a> - <a href="(.+?)">(.+?)</a>'
    videos = re.compile('<article class="elenco-categoria"><div class="immagine"><a.+? href="(.+?)"><img class="lazy".+? src="(.+?)"/></a></div><div class="contenuto-elenco-categoria"><div class="titolo"><h3><a.+?>(.+?)</a></h3></div><div class="descrizione">(.+?)</div>').findall(response)
    for link, img, title, descr in videos:
      img = img.replace('thumbs/', '')
      title = tools.normalizeText(title)
      descr = tools.normalizeText(tools.stripTags(descr))
      tools.addDir(handle, title, img, '', 'video', { 'title' : title, 'plot' : descr, 'duration' : -1, 'director' : '' }, { 'id' : 'v', 'page' : link })
    showNextPageDir(pages, regExPage, 's')
    xbmcplugin.endOfDirectory(handle)
  elif params['id'] == 'v': # Riproduzione del video.
    img = re.compile('<meta property="og:image" content="(.+?)"/>').findall(response)[0]
    url = re.compile('data-url-iphone="(.+?)"').findall(response)[0]
    title = re.compile('<div class="titolo" id="titolo-articolo"><h1>(.+?)</h1>').findall(response)[0]
    descr = re.compile('<div class="descrizione-dettaglio" id="descrizione-articolo">(.+?)</div>').findall(response)[0]
    li = tools.createListItem(title, img, '', 'video', { 'title' : title, 'plot' : tools.normalizeText(tools.stripTags(descr)), 'duration' : -1, 'director' : '' })
    xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream(url, li)

#print 'Servizio pubblico azione ' + str(datetime.datetime.now() - startTime)
