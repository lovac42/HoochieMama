# HoochieMama
AnkiAddon: Randomize Queue

<i>Title is in reference to Seinfeld, no relations to the current slang term.</i>


## About:
This is the back-ported _fillRev method from the V2 scheduler with some added features from serenityNow and works on both v1 and v2 scheduler. It allows randomization of subdecks on the v1 scheduler without switching to the V2 scheduler.

"'Randomization of subdecks on the v1 scheduler' in an add-on for 2.0 means to have the best part of the V2 scheduler (imo) while you can sync with AnkiDroid and use all the add-ons that haven't been ported yet." -<b>ijgnd</b>

Note1: V2 only randomizes review cards, not learning or new cards. Search for the addon HoochiePapa for this feature. And HoochieBaby randomizes the day learning queue. These uses the same template but were not developed on the same day and operates on differ queues.

Note2: V2 randomizes subdecks but uses max reviews limit from the parent deck. This creates an imbalance where users with large amount of over due low priority cards could potentially end up focusing on one subdeck. A typical example: say Leaves, Clouds, Knots, and Math with a max review of 5 each and a cap at 20 for the parent deck. If the user have a large amount of overdue, say 25 each, the V2 scheduler would grab 20 cards sorted by dues resulting in 13 Leaves, 4 Clouds, 2 Knots, and 1 Math.


### Enhancements (off by default):
- <b>Customize sorting</b> by dues, intervals, or reps.
- <b>Focus on today's dues first.</b> This will avoid round-robin scheduling of forgotten cards. It will also ensure a set number of today's due cards are taken from each subdeck.
- <b>Enforce subdeck limits.</b> This uses a custom queue builder (not V2), a set number of cards are taken from each subdeck (up to max rev) then randomizes the review before displaying it to the user. <b>If sorting, each deck is sorted individually, then 5+ cards are drawn at a time from each subdeck and shuffled before review.</b> So three subdeck sorting by ABC: 1A,1B,1C, 2A,2B,2C, 3A,3B,3C could result in 2A,3A,1A, 3B,1B,2B, 3C,2C,1C during review.

For more info on config combo options, please <a href="https://github.com/lovac42/HoochieMama/blob/master/src/config.md">see this page for more details.</a>


### Extra Shuffle:
New in v0.3.0 is the added option for extra shuffling for each batch. As you know, Anki grabs 50 cards per batch. So if you have your reviews sorted by young first, the extra shuffle will look like:  
FROM: ```1,1,2,2,2,3,4,4,5,5,5,5,8,10...```  
TO: ```8,1,2,1,5,5,1,4,3,10,4...```  

Unfortunately, if you only have a small number of reviews, the young and matured cards would be mixed together per batch, and the extra shuffling can be too much:  
FROM: ```(1,2,5,5,10,12,15,21,22,35,42,54,69...)```  
TO: ```(5,69,21,1,12,54,5,22,35,2...)```  

This is where fine mode comes in handy. It divides each batch further into three piles and shuffles each pile separately then places them back together:  
FROM: ```(1,2,5,5,10,12,15,21,22,35,42,54,69...)```  
TO: ```(2,5,1,5,10)```, ```(22,12,21,15)```, ```(54,35,69,42)```

These two modes will be labeled as fine and coarse mode.


## Configs:
This addon must be activated in preferences.

<img src="https://github.com/lovac42/HoochieMama/blob/master/screenshots/prefmenu.png?raw=true">

Note: If you have serenityNow installed, please update to the latest version or disable it. If you have any other addons that also monkey patches _fillRev, disable them as well. (e.g. <a href="https://ankiweb.net/shared/info/3731265543">Change Order of Review Cards in Regular Decks</a>)


## Bugs/Features:
In the event where subdecks have a large amount of overdues and both parent and child are capped at a small number, there is a mis-count issue with the V1 scheduler. The deck browser would report a review total calculated from each subdeck limit (V1), but in the overview and with the actual reviews, the numbers are based on the limit from the parent deck (V2). This discrepancy may cause some confusion, but it is only a cosmetic difference. Patching this will break compatibility with other popular addons, so I decided to leave this as it is. With the addon <a href="https://ankiweb.net/shared/info/877182321">Enhanced Main Window</a> or similar plugins, you should be able to get a ballpark of the actual review count making any fixes unnecessary.


## Sorting:
<img src="https://github.com/lovac42/HoochieMama/blob/master/screenshots/sorting.png?raw=true">
