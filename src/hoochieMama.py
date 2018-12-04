# -*- coding: utf-8 -*-
# Copyright: (C) 2018 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version: 0.0.8

# Title is in reference to Seinfeld, no relations to the current slang term.

# CONSTANTS:
SHOW_YOUNG_FIRST="order by ivl desc"
SHOW_MATURE_FIRST="order by ivl asc"
SHOW_LOW_REPS_FIRST="order by reps desc"
SHOW_HIGH_REPS_FIRST="order by reps asc"

# == User Config =========================================

#Warning! Chaning default settings may impact performance.

CUSTOM_SORT = None #Default: Randomize review
# CUSTOM_SORT = SHOW_YOUNG_FIRST
# CUSTOM_SORT = SHOW_MATURE_FIRST
# CUSTOM_SORT = SHOW_LOW_REPS_FIRST
# CUSTOM_SORT = SHOW_HIGH_REPS_FIRST

#Anki's default QUEUE_LIMIT of 50 does not work well for parent decks,
#so we changed it. Cheap windows tablets may need to lower this number.
QUEUE_LIMIT = 256 #Deal size

# == End Config ==========================================
##########################################################



import random
import anki.sched
from aqt import mw
from anki.utils import ids2str
from anki.hooks import wrap, addHook

from anki import version
ANKI21 = version.startswith("2.1.")
on_sync=False


#From: anki.schedv2.py
#Mod:  Various, see logs
def fillRev(self, _old):
    if self._revQueue:
        return True
    if not self.revCount:
        return False

    # This seem like old comments left behind, and does not affect current versions.
    # Remove these lines for testing
    if self.col.decks.get(self.col.decks.selected(),False)['dyn']:
        # dynamic decks need due order preserved
        return _old(self)


    qc = self.col.conf
    if not qc.get("hoochieMama", False):
        return _old(self)
    # print('using hoochieMama')


# In the world of blackjack, “penetration”, or “deck penetration”, 
# is the amount of cards that the dealer cuts off,
# relative to the cards dealt out.
    lim=currentRevLimit(self)
    if lim:
        if CUSTOM_SORT:
            penetration=min(QUEUE_LIMIT,lim)
            sortBy=CUSTOM_SORT
        else: #Default
            penetration=min(self.queueLimit,lim)
            sortBy=''

        self._revQueue = self.col.db.list("""
select id from cards where
did in %s and queue = 2 and due = ?
%s limit ?""" % (ids2str(self.col.decks.active()), sortBy),
                self.today, penetration)


        more=penetration-len(self._revQueue)
        if more:
            arr=self.col.db.list("""
select id from cards where
did in %s and queue = 2 and due < ?
%s limit ?""" % (ids2str(self.col.decks.active()), sortBy),
                self.today, more)
            if arr: self._revQueue.extend(arr)


        if self._revQueue:
            if not CUSTOM_SORT:
                # fixme: as soon as a card is answered, this is no longer consistent
                r = random.Random()
                # r.seed(self.today)
                r.shuffle(self._revQueue)
            return True

    if self.revCount:
        # if we didn't get a card but the count is non-zero,
        # we need to check again for any cards that were
        # removed from the queue but not buried
        self._resetRev()
        return self._fillRev()




#From: anki.schedv2.py
def currentRevLimit(self):
    d = self.col.decks.get(self.col.decks.selected(), default=False)
    return deckRevLimitSingle(self, d)


#From: anki.schedv2.py
def deckRevLimitSingle(self, d, parentLimit=None):
    if not d: return 0  # invalid deck selected?
    if d['dyn']: return 99999

    c = self.col.decks.confForDid(d['id'])
    lim = max(0, c['rev']['perDay'] - d['revToday'][1])
    if parentLimit is not None:
        return min(parentLimit, lim)
    elif '::' not in d['name']:
        return lim
    else:
        for parent in self.col.decks.parents(d['id']):
            # pass in dummy parentLimit so we don't do parent lookup again
            lim = min(lim, deckRevLimitSingle(self, parent, parentLimit=lim))
        return lim




#For reviewer count display (cosmetic)
#From: anki.schedv2.py
def resetRevCount(self, _old):
    if on_sync: return _old(self)

    qc = self.col.conf
    if not qc.get("hoochieMama", False):
        return _old(self)

    lim = currentRevLimit(self)
    self.revCount = self.col.db.scalar("""
select count() from (select id from cards where
did in %s and queue = 2 and due <= ? limit %d)""" % (
        ids2str(self.col.decks.active()), lim), self.today)


anki.sched.Scheduler._fillRev = wrap(anki.sched.Scheduler._fillRev, fillRev, 'around')
anki.sched.Scheduler._resetRevCount = wrap(anki.sched.Scheduler._resetRevCount, resetRevCount, 'around') #no need for v2
if ANKI21:
    import anki.schedv2
    anki.schedv2.Scheduler._fillRev = wrap(anki.schedv2.Scheduler._fillRev, fillRev, 'around')



#This fixes sync errors
def onSync(type):
    global on_sync
    if type=='finalize':
        on_sync=False
    else:
        on_sync=True
addHook('sync',onSync)



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
