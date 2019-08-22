# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2019 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# Title is in reference to Seinfeld, no relations to the current slang term.


CUSTOM_SORT = {
  #DEFAULT V2
  0:["None (Shuffled)", "order by due, random()"],

# == User Config =========================================

  1:["Young first",  "order by ivl asc, random()"],
  2:["Mature first", "order by ivl desc, random()"],
  3:["Low reps",     "order by reps asc, random()"],
  4:["High reps",    "order by reps desc, random()"],
  5:["Low ease factor",  "order by factor asc, random()"],
  6:["High ease factor", "order by factor desc, random()"],
  7:["Low lapses",   "order by lapses asc, random()"],
  8:["High lapses",  "order by lapses desc, random()"],
  9:["Overdues",     "order by due asc, random()"],
 10:["Dues",         "order by due desc, random()"],

 11:["Unrestricted Random (HighCPU)", "order by random()"],

# == End Config ==========================================

}

## Performance Config ####################################

# Performance impact cost O(n)
# Uses quick shuffle if limit is exceeded.
DECK_LIST_SHUFFLE_LIMIT = 256

##########################################################


import random
import anki.sched
from aqt import mw
from anki.utils import ids2str
from aqt.utils import showText
from anki.hooks import wrap
from anki.lang import _

from anki import version
ANKI21 = version.startswith("2.1.")
CCBC = version.endswith("ccbc")
on_sync=False


#Turn this on if you are having problems.
def debugInfo(msg):
    # print(msg) #console
    # showText(msg) #Windows
    return


#From: anki.schedv2.py
#Mod:  Various, see logs
def fillRev(self, _old):
    if self._revQueue:
        return True
    if not self.revCount:
        return False
    # Below section is invoked everytime the reviewer is reset (edits, adds, etc)

    # This seem like old comments left behind, and does not affect current versions.
    # Remove these lines for testing
    if self.col.decks.get(self.col.decks.selected(),False)['dyn']:
        # dynamic decks need due order preserved
        return _old(self)


    qc = self.col.conf
    if not qc.get("hoochieMama",0):
        return _old(self)
    debugInfo('using hoochieMama')


    lim=currentRevLimit(self)
    if lim:
        sortLevel=qc.get("hoochieMamaSort", 0)
        assert sortLevel < len(CUSTOM_SORT)
        sortBy=CUSTOM_SORT[sortLevel][1]

        lim=min(self.queueLimit,lim)
        perDeckLimit=qc.get("hoochieMama",0)==1
        priToday=qc.get("hoochieMama_prioritize_today",False)

        if perDeckLimit:
            self._revQueue=getRevQueuePerSubDeck(self,sortBy,lim,priToday)
        else:
            self._revQueue=getRevQueue(self,sortBy,lim,priToday)

        if self._revQueue:
            if perDeckLimit or qc.get("hoochieMama_extra_shuffle",False):
                random.Random().shuffle(self._revQueue)
            else:
                self._revQueue.reverse() #preserve order
            return True

    if self.revCount:
        # if we didn't get a card but the count is non-zero,
        # we need to check again for any cards that were
        # removed from the queue but not buried
        self._resetRev()
        return self._fillRev()



# In the world of blackjack, “penetration”, or “deck penetration”, 
# is the amount of cards that the dealer cuts off, relative to the cards dealt out.
def getRevQueue(sched, sortBy, penetration, priToday=False):
    debugInfo('v2 queue builder')
    deckList=ids2str(sched.col.decks.active())
    revQueue=[]

    if priToday:
        revQueue = sched.col.db.list("""
select id from cards where
did in %s and queue = 2 and due = ?
%s limit ?""" % (deckList, sortBy),
                sched.today, penetration)

    if not revQueue:
        revQueue = sched.col.db.list("""
select id from cards where
did in %s and queue = 2 and due <= ?
%s limit ?""" % (deckList, sortBy),
                sched.today, penetration)

    return revQueue #Order needs tobe reversed for custom sorts



def getRevQueuePerSubDeck(sched, sortBy, penetration, priToday=False):
    debugInfo('per subdeck queue builder')
    revQueue=[]
    sched._revDids=sched.col.decks.active()
    LEN=len(sched._revDids)
    if LEN>DECK_LIST_SHUFFLE_LIMIT: #segments
        sched._revDids=cutDecks(sched._revDids,4) #0based
    else: #shuffle deck ids
        r=random.Random()
        r.shuffle(sched._revDids)

    pen=max(5,penetration//LEN) #if div by large val
    for did in sched._revDids:
        d=sched.col.decks.get(did)
        lim=min(pen,deckRevLimitSingle(sched,d)) #find parent limit
        if not lim: continue

        arr=None
        if priToday:
            arr=sched.col.db.list("""
select id from cards where
did = ? and queue = 2 and due = ?
%s limit ?"""%sortBy, did, sched.today, lim)

        if not arr:
            arr=sched.col.db.list("""
select id from cards where
did = ? and queue = 2 and due <= ?
%s limit ?"""%sortBy, did, sched.today, lim)

        revQueue.extend(arr) 
        if len(revQueue)>=penetration: break
    return revQueue #randomized later


#Like cutting cards, this is a quick and dirty way to randomize the deck ids
def cutDecks(queue,cnt=0):
    total=len(queue)
    p=random.randint(30,70) # %
    cut=total*p//100
    if cnt:
        q=cutDecks(queue[cut:],cnt-1)
        return q+cutDecks(queue[:cut],cnt-1)
    return queue[cut:]+queue[:cut]



#From: anki.schedv2.py
def currentRevLimit(sched):
    d = sched.col.decks.get(sched.col.decks.selected(), default=False)
    return deckRevLimitSingle(sched, d)


#From: anki.schedv2.py
def deckRevLimitSingle(sched, d, parentLimit=None):
    if not d: return 0  # invalid deck selected?
    if d['dyn']: return 99999

    c = sched.col.decks.confForDid(d['id'])
    lim = max(0, c['rev']['perDay'] - d['revToday'][1])
    if parentLimit is not None:
        return min(parentLimit, lim)
    elif '::' not in d['name']:
        return lim
    else:
        for parent in sched.col.decks.parents(d['id']):
            # pass in dummy parentLimit so we don't do parent lookup again
            lim = min(lim, deckRevLimitSingle(sched, parent, parentLimit=lim))
        return lim




#For reviewer count display (cosmetic)
def resetRevCount(sched, _old):
    if on_sync:
        return _old(sched)

    qc = sched.col.conf
    if not qc.get("hoochieMama",0):
        return _old(sched)

    if qc.get("hoochieMama",0)==1:
        return _resetRevCountV1(sched)
    return _resetRevCountV2(sched)


#From: anki.schedv2.py
def _resetRevCountV2(sched):
    lim = currentRevLimit(sched)
    sched.revCount = sched.col.db.scalar("""
select count() from (select id from cards where
did in %s and queue = 2 and due <= ? limit %d)""" % (
        ids2str(sched.col.decks.active()), lim), sched.today)

#From: anki.sched.py
def _resetRevCountV1(sched):
    def _deckRevLimitSingle(d):
        if not d: return 0
        if d['dyn']: return 1000
        c = mw.col.decks.confForDid(d['id'])
        return max(0, c['rev']['perDay'] - d['revToday'][1])
    def cntFn(did, lim):
        return sched.col.db.scalar("""
select count() from (select id from cards where
did = ? and queue = 2 and due <= ? limit %d)""" % lim,
                                      did, sched.today)
    sched.revCount = sched._walkingCount(
        _deckRevLimitSingle, cntFn)



anki.sched.Scheduler._fillRev = wrap(anki.sched.Scheduler._fillRev, fillRev, 'around')
anki.sched.Scheduler._resetRevCount = wrap(anki.sched.Scheduler._resetRevCount, resetRevCount, 'around')
if ANKI21:
    import anki.schedv2
    anki.schedv2.Scheduler._fillRev = wrap(anki.schedv2.Scheduler._fillRev, fillRev, 'around')
    anki.schedv2.Scheduler._resetRevCount = wrap(anki.schedv2.Scheduler._resetRevCount, resetRevCount, 'around')



#This monitor sync start/stops
oldSync=anki.sync.Syncer.sync
def onSync(self):
    global on_sync
    on_sync=True
    ret=oldSync(self)
    on_sync=False
    return ret

anki.sync.Syncer.sync=onSync



##################################################
#
#  GUI stuff, adds preference menu options
#
#################################################
import aqt
import aqt.preferences
from aqt.qt import *


#Must use IF-ELSE, potention exception using try-catch on some systems.
if ANKI21 and not CCBC:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


def setupUi(self, Preferences):
    try:
        grid=self.lrnStageGLayout
    except AttributeError:
        self.lrnStage=QtWidgets.QWidget()
        self.tabWidget.addTab(self.lrnStage, "Muffins")
        self.lrnStageGLayout=QtWidgets.QGridLayout()
        self.lrnStageVLayout=QtWidgets.QVBoxLayout(self.lrnStage)
        self.lrnStageVLayout.addLayout(self.lrnStageGLayout)
        spacerItem=QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.lrnStageVLayout.addItem(spacerItem)

    r=self.lrnStageGLayout.rowCount()
    self.hoochieMama=QtWidgets.QCheckBox(self.lrnStage)
    self.hoochieMama.setText(_('Hoochie Mama! Randomize Queue'))
    self.hoochieMama.setTristate(True)
    self.lrnStageGLayout.addWidget(self.hoochieMama, r, 0, 1, 3)
    self.hoochieMama.clicked.connect(lambda:toggle(self))

    r+=1
    self.hoochieMamaSortLbl=QtWidgets.QLabel(self.lrnStage)
    self.hoochieMamaSortLbl.setText(_("      Sort By:"))
    self.lrnStageGLayout.addWidget(self.hoochieMamaSortLbl, r, 0, 1, 1)

    self.hoochieMamaSort = QtWidgets.QComboBox(self.lrnStage)
    if ANKI21:
        itms=CUSTOM_SORT.items()
    else:
        itms=CUSTOM_SORT.iteritems()
    for i,v in itms:
        self.hoochieMamaSort.addItem(_(""))
        self.hoochieMamaSort.setItemText(i, _(v[0]))
    self.lrnStageGLayout.addWidget(self.hoochieMamaSort, r, 1, 1, 2)

    r+=1 #Avoid round-robin reviews
    self.hoochieMamaPTD=QtWidgets.QCheckBox(self.lrnStage)
    self.hoochieMamaPTD.setText(_('Prioritize Today?'))
    self.lrnStageGLayout.addWidget(self.hoochieMamaPTD, r, 1, 1, 3)

    r+=1 #Force Extra shuffle
    self.hoochieMamaExRand=QtWidgets.QCheckBox(self.lrnStage)
    self.hoochieMamaExRand.setText(_('Extra Shuffle within each batch?'))
    self.lrnStageGLayout.addWidget(self.hoochieMamaExRand, r, 1, 1, 3)


def load(self, mw):
    qc = self.mw.col.conf
    cb=qc.get("hoochieMama", 0)
    self.form.hoochieMama.setCheckState(cb)
    cb=qc.get("hoochieMama_prioritize_today", 0)
    self.form.hoochieMamaPTD.setCheckState(cb)

    cb=qc.get("hoochieMama_extra_shuffle", 0)
    self.form.hoochieMamaExRand.setCheckState(cb)

    idx=qc.get("hoochieMamaSort", 0)
    self.form.hoochieMamaSort.setCurrentIndex(idx)
    toggle(self.form)


def save(self):
    toggle(self.form)
    qc = self.mw.col.conf
    qc['hoochieMama']=self.form.hoochieMama.checkState()
    qc['hoochieMama_prioritize_today']=self.form.hoochieMamaPTD.checkState()
    qc['hoochieMama_extra_shuffle']=self.form.hoochieMamaExRand.checkState()
    qc['hoochieMamaSort']=self.form.hoochieMamaSort.currentIndex()


def toggle(self):
    checked=self.hoochieMama.checkState()
    if checked:
        try:
            self.serenityNow.setCheckState(0)
        except: pass
        grayout=False
    else:
        grayout=True

    if checked==1:
        txt='Hoochie Mama! RandRevQ w/ subdeck limit'
        self.hoochieMamaExRand.setDisabled(True)
        self.hoochieMamaExRand.setText(_('Extra Shuffle (Mandatory)'))
    else:
        txt='Hoochie Mama! Randomize Rev Queue'
        self.hoochieMamaExRand.setDisabled(grayout)
        self.hoochieMamaExRand.setText(_('Extra Shuffle within each batch?'))
    self.hoochieMama.setText(_(txt))
    self.hoochieMamaPTD.setDisabled(grayout)
    self.hoochieMamaSort.setDisabled(grayout)
    self.hoochieMamaSortLbl.setDisabled(grayout)


aqt.forms.preferences.Ui_Preferences.setupUi = wrap(aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after")
aqt.preferences.Preferences.__init__ = wrap(aqt.preferences.Preferences.__init__, load, "after")
aqt.preferences.Preferences.accept = wrap(aqt.preferences.Preferences.accept, save, "before")
