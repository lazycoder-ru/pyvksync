#!/usr/bin/python
# -*- coding: utf-8 -*- 

# VKSync ver. 0.1
# Python script for synchronizing your audio collection on vk.com with local folder.

__version = "0.1"

from getpass import getpass
from lib import vk_sync

def display_welcome():
    print "pyVKSync", __version
    print "Download audio from vk.com"

def main():
    display_welcome()
    config = {}
    execfile("pyvksync.conf", config)
    if not "PATH" in config:
        print "Please, specify PATH to sync in vksync.conf"
    if not "EMAIL" in config:
        config["EMAIL"] = raw_input("Login(e-mail) on vk.com: ")
    password = getpass("Password[%s]: " % config["EMAIL"])
    vk_sync(config["EMAIL"], password, config["PATH"], config.get("USERID"))

    return 0

if __name__ == '__main__':
    main()
