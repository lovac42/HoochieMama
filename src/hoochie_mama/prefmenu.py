# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import aqt
import aqt.preferences
from aqt import mw
from aqt.qt import *
from anki.lang import _
from anki.hooks import wrap

from .sort import CUSTOM_SORT, VANGUARD
from .self_test import run_tests
from .lib.com.lovac42.anki.version import ANKI20
from .lib.com.lovac42.anki.gui.checkbox import TristateCheckbox
from .lib.com.lovac42.anki.gui import muffins


loaded = False


def setupUi(self, Preferences):
    global loaded
    loaded = False

    mama_groupbox = muffins.getMuffinsGroupbox(self, "Hoochie Mama!")
    mama_grid_layout = QGridLayout(mama_groupbox)

    r=0
    self.hoochieMama = TristateCheckbox(mama_groupbox)
    self.hoochieMama.setDescriptions({
        Qt.Unchecked:        "Hoochie Mama addon has been disabled",
        Qt.PartiallyChecked: "Randomize review cards, check subdeck limits",
        Qt.Checked:          "Randomize review cards, discard subdeck limits (~V2)",
    })
    mama_grid_layout.addWidget(self.hoochieMama, r, 0, 1, 3)
    self.hoochieMama.clicked.connect(lambda:onClick(self))
    self.hoochieMama.onClick = onClick

    r+=1
    self.hoochieMamaSortLbl = QLabel(mama_groupbox)
    self.hoochieMamaSortLbl.setText(_("      Sort reviews by:"))
    mama_grid_layout.addWidget(self.hoochieMamaSortLbl, r, 0, 1, 1)

    self.hoochieMamaSort = QComboBox(mama_groupbox)
    sort_itms = CUSTOM_SORT.iteritems if ANKI20 else CUSTOM_SORT.items
    for i,v in sort_itms():
        self.hoochieMamaSort.addItem(_(""))
        self.hoochieMamaSort.setItemText(i, _(v[0]))
    mama_grid_layout.addWidget(self.hoochieMamaSort, r, 1, 1, 3)
    self.hoochieMamaSort.currentIndexChanged.connect(
        lambda:onChanged(self.hoochieMamaSort,"hoochieMamaSort")
    )

    r+=1 #Avoid round-robin reviews
    self.hoochieMamaPTD = TristateCheckbox(mama_groupbox)
    if not VANGUARD:
        self.hoochieMamaPTD.setTristate(False)
        self.hoochieMamaPTD.setDescriptions({
            Qt.Unchecked:        "Set prioritization criteria?",
            Qt.PartiallyChecked: "Error you should not see this",
            Qt.Checked:          "Prioritize young cards due today",
        })
    else:
        self.hoochieMamaPTD.setDescriptions({
            Qt.Unchecked:        "Fast, no comparisons",
            Qt.PartiallyChecked: "Compare with ANN",
            Qt.Checked:          "Compare with SM8DLL",
        })
    mama_grid_layout.addWidget(self.hoochieMamaPTD, r, 1, 1, 3)
    self.hoochieMamaPTD.clicked.connect(
        lambda:onClickEx(self.hoochieMamaPTD,"hoochieMama_prioritize_today")
    )

    r+=1 #Force Extra shuffle
    self.hoochieMamaExRand = TristateCheckbox(mama_groupbox)
    self.hoochieMamaExRand.setDescriptions({
        Qt.Unchecked:        "Add Extra Shuffle?",
        Qt.PartiallyChecked: "Extra Shuffle: Fine (e.g. 1,5,3,2)",
        Qt.Checked:          "Extra Shuffle: Coarse (e.g. 3,25,9,6)",
    })
    mama_grid_layout.addWidget(self.hoochieMamaExRand, r, 1, 1, 3)
    self.hoochieMamaExRand.clicked.connect(
        lambda:onClickEx(self.hoochieMamaExRand,"hoochieMama_extra_shuffle")
    )

    if VANGUARD:
        r+=1
        self.hoochieMamaVdLbl = QtWidgets.QLabel(mama_groupbox)
        self.hoochieMamaVdLbl.setText(_("      Transformations:"))
        mama_grid_layout.addWidget(self.hoochieMamaVdLbl, r, 0, 1, 1)
        self.hoochieMamaVd = QtWidgets.QComboBox(mama_groupbox)

        sort_itms = VANGUARD.iteritems if ANKI20 else VANGUARD.items
        for i,v in sort_itms():
            self.hoochieMamaVd.addItem("")
            self.hoochieMamaVd.setItemText(i, _(v[0]))
        mama_grid_layout.addWidget(self.hoochieMamaVd, r, 1, 1, 3)
        self.hoochieMamaVd.currentIndexChanged.connect(
            lambda:onChanged(self.hoochieMamaVd, "hoochieMamaVd")
        )


def load(self, mw):
    global loaded
    qc = self.mw.col.conf

    cb = qc.get("hoochieMama", Qt.Unchecked)
    self.form.hoochieMama.setCheckState(cb)

    cb = qc.get("hoochieMama_prioritize_today", Qt.Unchecked)
    self.form.hoochieMamaPTD.setCheckState(cb)

    cb = qc.get("hoochieMama_extra_shuffle", Qt.Unchecked)
    self.form.hoochieMamaExRand.setCheckState(cb)

    idx = qc.get("hoochieMamaSort", 0)
    self.form.hoochieMamaSort.setCurrentIndex(idx)

    if VANGUARD:
        idx = qc.get("hoochieMamaVd", 0)
        self.form.hoochieMamaVd.setCurrentIndex(idx)

    _updateDisplay(self.form)
    loaded = True


def onClick(form):
    state = int(form.hoochieMama.checkState())
    mw.col.conf['hoochieMama'] = state
    _updateDisplay(form)
    run_tests.testWrap(state)


def onClickEx(checkbox, key):
    state = int(checkbox.checkState())
    mw.col.conf[key] = state
    idx = mw.col.conf.get("hoochieMamaSort", 0)
    run_tests.testSort(idx)


def onChanged(combobox, key):
    idx = combobox.currentIndex()
    mw.col.conf[key] = idx
    if loaded:
        run_tests.testSort(idx)


def _updateDisplay(form):
    state = form.hoochieMama.checkState()
    if state:
        try:
            form.serenityNow.setCheckState(Qt.Unchecked)
        except: pass

    grayout = state == Qt.Unchecked

    if state == Qt.PartiallyChecked:
        form.hoochieMamaExRand.setText(_('Extra Shuffle (Mandatory)'))
        form.hoochieMamaExRand.setDisabled(True)
    else:
        form.hoochieMamaExRand.setDisabled(grayout)
        #refresh checkbox desc text
        s = form.hoochieMamaExRand.checkState()
        form.hoochieMamaExRand.onStateChanged(s)

    form.hoochieMamaPTD.setDisabled(grayout)
    form.hoochieMamaSort.setDisabled(grayout)
    form.hoochieMamaSortLbl.setDisabled(grayout)

    if VANGUARD:
        form.hoochieMamaVd.setDisabled(grayout)
        form.hoochieMamaVdLbl.setDisabled(grayout)



# Wrap Crap ############

# if point version < 23? Use old wrap
# TODO: Find the point version for these new hooks.

aqt.forms.preferences.Ui_Preferences.setupUi = wrap(
    aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after")

aqt.preferences.Preferences.__init__ = wrap(
    aqt.preferences.Preferences.__init__, load, "after"
)

# aqt.preferences.Preferences.accept = wrap(
    # aqt.preferences.Preferences.accept, save, "before"
# )

