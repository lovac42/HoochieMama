# HoochieMama
AnkiAddon: Randomize Queue

Title is in reference to Seinfeld, no relations to the current slang term.

## About:
This is the back-ported _fillRev method from the v2 scheduler with some added features from serenityNow and works on both v1 and v2 scheduler. It allows randomization of sub-decks on the v1 scheduler without switching to the v2 scheduler.

"'Randomization of sub-decks on the v1 scheduler' in an add-on for 2.0 means to have the best part of the V2 scheduler (imo) while you can sync with AnkiDroid and use all the add-ons that haven't been ported yet." -ijgnd


### Enhancements:
V2 randomizes sub-decks but uses max reviews from the parent deck. This creates an imbalance where users with large amount of over due low priority cards could potentially end up focusing on one sub-deck. A typical example: say Leaves, Clouds, Knots, and Math with a max review of 5 each and a cap at 20 for the parent deck. If the user have a large amount of overdue, say 25 each, the V2 scheduler would grab 20 cards sorted by dues resulting in 13 Leaves, 4 Clouds, 2 Knots, and 1 Math.

The enhancement added is to focus on today's dues first. So for the previous example, it would be 4 dues today from each subdeck follow by any extra over dues from yesterday or later. Of course there are better enhancements that could have been made, but not for the general public and will probably degrade the performance of Anki. I see this as a reasonable compromise.


## Configs:
To prevent conflicts with other similar addons, this must be activated in preferences.

Note: If you have serenityNow installed, please update to the latest version or disable it. If you have any other addons that also monkey patches _fillRev, disable them as well. (e.g. <a href="https://ankiweb.net/shared/info/3731265543">Change Order of Review Cards in Regular Decks</a>)

<img src="https://github.com/lovac42/HoochieMama/blob/master/screenshots/prefmenu.jpg?raw=true">
