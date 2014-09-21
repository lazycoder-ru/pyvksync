# -*- coding: utf-8 -*- 

import urllib, urllib2, cookielib, re, HTMLParser

HEADERS = {'User-Agent':
'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0'}

class VKError(Exception):
    pass

def _get_normalize_str(string, restricted="<>:\"/\|?*"):
    h = HTMLParser.HTMLParser()
    string = h.unescape(string.lower())
    string = "".join(c for c in string if not c in restricted).title()
    return " ".join(string.split())

def vk_login(email, password):
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    urllib2.install_opener(opener)
    ip_h = re.findall('ip_h=(.+?)\&', urllib.urlopen("http://vk.com").read())[0]
    data = {"act":"login",
            "ip_h":ip_h,
            "_origin":"http://vk.com",
            "email":email,
            "pass":password}
    sendData = urllib.urlencode(data)
    req = urllib2.Request("http://login.vk.com", sendData, HEADERS)
    urllib2.urlopen(req)
    print "Getting user ID"
    page = urllib2.urlopen("http://vk.com/friends").read()
    try:
        userid = re.findall("name=\"id\" value=\"([0-9]+?)\"", page)[0]
    except Exception:
        raise VKError("Login failed!")
    return userid

def _vk_get_audiopage(userid):
    data = {"act":"load_audios_silent",
            "id":userid,
            "please_dont_ddos":"2",
            "al":"1"}
    sendData = urllib.urlencode(data)
    req = urllib2.Request("http://vk.com/audio.php", sendData, HEADERS)
    page = urllib2.urlopen(req).read()
    audiopage = unicode(str(page),'cp1251')
    matches = re.findall("\.mp3", audiopage) #dont work search or match
    if len(matches) == 0: raise VKError("Receiving audiopage error.")
    return audiopage

def _vk_parse_audio(audiopage):
    names = re.findall('.+?\[\'.+?\',\'(.+?)\',\'(http://.+?\.mp3)'
                        '.+?,\'.*?\',\'.*?\',\'(.+?)\',\'(.+?)\'', audiopage)
    tracks = {}
    for name in names:
        trackId = name[0]
        link = name[1]
        artist = _get_normalize_str(name[2])
        song = _get_normalize_str(name[3])
        tracks[trackId] = [link, artist, song]
    #linklist = list(set(linklist)) #remove dublicates
    return tracks

def vk_get_audio(email, password, userid=None):
    tracks = {}
    if not email or not password:
        raise VKError("Error. Login or password are not specified.")
    print "Logging via %s..." % email
    ownid = vk_login(email, password)
    if not userid: userid = ownid
    print "Receiving audiopage(%s)..." % userid
    page = _vk_get_audiopage(userid)
    print "Parsing audio..."
    tracks = _vk_parse_audio(page)
    print "Successfully parsed %d tracks." % len(tracks)
        
    return tracks, userid