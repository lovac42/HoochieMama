# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from ..version import ANKI20
if ANKI20:
    range = xrange


def isSorted(arr, key=lambda x, y: x < y):
    return all([key(arr[i],arr[i+1]) for i in range(len(arr)-1)])
