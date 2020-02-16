# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import random


# Each batch is split into 3 piles and shuffled 
# separately, then placed back together.
# This retains the sorting somewhat.
def nonuniformShuffle(queue):
    r=random.Random()
    LEN=len(queue)
    try:
        DIV=(LEN//min(3,LEN//8))+1
    except: # ZeroDivisionError:
        DIV=10
    Q=[]
    i=0
    while(True):
        j=i+DIV
        e=min(j,LEN)
        if e<=i: break
        q=queue[i:e]
        r.shuffle(q)
        Q.extend(q)
        i=j
    return Q

