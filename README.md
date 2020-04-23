# wiki_game
Given a starting page on Wikipedia, using connected pages, finds a list of linked pages to a target page.

This is a command line program that takes two arguments: Source and Target
The argument passed in as Source is "starting" page on wikipedia, it's goal is to 
scape links in starting wikipedia page until it finds the argument passed in 
as Target representing the target page.

All files required to run the program are included in this repository. Simply install
the dependant Python modules using `pip install -r requirements.txt` and run the file 
using the command `python wikipedia_game.py`

This was an interesting challenge to tackle. At first glance the requirements looked 
fairly straight forward, but as you dig in deeper, you begin realize why this challenge
can be given as a take home quiz without concern that a candidate would simply copy
a solution from the internet.

This is one of those problems where there is no real "correct" answer. In english
according to wikipedia there are currently over 6,000,000 articles and each article
based on my experience can have anywhere from 10 to over 10,000 page/article links.

I made some assumptions going into the project that turned out to cause various
challenges as I worked towards a complete solution. For starters, my initial thought
was to save time on not the first execution but those thereafter by storing wikipeida
API call results in a persistant database. Based on my testing, I'm starting to realize
that unless you plan to store results for close to all 6mil results, storing page/articles
on any given execution is just a tiny drop in the bucket for all the potential inputs.

I spent much more time than I'd like to admit setting up a sqlite db and hooking it up
to SQLalchemy. At this point, I'm not sure the time savings on concurrent calls are
worth it. I will say that it is nice for testing though. 

Some next steps I would take for optimizing my solution:
 - Threading is the obvious choice, since Wikipedia is I/O bound and a fast solution requires
   so many calls. However, wikipedia requests (at least on the free plan) that we make no more
   than 200 calls per second. Given the over 6m articles, if the intention was to scape every 
   single article and load them into a database, that would still take over 8 hours. 
   
 - I know there is some significant performance improvements to be had on my db writes/reads.
   and optimized production environment would likely work though all the links presented,
   without having to worry about wikipedias 200req/sec cap.
   
 - I'm not an expert in NLP by any means, but if we broke down page contents and the results
   as part of a sorting algorithm, we'd likely see some improvements there as well. If I was going
   work on optimizing my current code base, that's probably where I'd start. 
   
 - I decided to run with the wikipedia API rather than webscraping the HTML of a request. I
   wasn't sure exactly what was expected here, but I just thought of it as a actual challenge
   on the job to produce an answer. If I needed to scrape data from a website out there as part
   my job duties, I'd likely select an API over webscraping about 9 times out of 10. By using the
   existing API we reduce the risk of frontend UI changes (that happen much for frequently) from
   effecting the results of the code in production. However, I can see where there might be
   some optimization improvements if we looked at links in specific sections rather than
   treating all links the same. Again this is just one of the tradeoffs that needed to be made.
