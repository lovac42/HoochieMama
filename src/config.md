

# Config Options

## Example (V2):
Think about playing cards when reading below text:

PRIORITIZE_TODAY = False  
IMPOSE_SUBDECK_LIMIT = False  
CUSTOM_SORT = None  

<i>Cards are sorted by overdueness from all subdecks. 
50 cards (max at a time) are taken from the front 
then shuffled and distributed for review. (Default V2 setting.)</i>



PRIORITIZE_TODAY = False  
IMPOSE_SUBDECK_LIMIT = False  
CUSTOM_SORT = SHOW_MATURE_FIRST  

<i>Cards are sorted by IVL from all subdecks. 
50 cards (max at a time) are taken from the front 
and distributed for review. (No shuffle)</i>



PRIORITIZE_TODAY = True  
IMPOSE_SUBDECK_LIMIT = False  
CUSTOM_SORT = None  

<i>Cards are sorted by overdueness from all subdecks,
with today's due cards at the front of the queue. 
50 cards (max at a time) are taken from the front 
then shuffled and distributed for review.</i>



PRIORITIZE_TODAY = True  
IMPOSE_SUBDECK_LIMIT = False  
CUSTOM_SORT = SHOW_MATURE_FIRST  

<i>Cards are sorted by IVL from all subdecks,
with today's due cards at the front of the queue. 
50 cards (max at a time) are taken from the front 
and distributed for review. (No shuffle)</i>



## Example (Custom Queue Builder):
Think about playing cards when reading below text:

PRIORITIZE_TODAY = False  
IMPOSE_SUBDECK_LIMIT = True  
CUSTOM_SORT = None  

<i>Cards are sorted by overdueness from each respective subdeck.
n cards per subdeck (up to 50 chunks at a time) are taken from the front 
of each deck then shuffled and distributed for review.</i>



PRIORITIZE_TODAY = True  
IMPOSE_SUBDECK_LIMIT = True  
CUSTOM_SORT = None  

<i>Cards are sorted by overdueness from each respective subdeck, 
with today's due cards at the front of each subdeck's queue. 
n cards per subdeck (up to 50 chunks at a time) are taken from the front 
of each deck then shuffled and distributed for review.</i>



PRIORITIZE_TODAY = False  
IMPOSE_SUBDECK_LIMIT = True  
CUSTOM_SORT = SHOW_MATURE_FIRST  

<i>Cards are sorted by IVL from each respective subdeck.
n cards per subdeck (up to 50 chunks at a time) are taken from the front 
of each deck then shuffled and distributed for review.</i>

