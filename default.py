# -*- coding: cp1252 -*-
import urllib,urllib2,re,xbmcplugin,xbmcaddon,xbmcgui,xbmc,simplejson

# version 2.5
#By CB

TELEQUEBEC_BASE_URL = 'http://zonevideo.telequebec.tv'

#Merci à l'auteur de cette fonction
def unescape_callback(matches):
	html_entities = {
		'quot':'\"', 'amp':'&', 'apos':'\'', 'lt':'<', 'gt':'>', 'nbsp':' ', 'copy':'©', 'reg':'®',
		'Agrave':'À', 'Aacute':'Á', 'Acirc':'Â', 'Atilde':'Ã', 'Auml':'Ä', 'Aring':'Å', 'AElig':'Æ',
		'Ccedil':'Ç', 'Egrave':'È', 'Eacute':'É', 'Ecirc':'Ê', 'Euml':'Ë', 'Igrave':'Ì', 'Iacute':'Í',
		'Icirc':'Î', 'Iuml':'Ï', 'ETH':'Ð', 'Ntilde':'Ñ', 'Ograve':'Ò', 'Oacute':'Ó', 'Ocirc':'Ô',
		'Otilde':'Õ', 'Ouml':'Ö', 'Oslash':'Ø', 'Ugrave':'Ù', 'Uacute':'Ú', 'Ucirc':'Û', 'Uuml':'Ü',
		'Yacute':'Ý', 'agrave':'à', 'aacute':'á', 'acirc':'â', 'atilde':'ã', 'auml':'ä', 'aring':'å',
		'aelig':'æ', 'ccedil':'ç', 'egrave':'è', 'eacute':'é', 'ecirc':'ê', 'euml':'ë', 'igrave':'ì',
		'iacute':'í', 'icirc':'î', 'iuml':'ï', 'eth':'ð', 'ntilde':'ñ', 'ograve':'ò', 'oacute':'ó',
		'ocirc':'ô', 'otilde':'õ', 'ouml':'ö', 'oslash':'ø', 'ugrave':'ù', 'uacute':'ú', 'ucirc':'û',
		'uuml':'ü', 'yacute':'ý', 'yuml':'ÿ'
	}

	entity = matches.group(0)
	val = matches.group(1)

	try:
		if entity[:2] == '\u':
			return entity.decode('unicode-escape')
		elif entity[:3] == '&#x':
			return unichr(int(val, 16))
		elif entity[:2] == '&#':
			return unichr(int(val))
		else:
			return html_entities[val].decode('utf-8')

	except (ValueError, KeyError):
		pass

def HTMLUnescape(data):
	data = data.decode('utf-8')
	data = re.sub('&#?x?(\w+);|\\\\u\d{4}', unescape_callback, data)
	data = data.encode('utf-8')

	return data

def rechercherUnElement(argument, rechercherDans):
        reponse = re.compile(argument, re.DOTALL).search(rechercherDans)
        if(reponse):
                return reponse.group(1)
        else:
                return ""

def getURLtxt(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Accept-Charset', 'utf-8')
        response = urllib2.urlopen(req)
        link=response.read()
        link = HTMLUnescape(link)
        response.close()
        return link

def getBlock(url):
        link = getURLtxt(url)
        main = rechercherUnElement('content index(.+?)<footer>',link)
        return main
def getCategories(url):
        main = getBlock(url)
        match=re.compile('<option value="(.+?)">(.+?)</option>',re.DOTALL).findall(main)
        return match

def getListeEmissions(url):
        main = getBlock(url)
        match=re.compile('<li data-genre="(.+?)"><a href="(.+?)">(.+?)</a></li>',re.DOTALL).findall(main)
        return match

def comparerCategorie(categorieVoulue, listeCategorie):
        if categorieVoulue == '0' : return 1
        match=re.split(';',listeCategorie)
        for catListee in match:
                if catListee==categorieVoulue:
                        return 1
        return 0

def trouverInfosEmission(url):
       link = getURLtxt(url)

       main = rechercherUnElement('<article class="emission">(.+?)</article>',link)

       sub= rechercherUnElement('class="emissionHeader"(.+?)</div>',main)

       icon = rechercherUnElement('img src="(.+?)"',sub)

       sub2= rechercherUnElement('class="emissionInfo"(.+?)</div>',main)

       resume = rechercherUnElement('<p>(.+?)</p>',sub2)

       return [icon,resume]


def creerMenuCategories():
        urlAZ = TELEQUEBEC_BASE_URL+'/a-z/'
        nomCategories = getCategories(urlAZ)
        for numberCat,nomCat in nomCategories:
                if numberCat<>'All':
                        addDir(nomCat,urlAZ,1,'',numberCat,0)
        addDir('Tous les genres',urlAZ,1,'','0',0)
        addDir('- Populaires -',TELEQUEBEC_BASE_URL+'/populaires/',2,'','0',1)
        addDir('- Dossiers -',TELEQUEBEC_BASE_URL+'/dossiers/',6,'','0',1)
        addDir('- R%C3%A9cents -',TELEQUEBEC_BASE_URL,2,'','0',1)

def creerListeFiltree(categorieVoulue,url):
        liste = getListeEmissions(url)
        for categ,lien,titre in liste:
                if comparerCategorie(str(categorieVoulue),categ)==1:
                        elementsInformations = trouverInfosEmission(TELEQUEBEC_BASE_URL+lien)
                        addEmission(titre,TELEQUEBEC_BASE_URL+lien,elementsInformations[0],elementsInformations[1])

def creerDossiers(url):
		link = getURLtxt(url)
		container = re.split('<div class="listItem floatContainer">',link)
		liste = re.split('<div class="item"',container[1])
		for item in liste:
			sub2 = re.compile('<div class="info">(.+?)</div>',re.DOTALL).findall(item)
			if len(sub2)>0:
				sub2=sub2[0]
				urlDossier = rechercherUnElement('href="(.+?)">',sub2)
				nomDossier = rechercherUnElement('<a(?:.+?)>(.+?)</a>',sub2)
				icon = rechercherUnElement('src="(.+?)"',item)
				#infos = trouverInfosEpisode(TELEQUEBEC_BASE_URL+urlEpisode)
				addEmission(nomDossier,TELEQUEBEC_BASE_URL+urlDossier,icon,'')

def creerListeVideos(url):
       link = getURLtxt(url)
       nbSaisons=creerListeSaisons(link)
       nbSaisons=creerListeSupplement(link,nbSaisons)


def creerListeSaisons(link):
       nbSaisons = 0
       sub = rechercherUnElement('<ul class="menu(.+?)</ul>',link)
       match = re.compile('<li(.+?)</li>',re.DOTALL).findall(sub)
       for saisonTxt in match:
               nbSaisons = nbSaisons+1
               nomSaison = rechercherUnElement('<a.*?>(.+?)</a>',saisonTxt)
               addDirSaison(nomSaison,url,'',nbSaisons)
       if nbSaisons==0:
               creerListeEpisodes(url,1,fullName)
       return nbSaisons


def creerListeSupplement(link,nbSaisons):
        main = re.compile('class="extrasEmission"(.+?)</section>',re.DOTALL).findall(link)
        for extra in main:
                nbSaisons = nbSaisons+1
                titre = rechercherUnElement('<h2.*?<span>(.+?)</span>',link)
                addDirSaison(titre,url,'',nbSaisons)
        return nbSaisons

def creerListeEpisodes(url,saison,nomComplet):
        link = getURLtxt(url)
        containerSaison = re.split('<div class="listItem floatContainer">',link)
        if len(containerSaison)<saison:
                debugPrint('Probleme de scraper de saisons')
        else:
                 liste = re.split('<div class="item"',containerSaison[saison])
                 for item in liste:
                        sub2 = re.compile('<div class="info">(.+?)</div>',re.DOTALL).findall(item)
                        if len(sub2)>0:
                                sub2=sub2[0]
                                urlEpisode = rechercherUnElement('href="(.+?)">',sub2)
                                nomEmission = rechercherUnElement('<p(?:.+?)>(.+?)</p>',sub2)
                                nomEpisode = rechercherUnElement('<a(?:.+?)>(.+?)</a>',sub2)
                                icon = rechercherUnElement('src="(.+?)"',item)
                                dureeBlock = rechercherUnElement('"infoSaison"(.+?)</p>',item)
                                duree = rechercherUnElement('(..:..)',dureeBlock)
                                #duree = (str(int(duree[0])*60+int(duree[1])))
                                #infos = trouverInfosEpisode(TELEQUEBEC_BASE_URL+urlEpisode)
                                if (nomComplet==1):
                                       addLink(nomEmission+' : '+nomEpisode,TELEQUEBEC_BASE_URL+urlEpisode,icon,'','',duree)
                                else:
                                       addLink(nomEpisode,TELEQUEBEC_BASE_URL+urlEpisode,icon,'','',duree)

def trouverInfosEpisode(url):
       link = getURLtxt(url)
       icon = rechercherUnElement('<meta itemprop="image" content="(.+?)">',link)
       description = rechercherUnElement('<meta name="description" content="(.+?)>',link)

       return [icon,description]

def JOUERVIDEO(url,name,url_info):
        link = getURLtxt(url)

        #Obtenir mediaUID pure de l'émission
        mediaUID = rechercherUnElement('mediaUID: \'Limelight_(.+?)\'',link)

        #Obtenir JSON avec liens RTMP du playlistService
        link = getURLtxt('http://production.ps.delve.cust.lldns.net/r/PlaylistService/media/%s/getPlaylistByMediaId' % mediaUID)
        videoJSON = simplejson.loads(link)

        #Preparer list de videos à jouer
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

        #Analyser chaque stream disponible pour trouver la meilleure qualité
        for playlistItem in videoJSON['playlistItems']:
            highestBitRate = 0
            streamURL = None
            for stream in playlistItem['streams']:
                if stream['videoBitRate'] > highestBitRate:
                    highestBitRate = stream['videoBitRate']
                    streamURL = stream['url']

            if streamURL:
                #Séparer le lien en RTMP et PLAYPATH
                rtmpUrl = streamURL[:streamURL.find('mp4')]
                playPath = streamURL[streamURL.find('mp4'):]

                #Générer un lien compatible pour librtmp
                swfUrl = 'http://s.delvenetworks.com/deployments/flash-player/flash-player-5.10.1.swf?playerForm=Chromeless'
                url = '%s playPath=%s swfUrl=%s swfVfy=true' % (rtmpUrl, playPath, swfUrl)

                xbmc.log('Starting playback of %s' % url)
                item = xbmcgui.ListItem(videoJSON['title'],iconImage=videoJSON['imageUrl'],thumbnailImage=videoJSON['imageUrl'])
                playlist.add(url, item)
            else:
                xbmc.executebuiltin('Notification(%s,Incapable d''obtenir lien du video,5000,%s' % (xbmcaddon.Addon().getAddonInfo('name'), xbmcaddon.Addon().getAddonInfo('icon')))

        if playlist.size() > 0:
            xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(playlist)


def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

def addDir(name,url,mode,iconimage,categorie,nomComplet):
        name=name
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&categorie="+str(categorie)+"&fullName="+urllib.quote_plus(str(nomComplet))
        ok=True
        liz=xbmcgui.ListItem(urllib.unquote(name), iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": urllib.unquote(name) } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addEmission(name,url,iconimage,plot):
        prochainMode = 2
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(prochainMode)+"&name="+urllib.quote_plus(name)+"&fullName="+urllib.quote_plus(str(fullName))
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": urllib.unquote(name),"Plot":plot } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addDirSaison(name,url,iconimage,saison):
        prochainMode = 3
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(prochainMode)+"&name="+urllib.quote_plus(name)+"&season="+str(saison)+"&fullName="+urllib.quote_plus(str(fullName))
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": urllib.unquote(name),"Plot":name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,iconimage,url_info,plot,duree):
        ok=True
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=4&name="+urllib.quote_plus(name)+"&Info="+urllib.quote_plus(url_info)
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": urllib.quote_plus(name),"Plot":plot,"Duration":duree } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

def debugPrint(texte):
        u=sys.argv[0]+"?url="+urllib.quote_plus(TELEQUEBEC_BASE_URL)+"&mode="+str(0)+"&name="+urllib.quote_plus(texte)
        ok=True
        liz=xbmcgui.ListItem(texte, iconImage="DefaultFolder.png", thumbnailImage='')
        liz.setInfo( type="Video", infoLabels={ "Title": texte } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok


params=get_params()
url=None
name=None
mode=None
url_info=None
categorie=None
season=0
fullName=0

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        categorie=int(params["categorie"])
except:
        pass
try:
        url_info=int(params["Info"])
except:
        pass
try:
        season=int(params["season"])
except:
        pass
try:
        fullName=int(params["fullName"])
except:
        pass
#print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        #print ""
        creerMenuCategories()

elif mode==1:
        #print ""+url
        creerListeFiltree(categorie,url)

elif mode==2:
        #print ""+url
        creerListeVideos(url)

elif mode==3:
        #print ""+url
        creerListeEpisodes(url,season,fullName)

elif mode==4:
        #print ""+url
        #print ""+url_info
        JOUERVIDEO(url,name,url_info)

elif mode==6:
        #print ""+url
        creerDossiers(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
