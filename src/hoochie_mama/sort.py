# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochieMama
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


CUSTOM_SORT = {
  0:["None (Equivalent to V2)",  "order by due, random()"],

# == User Config =========================================

  1:["Young IVL first (asc)",          "order by ivl asc, random()"],
  2:["Mature IVL first (desc)",        "order by ivl desc, random()"],
  3:["Low reps count first (asc)",     "order by reps asc, random()"],
  4:["High reps count first (desc)",   "order by reps desc, random()"],
  5:["Low ease factor first (asc)",    "order by factor asc, random()"],
  6:["High ease factor first (desc)",  "order by factor desc, random()"],
  7:["Low lapses count first (asc)",   "order by lapses asc, random()"],
  8:["High lapses count first (desc)", "order by lapses desc, random()"],
  9:["Overdue cards first (asc)",      "order by due asc, random()"],
 10:["Punctual cards first (desc)",    "order by due desc, random()"],

# == End Config ==========================================

 11:["Unrestricted Random (HighCPU)",  "order by random()"]
}

# Difference between #0 and #9:
# In the current version, they are the same.
# In the previous versions of V2, cards are sorted
# by overdues then randomized per batch. whereas,
# cards sorted in #9 are not randomized.
