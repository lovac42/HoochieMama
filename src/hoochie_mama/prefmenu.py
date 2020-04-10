# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import aqt
import aqt.preferences
from aqt.qt import *
from anki.lang import _
from anki.hooks import wrap

from .sort import CUSTOM_SORT
from .lib.com.lovac42.anki.version import ANKI21, ANKI20
from .lib.com.lovac42.anki.gui.checkbox import TristateCheckbox
from .lib.com.lovac42.anki.gui import muffins


if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


def setupUi(self, Preferences):
    grid_layout = muffins.getMuffinsTab(self)
    r = grid_layout.rowCount()
    mama_groupbox = QtWidgets.QGroupBox(self.lrnStage)
    mama_groupbox.setTitle("Hoochie Mama!")
    mama_grid_layout = QtWidgets.QGridLayout(mama_groupbox)
    grid_layout.addWidget(mama_groupbox, r, 0, 1, 3)

    r=0

    self.hoochieMama = TristateCheckbox(mama_groupbox)
    self.hoochieMama.setDescriptions({
        Qt.Unchecked:        "Hoochie Mama addon has been disabled",
        Qt.PartiallyChecked: "Randomize review cards, check subdeck limits",
        Qt.Checked:          "Randomize review cards, discard subdeck limits (~V2)",
    })

    mama_grid_layout.addWidget(self.hoochieMama, r, 0, 1, 3)
    self.hoochieMama.clicked.connect(lambda:toggle(self))

    r+=1
    self.hoochieMamaSortLbl=QtWidgets.QLabel(mama_groupbox)
    self.hoochieMamaSortLbl.setText(_("      Sort reviews by:"))
    mama_grid_layout.addWidget(self.hoochieMamaSortLbl, r, 0, 1, 1)

    self.hoochieMamaSort = QtWidgets.QComboBox(mama_groupbox)

    sort_itms = CUSTOM_SORT.iteritems if ANKI20 else CUSTOM_SORT.items
    for i,v in sort_itms():
        self.hoochieMamaSort.addItem(_(""))
        self.hoochieMamaSort.setItemText(i, _(v[0]))
    mama_grid_layout.addWidget(self.hoochieMamaSort, r, 1, 1, 3)

    r+=1 #Avoid round-robin reviews
    self.hoochieMamaPTD=QtWidgets.QCheckBox(mama_groupbox)
    self.hoochieMamaPTD.setText(_("Prioritize the reviews due today first?"))
    mama_grid_layout.addWidget(self.hoochieMamaPTD, r, 1, 1, 3)

    r+=1 #Force Extra shuffle
    self.hoochieMamaExRand = TristateCheckbox(mama_groupbox)
    self.hoochieMamaExRand.setDescriptions({
        Qt.Unchecked:        "Add Extra Shuffle?",
        Qt.PartiallyChecked: "Extra Shuffle: Fine (e.g. 1,5,3,2)",
        Qt.Checked:          "Extra Shuffle: Coarse (e.g. 3,25,9,6)",
    })
    mama_grid_layout.addWidget(self.hoochieMamaExRand, r, 1, 1, 3)



def load(self, mw):
    qc = self.mw.col.conf

    cb=qc.get("hoochieMama", Qt.Unchecked)
    self.form.hoochieMama.setCheckState(cb)

    cb=qc.get("hoochieMama_prioritize_today", Qt.Unchecked)
    self.form.hoochieMamaPTD.setCheckState(cb)

    cb=qc.get("hoochieMama_extra_shuffle", Qt.Unchecked)
    self.form.hoochieMamaExRand.setCheckState(cb)

    idx=qc.get("hoochieMamaSort", 0)
    self.form.hoochieMamaSort.setCurrentIndex(idx)

    toggle(self.form)



def save(self):
    toggle(self.form)
    qc = self.mw.col.conf

    qc['hoochieMama']=int(self.form.hoochieMama.checkState())
    qc['hoochieMama_prioritize_today']=int(self.form.hoochieMamaPTD.checkState())
    qc['hoochieMama_extra_shuffle']=int(self.form.hoochieMamaExRand.checkState())

    qc['hoochieMamaSort']=self.form.hoochieMamaSort.currentIndex()



def toggle(self):
    checked=self.hoochieMama.checkState()
    if checked:
        try:
            self.serenityNow.setCheckState(Qt.Unchecked)
        except: pass
        grayout = False
    else:
        grayout = True

    if checked == Qt.PartiallyChecked:
        self.hoochieMamaExRand.setText(_('Extra Shuffle (Mandatory)'))
        self.hoochieMamaExRand.setDisabled(True)
    else:
        self.hoochieMamaExRand.setDisabled(grayout)
        #refresh checkbox desc text
        s = self.hoochieMamaExRand.checkState()
        self.hoochieMamaExRand.onStateChanged(s)

    self.hoochieMamaPTD.setDisabled(grayout)
    self.hoochieMamaSort.setDisabled(grayout)
    self.hoochieMamaSortLbl.setDisabled(grayout)





# if point version < 23? Use old wrap
# TODO: Find the point version for these new hooks.

aqt.forms.preferences.Ui_Preferences.setupUi = wrap(
    aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after")

aqt.preferences.Preferences.__init__ = wrap(
    aqt.preferences.Preferences.__init__, load, "after"
)

aqt.preferences.Preferences.accept = wrap(
    aqt.preferences.Preferences.accept, save, "before"
)

