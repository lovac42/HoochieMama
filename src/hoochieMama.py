# -*- coding: utf-8 -*-
# Copyright: (C) 2018 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version: 0.0.2

# Title is in reference to Seinfeld, no relations to the current slang term.

# CONSTANTS:
SORT_BY_HARD_FIRST="order by ivl desc"
SORT_BY_EASY_FIRST="order by ivl asc"

# == User Config =========================================

#Warning! Chaning default settings may impact performance.

CUSTOM_SORT = None #disabled
# CUSTOM_SORT = SORT_BY_HARD_FIRST
# CUSTOM_SORT = SORT_BY_EASY_FIRST

#Anki's default QUEUE_LIMIT of 50 does not work well for parent decks,
#so we changed it. Cheap windows tablets may need to lower this number.
QUEUE_LIMIT = 250 #Deal size

# == End Config ==========================================
##########################################################



import random
import anki.sched
from aqt import mw
from anki.utils import ids2str, intTime
from anki.hooks import wrap
from anki import version
ANKI21 = version.startswith("2.1.")


#From: anki.schedv2.py
#Mod:  names for backwards compatibility
#Mod2: serenityNow, prioritize today first before overdues.
#      This will even out the numbers imposed by the parent deck limits.
#Mod3: added options for sorting by ivl.

def fillRev(self, _old):
    qc = self.col.conf
    if not qc.get("hoochieMama", False):
        return _old(self)
    # print('using hoochieMama')


    if self._revQueue:
        return True
    if not self.revCount:
        return False

    PENETRATION=QUEUE_LIMIT if CUSTOM_SORT else self.queueLimit
    lim=min(PENETRATION, currentRevLimit())
    if lim:
        DYN=self.col.decks.get(self.col.decks.selected(),False)['dyn']
        sortBy=CUSTOM_SORT if not DYN and CUSTOM_SORT else ''

        self._revQueue = self.col.db.list("""
select id from cards where
did in %s and queue = 2 and due = ?
%s
limit ?""" % (ids2str(self.col.decks.active()), sortBy),
                self.today, lim)


        more=lim-len(self._revQueue)
        if more:
            self._revQueue.extend(self.col.db.list("""
select id from cards where
did in %s and queue = 2 and due < ?
%s
limit ?""" % (ids2str(self.col.decks.active()), sortBy),
                self.today, more))


        if self._revQueue:
            if DYN: # dynamic decks need due order preserved
                self._revQueue.reverse()
            elif sortBy=='':
                # fixme: as soon as a card is answered, this is no longer consistent
                r = random.Random()
                # r.seed(self.today)
                # r.seed(intTime(1000))
                r.shuffle(self._revQueue)
            return True

    if self.revCount:
        # if we didn't get a card but the count is non-zero,
        # we need to check again for any cards that were
        # removed from the queue but not buried
        self._resetRev()
        return self._fillRev()


#From: anki.schedv2.py
def currentRevLimit():
    d = mw.col.decks.get(mw.col.decks.selected(), default=False)
    return deckRevLimitSingle(d)

#From: anki.schedv2.py
def deckRevLimitSingle(d, parentLimit=None):
    # invalid deck selected?
    if not d: return 0
    if d['dyn']: return mw.col.sched.dynReportLimit

    c = mw.col.decks.confForDid(d['id'])
    lim = max(0, c['rev']['perDay'] - d['revToday'][1])
    if parentLimit is not None:
        return min(parentLimit, lim)
    elif '::' not in d['name']:
        return lim
    else:
        for parent in mw.col.decks.parents(d['id']):
            # pass in dummy parentLimit so we don't do parent lookup again
            lim = min(lim, deckRevLimitSingle(parent, parentLimit=lim))
        return lim


anki.sched.Scheduler._fillRev = wrap(anki.sched.Scheduler._fillRev, fillRev, 'around')
if ANKI21:
    import anki.schedv2
    anki.schedv2.Scheduler._fillRev = wrap(anki.schedv2.Scheduler._fillRev, fillRev, 'around')


##################################################
#
#  GUI stuff, adds preference menu options
#
#################################################
import aqt
import aqt.preferences
from aqt.qt import *


if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

def setupUi(self, Preferences):
    r=self.gridLayout_4.rowCount()
    self.hoochieMama = QtWidgets.QCheckBox(self.tab_1)
    self.hoochieMama.setObjectName(_fromUtf8("hoochieMama"))
    self.hoochieMama.setText(_('Hoochie Mama! Randomize Queue'))
    self.hoochieMama.toggled.connect(lambda:toggle(self))
    self.gridLayout_4.addWidget(self.hoochieMama, r, 0, 1, 3)

def __init__(self, mw):
    qc = self.mw.col.conf
    cb=qc.get("hoochieMama", 0)
    self.form.hoochieMama.setCheckState(cb)

def accept(self):
    qc = self.mw.col.conf
    qc['hoochieMama']=self.form.hoochieMama.checkState()

def toggle(self):
    checked=not self.hoochieMama.checkState()==0
    if checked:
        try:
            self.serenityNow.setCheckState(0)
        except: pass

aqt.forms.preferences.Ui_Preferences.setupUi = wrap(aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after")
aqt.preferences.Preferences.__init__ = wrap(aqt.preferences.Preferences.__init__, __init__, "after")
aqt.preferences.Preferences.accept = wrap(aqt.preferences.Preferences.accept, accept, "before")
