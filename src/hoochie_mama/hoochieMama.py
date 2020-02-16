# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# Title is in reference to Seinfeld, no relations to the current slang term.


import random
import anki.sched
from aqt import mw
from anki.utils import ids2str
from anki.hooks import wrap

from .sort import CUSTOM_SORT
from .utils import *
from .const import *



#Turn this on if you are having problems.
def debugInfo(msg):
    # print(msg) #console

    # from aqt.utils import showText
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
        extShuffle=qc.get("hoochieMama_extra_shuffle",False)

        if perDeckLimit:
            self._revQueue=getRevQueuePerSubDeck(self,sortBy,lim,priToday)
        else:
            self._revQueue=getRevQueue(self,sortBy,lim,priToday)

        if self._revQueue:
            if perDeckLimit or extShuffle==2:
                random.Random().shuffle(self._revQueue)
                return True
            elif extShuffle:
                self._revQueue=nonuniformShuffle(self._revQueue)
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
    r=random.Random()
    r.shuffle(sched._revDids)

    pen=max(5,penetration//len(sched._revDids)) #if div by large val
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
    if mw.state == "sync":
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

