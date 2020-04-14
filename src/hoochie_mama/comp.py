# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from anki.hooks import addHook

from .const import ADDON_NAME, TARGET_STABLE_VERSION
from .lib.com.lovac42.anki.version import POINT_VERSION, ANKI21


WARNING_MSG = """\
The addon "%s" was not made for your fancy new version

of Anki. You may continue to use it on this platform, unsupported.

But no whining or complaining should any problems occur, mkay?

    —L42   (╯°□°)╯︵ ┻━┻

_________________________________________________________
This addon was last tested to work on Anki v2.1.%d.
"""


def ankiVersionCompatibilityChecker(addon_name, stable_version):
    try:
        if stable_version < POINT_VERSION:
            import os
            import time
            from aqt import mw
            from aqt.utils import showWarning

            dir = os.path.dirname(__file__)
            meta = mw.addonManager.addonMeta(dir)

            mod = meta.get("mod", 0)
            warn_mod = meta.get("warn_time", -1)
            warn_ver = meta.get("warn_pt_ver", stable_version)
            if warn_mod < mod or warn_ver < POINT_VERSION:
                if not mod:
                    mod = int(time.time())
                    meta["mod"] = mod
                meta["warn_time"] = mod
                meta["warn_pt_ver"] = POINT_VERSION
                mw.addonManager.writeAddonMeta(dir, meta)
                showWarning(WARNING_MSG %(addon_name,stable_version))
    except:
        print("Count not print version compatibility warning due to an error.")



def onProfileLoaded():
    ankiVersionCompatibilityChecker(
        ADDON_NAME, TARGET_STABLE_VERSION)

if ANKI21:
    addHook('profileLoaded', onProfileLoaded)
