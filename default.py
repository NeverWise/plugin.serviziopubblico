#!/usr/bin/python
import neverwise as nw, os, subprocess, sys, xbmcplugin#, datetime


class ServizioPubblico(object):

  _handle = int(sys.argv[1])
  _params = nw.urlParametersToDict(sys.argv[2])
  _fanart = nw.addon.getAddonInfo('fanart')

  def __init__(self):

    # Visualizzazione del menu.
    if len(self._params) == 0:
      li = nw.createListItem('In primo piano', fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : 'In primo piano' })
      xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'f' }), li, True)
      li = nw.createListItem('Canali', fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : 'Canali' })
      xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'c' }), li, True)
      xbmcplugin.endOfDirectory(self._handle)
    elif self._params['action'] == 'f':
      response = self._getSPResponse('get_oggi_su_sp')
      self._showArticles(response)

    elif self._params['action'] == 'c':
      response = self._getSPResponse('get_canali_fissi')
      if response.isSucceeded:

        for canale in response.body['canali']:
          img = self._normalizeImage(canale['url_thumb2'])
          li = nw.createListItem(canale['titolo'], thumbnailImage = img, fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : canale['titolo'], 'plot' : canale['descrizione'] })
          xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'a', 'id' : canale['id'] }), li, True)

        xbmcplugin.endOfDirectory(self._handle)

    elif self._params['action'] == 'a':
      response = self._getSPResponse('search_articoli/?canale_id={0}&limit=500'.format(self._params['id']))
      self._showArticles(response)

    elif self._params['action'] == 'd':
      name = os.path.basename(self._params['id'])
      name_parts = os.path.splitext(name)
      if 'm3u' in name_parts[1]:
        name = '{0}.ts'.format(name_parts[0])
      #~ subprocess.call([nw.addon.getSetting('ffmpeg_path'), '-i', self._params['id'], '-c', 'copy', name])
      subprocess.Popen([nw.addon.getSetting('ffmpeg_path'), '-i', self._params['id'], '-c', 'copy', name])


  def _getSPResponse(self, route):
    return nw.getResponseJson('http://spwps.meride.tv/ws/{0}'.format(route))


  def _normalizeImage(self, image):
    return image.replace('http://www.serviziopubblico.ithttp', 'http')


  def _showArticles(self, response):
    if response.isSucceeded:
      haveFFmpeg = os.path.isfile(nw.addon.getSetting('ffmpeg_path')) and os.path.isdir(nw.addon.getSetting('download_path'))
      for articolo in response.body['articoli']:
        title = u'{0} ({1})'.format(articolo['nome'], articolo['data_creazione'])
        img = self._normalizeImage(articolo['url_thumb2'])
        cm = None
        if haveFFmpeg:
          cm = nw.getDownloadContextMenu('RunPlugin({0})'.format(nw.formatUrl({ 'action' : 'd', 'id' : articolo['url_video'] })), title)
        li = nw.createListItem(title, thumbnailImage = img, fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : title, 'plot' : articolo['contenuto'] }, isPlayable = True, contextMenu = cm)
        xbmcplugin.addDirectoryItem(self._handle, articolo['url_video'], li)

      xbmcplugin.endOfDirectory(self._handle)


# Entry point.
#startTime = datetime.datetime.now()
sp = ServizioPubblico()
del sp
#xbmc.log('{0} azione {1}'.format(nw.addonName, str(datetime.datetime.now() - startTime)))
