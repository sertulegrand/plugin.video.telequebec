# -*- coding: cp1252 -*-

""" -*- coding: utf-8 -*- """
# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB
#
# pylint...: --max-line-length 120
# vim......: set expandtab
# vim......: set tabstop=4
#

import sys,urllib, xbmcgui, xbmcplugin, xbmcaddon,re,cache, simplejson, xbmc

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'

__handle__ = int(sys.argv[1])

def ajouterItemAuMenu(items):
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATE)
    
    for item in items:
        if item['isDir'] == True:
            ajouterRepertoire(item)
            
        else:
            ajouterVideo(item)
            xbmc.executebuiltin('Container.SetViewMode('+str(xbmcplugin.SORT_METHOD_DATE)+')')
            xbmc.executebuiltin('Container.SetSortDirection(0)')



def ajouterRepertoire(show):

    nom = show['nom']
    url = show['url']
    iconimage =show['image']
    genreId = show['genreId']
    resume = remove_any_html_tags(show['resume'])
    fanart = show['fanart']
    filtres = show['filtres']

    if resume=='':
        resume = urllib.unquote(ADDON.getAddonInfo('id')+' v.'+ADDON.getAddonInfo('version'))
    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
        resume = '[B]'+nom+'[/B][CR]'+urllib.unquote(resume)
    if iconimage=='':
        iconimage = ADDON_IMAGES_BASEPATH+'default-folder.png'

    """ function docstring """
    entry_url = sys.argv[0]+"?url="+url+\
        "&mode=1"+\
        "&filters="+urllib.quote(simplejson.dumps(filtres))
  
    is_it_ok = True
    liz = xbmcgui.ListItem(nom,iconImage=iconimage,thumbnailImage=iconimage)

    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title": nom,\
            "plot":resume
        }\
    )
    setFanart(liz,fanart)

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=True)

    return is_it_ok

def setFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)


def ajouterVideo(show):
    name = show['nom']
    the_url = show['url']
    iconimage = show['image']
    url_info = 'none'
    finDisponibilite = show['endDateTxt']

    resume = remove_any_html_tags(show['resume'] +'[CR][CR]' + finDisponibilite)
    duree = show['duree']
    fanart = show['fanart']
    sourceId = show['sourceId']
    annee = show['startDate'][:4]
    premiere = show['startDate']
    episode = show['episodeNo']
    saison = show['seasonNo']
    


    is_it_ok = True
    entry_url = sys.argv[0]+"?url="+urllib.quote_plus(the_url)+"&sourceId="+(sourceId)

    if resume != '':
        if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
            resume = '[B]'+name.lstrip()+'[/B]'+'[CR]'+resume.lstrip() 
    else:
        resume = name.lstrip()

    liz = xbmcgui.ListItem(\
        remove_any_html_tags(name), iconImage=ADDON_IMAGES_BASEPATH+"default-video.png", thumbnailImage=iconimage)
    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title":remove_any_html_tags(name),\
            "Plot":remove_any_html_tags(resume, False),\
            "Duration":duree,\
            "Year":annee,\
            "Premiered":premiere,\
            "Episode":episode,\
            "Season":saison}\
    )
    liz.addContextMenuItems([('Informations', 'Action(Info)')])
    setFanart(liz,fanart)
    liz.setProperty('IsPlayable', 'true')

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
    return is_it_ok

RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')

def jouer_video(media_uid):
    """ function docstring """
    check_for_internet_connection()
    
    # Obtenir JSON avec liens RTMP du playlistService
    video_json = simplejson.loads(\
        cache.get_cached_content(\
            'http://production.ps.delve.cust.lldns.net/r/PlaylistService/media/%s/getPlaylistByMediaId' % media_uid\
        )\
    )
    
    # Preparer list de videos à jouer
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()

    # Analyser chaque stream disponible pour trouver la meilleure qualité
    #for play_list_item in video_json['playlistItems']:
    play_list_item =video_json['playlistItems'][0]
    
    highest_bit_rate = 0
    stream_url = None
    for stream in play_list_item['streams']:
        if stream['videoBitRate'] > highest_bit_rate:
            highest_bit_rate = stream['videoBitRate']
            stream_url = stream['url']
    if stream_url:
        # Générer un lien compatible pour librtmp
        # rtmp_url - play_path - swf_url
        url_final = '%s playPath=%s swfUrl=%s swfVfy=true' % (\
            stream_url[:stream_url.find('mp4')],\
            stream_url[stream_url.find('mp4'):],\
            'http://s.delvenetworks.com/deployments/flash-player/flash-player-5.10.1.swf?playerForm=Chromeless'\
        )
       # log('Starting playback of :' + urllib.quote_plus(url_final))
        item = xbmcgui.ListItem(\
            video_json['title'],\
            iconImage=video_json['imageUrl'],\
            thumbnailImage=play_list_item['thumbnailImageUrl'], path=url_final)
        #playlist.add(url_final, item)
        play_item = xbmcgui.ListItem(path=url_final)
        xbmc.log("**************************************DING? " +sys.argv[0])
        xbmcplugin.setResolvedUrl(__handle__,True, item)
        xbmc.log("**************************************DONG! ")
    else:
        xbmc.executebuiltin('Notification(%s,Incapable d''obtenir lien du video,5000,%s' % (ADDON_NAME, ADDON_ICON))

    #if playlist.size() > 0:
    #    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(playlist)
   

def check_for_internet_connection():
    """ function docstring """
    if ADDON.getSetting('NetworkDetection') == 'false':
        return
   #retire cb
    
   # if html.is_network_available(parseTQ.BASE_URL) == False:
   #     xbmcgui.Dialog().ok(\
   #         ADDON_NAME,\
   #         ADDON.getLocalizedString(32112),\
   #         ADDON.getLocalizedString(32113)\
   #     )
   #     exit()
    return

def remove_any_html_tags(text, crlf=True):
    """ function docstring """
    text = RE_HTML_TAGS.sub('', text)
    text = text.lstrip()
    if crlf == True:
        text = RE_AFTER_CR.sub('', text)
    return text
