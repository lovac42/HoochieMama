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
from .const import *

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
    self.hoochieMamaSortLbl.setText(_("      Sort RevQ By:"))
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
    self.hoochieMamaPTD.setText(_("Prioritize today's revs first?"))
    self.lrnStageGLayout.addWidget(self.hoochieMamaPTD, r, 1, 1, 3)

    r+=1 #Force Extra shuffle
    self.hoochieMamaExRand=QtWidgets.QCheckBox(self.lrnStage)
    self.hoochieMamaExRand.setText(_('Use Extra Shuffle?'))
    self.hoochieMamaExRand.setTristate(True)
    self.lrnStageGLayout.addWidget(self.hoochieMamaExRand, r, 1, 1, 3)
    self.hoochieMamaExRand.clicked.connect(lambda:togExtRand(self))

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
        togExtRand(self)
    self.hoochieMama.setText(_(txt))
    self.hoochieMamaPTD.setDisabled(grayout)
    self.hoochieMamaSort.setDisabled(grayout)
    self.hoochieMamaSortLbl.setDisabled(grayout)

def togExtRand(self):
    checked=self.hoochieMamaExRand.checkState()
    if checked==2: #hoochie overwhelming
        self.hoochieMamaExRand.setText(_('Extra Shuffle: Coarse (e.g. 3,25,9,6)'))
    elif checked==1: #less hoochie
        self.hoochieMamaExRand.setText(_('Extra Shuffle: Fine (e.g. 1,5,3,2)'))
    else:
        self.hoochieMamaExRand.setText(_('Use Extra Shuffle?'))


aqt.forms.preferences.Ui_Preferences.setupUi = wrap(aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after")
aqt.preferences.Preferences.__init__ = wrap(aqt.preferences.Preferences.__init__, load, "after")
aqt.preferences.Preferences.accept = wrap(aqt.preferences.Preferences.accept, save, "before")
