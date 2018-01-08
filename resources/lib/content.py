# -*- coding: utf-8 -*-

# version 3.1.3 - Par CB

import urllib2, simplejson, parse, cache, re, xbmcaddon,xbmc

BASE_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/'
AZ_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/Az'
DOSSIERS_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/folders'
POPULAIRE_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/populars/'

MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

SEASON = 'Saison'
EPISODE = 'Episode'
LABEL = 'label'
FILTRES = '{"content":{"genreId":"","mediaBundleId":-1},"show":{"' + SEASON + '":"","' + EPISODE + '":"","' + LABEL + '":""},"fullNameItems":[],"sourceId":""}'
INTEGRAL = 'Integral'


def dictOfGenres(filtres):
    liste =[]
    liste.append({'genreId': 0, 'nom': '[B]A %C3%A0 Z - Toutes les cat%C3%A9gories[/B]','resume':'Tout le contenu disponible.'})
    liste.append({'genreId': 1, 'nom': 'Documentaires','resume':'Les documentaires.'})
    liste.append({'genreId': 2, 'nom': 'Famille', 'resume':'Pour toute la famille.'})
    liste.append({'genreId': 3, 'nom': 'Films','resume':'Les films.'})
    liste.append({'genreId': 6, 'nom': 'Jeunesse - tout-petits','resume':'Pour les petits.'})
    liste.append({'genreId': 4, 'nom': 'Jeunesse - grands','resume':'Pour les plus grands.'})
    liste.append({'genreId': 5, 'nom': 'Jeunesse - plus grands','resume':'Pour les vraiment grands.'})
    liste.append({'genreId': 7, 'nom': 'Magazines','resume':'Les magasines.'})
    liste.append({'genreId': 9, 'nom': 'S%C3%A9ries de fiction','resume':'La fiction.'})
    liste.append({'genreId': 10, 'nom': 'Vari%C3%A9t%C3%A9s','resume':'Pour se divertir.'})

    for item in liste :
        item['isDir']= True
        item['nom']= urllib2.unquote(item['nom'])
        item['url'] = AZ_URL
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres'] = parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']

    return liste

def dictOfMainDirs(filtres):
    liste = []

    liste.append({'genreId': -2, 'nom': '[B]Populaires[/B]', 'url' : POPULAIRE_URL,'resume':'Les videos populaires du moment.'})
    liste.append({'genreId': -1, 'nom': '[B]Dossiers[/B]', 'url': DOSSIERS_URL,'resume':'Des segments abordant un sujet commun.'})

    for item in liste :
        item['isDir']= True
        item['nom']= urllib2.unquote(item['nom'])
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres']= parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item['filtres']['show']={}
        item['filtres']['fullNameItems'].append('nomDuShow')        
    return liste

def dictOfPopulaires(filtres):
    liste=[{'genreId': -21, 'nom': 'Populaires en ce moment', 'url' : 'Day/','resume':'Les videos populaires en ce moment.'}]
    liste.append({'genreId': -22, 'nom': 'Populaires cette semaine', 'url' :'Week/','resume':'Les videos populaires cette semaine.'})
    liste.append({'genreId': -23, 'nom': 'Populaires depuis 1 mois', 'url' : 'Month/','resume':'Les videos populaires depuis 1 mois.'})
    for item in liste :
        item['isDir']= True
        item['nom']= urllib2.unquote(item['nom'])
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres']= parse.getCopy(filtres)
        item['filtres']['content']['genreId'] = item['genreId']
        item['filtres']['content']['url'] = item['url']
        item['filtres']['show']={}
        item['filtres']['fullNameItems'].append('nomDuShow')        
    return liste

    
def formatListe(liste, filtres):
    newListe = []
    for item in liste:
        print item.keys()
        newItem = {}
        newItem['isDir'] = True
        newItem['nom'] = item['view']['title']
        newItem['mediaBundleId'] = item['mediaBundleId']
        newItem['url'] = MEDIA_BUNDLE_URL + str(item['mediaBundleId'])
        newItem['image'] = getThumbnails(item)
        newItem['genreId'] = ''
        newItem['nomComplet'] = item['view']['title']
        newItem['resume'] = item['view']['description']
        newItem['fanart'] = getFanArt(item)
        newItem['filtres'] = parse.getCopy(filtres)
        newItem['filtres']['content']['mediaBundleId'] = item['mediaBundleId']
        newListe.append(newItem)

    return newListe
def get_liste_populaire(filtres):
    show = getLinkPop(filtres['content']['url'])
    items = show['items']

    newListe = []
    for episode in items:
        logjson(episode)
        newItem = {}
        newItem['isDir'] = False
        newItem[LABEL] = 'Contenu'
        newItem['categoryType'] = episode['categoryType']
        newItem['url'] = episode['permalink']
        newItem['image'] = getThumbnails(episode)
        newItem['genreId'] = ''
        newItem['nomComplet'] = episode['view']['title']
        newItem['resume'] = episode['view']['description']

        try:
             newItem[SEASON] = episode['view']['season'].encode('utf-8','ignore')
        except Exception:
             newItem[SEASON] =''
        
        newItem['duree'] = episode['duration']/1000
        newItem['seasonNo'] = newItem[SEASON]
        
        try:
            newItem['episodeNo'] =episode['view']['episode'].encode('utf-8','ignore')
        except Exception:
            newItem['episodeNo'] =''
            
        newItem['startDate'] = episode['startDate']
        newItem['endDate'] = episode['endDate']
        newItem['endDateTxt'] = episode['view']['endDate']


        newItem['streamInfo'] = episode['streamInfo']

        newItem['nomDuShow'] =  episode['view']['containerTitle']
        
        newItem['sourceId'] = episode['streamInfo']['sourceId']
        newItem[EPISODE] = str(newItem['episodeNo'])
        newItem['fanart'] = getImage(episode['view']['thumbImg'],'1280','720')
        newItem['nom'] = ''

        newItem['nom'] = episode['view']['containerTitle'] + ' - ' + episode['view']['title']
        newListe.append(newItem)

    return newListe
    
def getListeOfVideo(mediaBundleId, filtres):
    show = getShow(mediaBundleId)
    fanart_url = getFanArt(show)
    mainShowName = show['view']['title']
    
    newListe = []
    for bloc in show['mediaGroups']:
        if bloc['label'] == None:
            nomBloc = 'Contenu'
        else:
            nomBloc = bloc['label']
        
        for episode in bloc['medias']:
            newItem = {}
            newItem['isDir'] = False
            newItem[LABEL] = nomBloc
            newItem['categoryType'] = episode['categoryType']
            newItem['url'] = episode['permalink']
            newItem['image'] = getThumbnails(episode)
            newItem['genreId'] = ''
            newItem['nomComplet'] = episode['view']['title']
            newItem['resume'] = episode['view']['description']
            newItem[SEASON] = 'Saison ' + str(episode['seasonNo'])
            newItem['duree'] = episode['duration']/1000

            
            newItem['seasonNo'] = episode['seasonNo']
            newItem['episodeNo'] =episode['episodeNo']
            newItem['startDate'] = episode['startDate']
            newItem['endDate'] = episode['endDate']
            newItem['endDateTxt'] = episode['view']['endDate']


            newItem['streamInfo'] = episode['streamInfo']

            newItem['nomDuShow'] = mainShowName
            
            newItem['sourceId'] = episode['streamInfo']['sourceId']
            newItem[EPISODE] = 'Episode ' + str(episode['episodeNo']).zfill(2)
            newItem['fanart'] = fanart_url
            newItem['nom'] = ''

            for tag in filtres['fullNameItems']:
                newItem['nom'] = newItem['nom'] + newItem[tag] + ' - '


            newItem['nom'] = newItem['nom'] + episode['view']['title']
            newListe.append(newItem)

    return newListe

def get_liste_emissions(filtres):
    liste = get_liste(filtres['content']['genreId'])
    return formatListe(liste, filtres)

def get_liste(categorie):
    if categorie >= 0:
        liste = getJsonBlock(AZ_URL, 0)
        if categorie == 0:
            return liste
        listeFiltree = []
        for show in liste:
            if isGenre(categorie, show):
                listeFiltree.append(show)

        return listeFiltree
    if categorie == -1:
        return getJsonBlock(DOSSIERS_URL, 1)
    if categorie == -2:
        return getJsonBlock(POPULAIRE_DAY,1)['data'][0]['items']
    return {}

def isGenre(genreValue, show):
    genres = show['genres']
    for genre in genres:
        if genre['genreId'] == genreValue:
            return True

    return False

def isIntegral(show):
    if show['categoryType']==INTEGRAL:
        return True
    else:
        return False

def getThumbnails(show):
    return getImage(show['view']['thumbImg'], '320','180')

def getFanArt(show):
    return getImage(show['view']['headerImg'],'1280','720')

def getImage(url,width,height):
    link = re.sub('{w}', width, url)
    link = re.sub('{h}', height, link)
    return link
    
def getShow(mediaBundleId):
    database = simplejson.loads(cache.get_cached_content(MEDIA_BUNDLE_URL + str(mediaBundleId)))
    return database['data']

def getLinkPop(url):
    database = simplejson.loads(cache.get_cached_content(POPULAIRE_URL + str(url)))
    return database['data'][0]

def getJsonBlock(url, block):
    dataBlock = []
    try:
        db = simplejson.loads(cache.get_cached_content(url))
        dataBlock = db['data'][block]['items']
    except Exception:
        dataBlock = []
    return dataBlock

def logjson(json):
    xbmc.log(simplejson.dumps(json, sort_keys=True,indent=4, separators=(',', ': ')))

