# -*- coding: utf-8 -*-

import os
from vkdata import vk_get_audio
from pyfileget import download
from locstore import Locstore

def get_filename(**template):
    filename = u"{artist} - {song}.mp3".format(**template)
    return filename

def get_current_dir(filename=__file__):
    return os.path.dirname(os.path.realpath(filename))

def get_new_tracks(vklist, locallist):
    newtracks = {}
    for trackID in vklist.keys():
        if not trackID in locallist.keys():
            newtracks[trackID] = list(vklist[trackID])
    return newtracks
       
def download_tracks(tracklist, locallist, basepath):
    l = len(tracklist)
    i = 0
    for trackID, [link, artist, song] in tracklist.items():
        i += 1
        print "%d of %d" % (i, l)
        filename = get_filename(artist=artist, song=song)
        path = os.path.join(basepath, filename)
        artistpath = os.path.join(basepath, artist, filename)
        if not (os.path.exists(path) or os.path.exists(artistpath)):
            download(link, path)
        locallist[trackID] = [link, artist, song, path]
    return locallist

def update_filenames(vklist, locallist):
    for trackID, [link, vkArtist, vkSong] in vklist.items():
        _link, localArtist, localSong, path = locallist[trackID]
        if not(vkArtist == localArtist and vkSong == localSong):
            newpath = os.path.join(os.path.dirname(path),
                                   get_filename(artist=vkArtist, song=vkSong))
            print "Renaming [%s] to [%s]" % (path, newpath)
            os.rename(path, newpath)
            locallist[trackID] = [_link, vkArtist, vkSong, newpath]
    return locallist    

def get_artist_path(artist, basepath):
    newPath = os.path.join(basepath, artist)
    if not os.path.exists(newPath): 
        print "Creating new path", newPath
        os.mkdir(newPath)
    return newPath

def get_artist_count(locallist):
    count = {}
    for link, artist, song, path in locallist.values():
        try:
            count[artist] += 1
        except KeyError:
            count[artist] = 1
    return count

def sort_to_folders(locallist, basepath, foldermin=3):
    artistsCount = get_artist_count(locallist)
    for trackID, [link, artist, song, path] in locallist.items():
        newPath = os.path.join(basepath, os.path.basename(path))
        if artistsCount[artist] >= foldermin:
            newPath = os.path.join(get_artist_path(artist, basepath),
                                   os.path.basename(path))
        if not path == newPath:
            print "Moving [%s] to [%s]" % (path, newPath)
            os.rename(path, newPath)
            locallist[trackID] = [link, artist, song, newPath]

def remove_empty_dirs(path):
    for root, dirs, files in os.walk(path): 
        for dname in dirs:
            dpath = os.path.join(root, dname)
            if not os.listdir(dpath): os.rmdir(dpath)

def check_index(locallist, basepath):
    paths = []
    for root, dirs, files in os.walk(basepath):
        for fname in files: 
            if fname.split(".")[-1] == "mp3":
                paths.append(os.path.join(root, fname))
    for trackID, [link, artist, song, path] in locallist.items():
        if path in paths: paths.remove(path)
    return paths

def vk_sync(email, password, path, userid=None):
    audlist, userid = vk_get_audio(email, password, userid)
    indexfilename = os.path.join(get_current_dir(), "vkaudio_%s.json" % userid)
    lc = Locstore(indexfilename)
    dwnedTracks = lc.handle
    path = os.path.join(path, "audio%s" % userid)
    tracksToDownload = get_new_tracks(audlist, dwnedTracks)
    print len(tracksToDownload), "track(s) need to download" 
    download_tracks(tracksToDownload, dwnedTracks, path)
    lc.save()
    print "Renaming..."
    update_filenames(audlist, dwnedTracks)
    lc.save()
    print "Sorting..."
    sort_to_folders(dwnedTracks, path)
    lc.save()
    remove_empty_dirs(path)

    removedtracks = check_index(dwnedTracks, path)
    if len(removedtracks):
        print len(removedtracks), ("track(s) are not in index, but still"
                                    " in your sync folder.")
        remfilename = os.path.join(get_current_dir(), 
                                    "vkaudio_%s_removed.json" % userid)
        Locstore(remfilename).save(removedtracks)
