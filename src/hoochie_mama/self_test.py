# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from aqt.utils import tooltip

from .const import ADDON_NAME
from .config import Config
from .lib.com.lovac42.anki.backend.utils import isSorted
from .lib.com.lovac42.anki.version import ANKI20

if ANKI20:
    range = xrange


class Tests:
    conf = Config(ADDON_NAME)

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = -1

    def _isReview(self):
        if mw.state == "review":
            tooltip("Mama can't run self-tests during review.", period=1200)
            return True

    def _selectDeck(self, did=1):
        old_did = mw.col.decks.selected()
        mw.col.decks.select(did)
        mw.col.sched._revDids = [did]
        return old_did

    def _restoreDeck(self, did):
        mw.col.decks.select(did)
        mw.col.sched._resetRev()

    def _setupTestCounts(self):
        mw.col.sched.newCount = 20
        mw.col.sched.revCount = 20
        mw.col.sched.lrnCount = 20
        mw.col.sched._revQueue = []

    def _isShuffled(self, index):
        mama_checkbox = mw.col.conf.get("hoochieMama", 1)
        if mama_checkbox==2:
            shuffle = mw.col.conf.get("hoochieMama_extra_shuffle", 0)
        else:
            shuffle = 2 #mandatory
        return shuffle or index in (0,11)


    def testWrap(self, checkbox):
        if not self.conf.get("run_self_test_wrap", True) or self._isReview():
            return

        self.reset()
        self._setupTestCounts()
        old_did = self._selectDeck(1)
        try:
            mw.col.sched._fillRev()
        finally:
            self._restoreDeck(old_did)

        assert checkbox == self.state, "HoochieMama, self-test failed. Test value was not as expected."

        if checkbox==1:
            tooltip("Mama was wrapped successfully! (with subdecks)", period=1200)
        elif checkbox==2:
            tooltip("Mama was wrapped successfully! (no subdecks)", period=1200)
        elif checkbox==0:
            tooltip("Mama was unwrapped...", period=800)
        else:
            raise ValueError("Checkbox state was not expected.")


    def testSort(self, index):
        if not self.conf.get("run_self_test_sort", False) or self._isReview():
            return
        if index > 11:
            raise ValueError("Index was not expected.")

        expected=0
        old_did = self._selectDeck(1)
        try:
            for i in range(5):
                r = self._testSort(index)
                if r < 0:
                    tooltip("Mama can't run self-tests. Not enough cards in default deck for testing.", period=2000)
                    return
                expected += r
        finally:
            self._restoreDeck(old_did)

        shuffle = self._isShuffled(index)

        # ensure a pass-rate of 3/5 due to unpredictable randomness.
        assert expected == 5 or (shuffle and expected >= 3), "HoochieMama, self-test failed. Tested values were not as expected."

        tooltip("Mama sort-test: OK", period=800)



    def _testSort(self, index):
        "This test require some cards put inside the Default anki folder."
        self.reset()
        self._setupTestCounts()

        mw.col.sched._fillRev()
        cids = mw.col.sched._revQueue
        if not cids or len(cids)<10:
            return -1

        arr = []
        for cid in cids:
            card = mw.col.getCard(cid)
            if index in (0,9,10,11):
                arr.append(card.due)
            elif index in (1,2):
                arr.append(card.ivl)
            elif index in (3,4):
                arr.append(card.reps)
            elif index in (5,6):
                arr.append(card.factor)
            elif index in (7,8):
                arr.append(card.lapses)
            else:
                raise ValueError("Index was not expected.")

        # print(arr)

        dr = False #desired result
        shuffle = self._isShuffled(index)
        if not shuffle and index in (1,3,5,7,9):
            dr = isSorted(arr, key=lambda x, y: x >= y)
        elif not shuffle and index in (2,4,6,8,10):
            dr = isSorted(arr, key=lambda x, y: x <= y)
        else: #idx = 0 or 11, test random
            #TODO:
            #  This test does not account for x >= y
            #  caused by addon conflicts.
            not_rand = isSorted(arr, key=lambda x, y: x <= y)
            if not_rand: #not random, test for same due
                dr = isSorted(arr, key=lambda x, y: x == y)
            else:
                dr = True

        if not dr:
            return 0
        return 1



run_tests = Tests()
