#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os, json

class Locstore(object):
    def __init__(self, filename, initvalue={}):
        self._filename, self.handle = filename, initvalue
        self.__isSaved = True
        self.reload()

    def _decode_list(self, data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(self, data):
        rv = {}
        if isinstance(data, list):
            return self._decode_list(data)
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv
    
    def reload(self):
        if os.path.exists(self._filename) and \
            os.path.getsize(self._filename) > 0:
            with open(self._filename, "rb") as f: self.handle = json.load(f)
        self.__isSaved = False

    def save(self, data=None):
        if data: self.handle = data
        with open(self._filename, "wb") as f:
            json.dump(self._decode_dict(self.handle), f, ensure_ascii=False,
                                        indent=1, encoding="utf-8")
        self.__isSaved = True