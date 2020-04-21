# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/AddonManager21
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version: 0.1.1


from aqt import mw
from aqt.qt import *
from anki.hooks import addHook, runHook
from codecs import open
from anki.utils import json
import os, collections

from anki import version
ANKI21=version.startswith("2.1.")


class Config():
    config = {}

    def __init__(self, addonName):
        self.addonName=addonName
        addHook('profileLoaded', self._loadConfig)
        # addHook('unloadProfile', self._patch_manifest)

    def set(self, key, value):
        self.config[key]=value

    def get(self, key, default=None):
        return self.config.get(key, default)

    def has(self, key):
        return self.config.get(key)!=None

    def _loadConfig(self):
        if getattr(mw.addonManager, "getConfig", None):
            mw.addonManager.setConfigUpdatedAction(__name__, self._updateConfig)
            # self.config=mw.addonManager.getConfig(__name__)
        # else:
        c,m = self._readConfig()
        self.config = c
        self.meta = m
        runHook(self.addonName+'.configLoaded')

    def _updateConfig(self, config):
        self.config=nestedUpdate(self.config,config)
        runHook(self.addonName+'.configUpdated')

    def _readConfig(self):
        conf=self.readFile('config.json') or {}
        meta=self.readFile('meta.json') or {}
        if meta:
            conf=nestedUpdate(conf,meta.get('config',{}))
        return conf, meta

    def readFile(self, fname, jsn=True):
        moduleDir, _ = os.path.split(__file__)
        path = os.path.join(moduleDir,fname)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data=f.read()
            if jsn:
                return json.loads(data)
            return data

    def save(self):
        moduleDir, _ = os.path.split(__file__)
        path = os.path.join(moduleDir,'meta.json')
        self.meta['config']=self.config
        with open(path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.meta))

    def _patch_manifest(self):
        """ If mod time in manifest is larger than
            mod time on the server, update
            max_point_version on unloadProfile.
        """
        meta = self.meta
        pt = meta.get('max_point_version',0)
        if pt<0:
            manf=self.readFile('manifest.json') or {}
            if meta.get('mod',0)<manf.get('mod',0):
                meta['max_point_version']=manf.get('max_point_version',abs(pt))
                meta['mod']=manf.get('mod',0)
                self.save()



#From: https://stackoverflow.com/questions/3232943/
def nestedUpdate(d, u):
    if ANKI21: #py3.3+
        itms=u.items()
    else: #py2.7
        itms=u.iteritems()
    for k, v in itms:
        if isinstance(v, collections.Mapping):
            d[k] = nestedUpdate(d.get(k, {}), v)
        else:
            d[k] = v
    return d
