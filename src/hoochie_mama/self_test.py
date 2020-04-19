# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from aqt.utils import tooltip


FILTERED_DECK = 3


class Tests:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = -1

    def testWrap(self, checkbox):
        if mw.state != "review":
            tooltip("Mama can't run self-tests, you are not in the reviewer.", period=1200)
        elif not mw.col.sched.revCount:
            # Obviously this requires more than one review card for testing.
            # Otherwise, one would be stuck in the reviewer, while the queue is empty.
            tooltip("Mama can't run self-tests, you don't have enough review cards.", period=1200)
        else:
            self.reset()
            # Clears queue from blocking test. But this must be
            # reset to avoid double loading of the same card.
            mw.col.sched.revCount = 20
            mw.col.sched._revQueue = []
            try:
                mw.col.sched._fillRev()
            finally:
                mw.reset()

            if self.state==FILTERED_DECK:
                tooltip("Mama doesn't work with filtered decks.", period=1200)
                return

            assert checkbox == self.state, "\
HoochieMama, self-test failed. Test value was not as expected."

            if checkbox==1:
                tooltip("Mama was wrapped successfully! (with subdecks)", period=1200)
            elif checkbox==2:
                tooltip("Mama was wrapped successfully! (no subdecks)", period=1200)
            else:
                tooltip("Mama was unwrapped...", period=800)


run_tests = Tests()
