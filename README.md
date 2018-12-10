# Homework 4: MongoDB database of image analysis from Google Cloud Vision API

### Due: December 10, 2018

### Prof Michael Mandel `mim@sci.brooklyn.cuny.edu`

## Introduction

For this assignment, you will be interacting with a set of text documents extracted from HTML pages using the Whoosh search engine in Python. The HTML pages are the pages that the Google Cloud Vision API identified as containing the images that we have been working with.

I have provided starter code in Python and because you will be using Whoosh, you must complete the assignment in Python. You will submit your code, the output of your queries, and a brief report describing your approach.

### Install and setup Whoosh

Use `pip` to install the `whoosh` package:

```bash
pip install Whoosh
```

The following code should run from the commandline and print "Worked!" without generating any errors. If it doesn't, then you have a problem with your python configuration or the installation of the `Whoosh` package.

```bash
python -c 'import whoosh; print("Worked!")'
```

### Introduction to the data (derived from data for homeworks 1, 2, and 3)

The data is derived from the data from homeworks 1, 2, and 3. It is provided in this repository in the `data/` directory. You will be working with the data in `data/pageText/` which is purely textual data. It is derived from the HTML pages in `data/pages/` which is only provided for your reference.

### Introduction to starter code

All of the python code is contained in the file [`runWhoosh.py`](https://github.com/cisc7610/homework4/blob/master/runWhoosh.py).
If you have all of the necessary dependencies installed, you should be able to run the script as it is to populate the search engine and perform a basic search.

If it is working, it should print out (among other things):

```
************************************************************
Top 20 terms
************************************************************


new	1.238054351312873
york	1.2138877407557376
was	1.1528091018625797
city	1.1521471877477851
all	1.1282244248428333
photos	1.123346974800077
flickr	1.120673627748619
de	1.1151258493496314
my	1.1135350567601834
but	1.0760340756525266
one	1.0677393268888629
art	1.0618331867941
has	1.0591524293950991
orleans	1.052347558290222
bridge	1.0393962386859077
world	1.035395129299458
la	1.0321754629743232
there	1.0315826984389482
their	1.0279772967904774
out	1.0169593132866073



************************************************************
Query:   new york   returned 196 results
************************************************************


Url: indulgy.com/post/9oS6UVpli2/empire-state-building-at-night-new-york-city
Highlight: State Building, NEW YORK City
Collect this now...State Building, NEW YORK City, 1957
Collect this...State Building ~ NEW YORK City, NEW YORK ✅
Collect this now for


Url: www.flickr.com/photos/tags/New_York
Highlight: guide possible to NEW YORK City!
Time Square : NEW YORK City
Time Square : NEW YORK City
Time Square has...questions. Thank you
NEW YORK - The City of Gold
NEW YORK Skyline Panorama
NEW YORK at Twilight, a Panorama...State Building
NEW YORK Public Library
NEW YORK from Brooklyn
NEW YORK depuis Brooklyn au


Url: indulgy.com/post/nGdsQo4VJ2/george-rodger-new-york-city-the-empire-stat
Highlight: State Building ~ NEW YORK City, NEW YORK ✅
Collect this now for...State Building in NEW YORK City 8/18/14
Collect...Empire State - NEW YORK City
Collect this now


Url: www.etsy.com/listing/200815622/nyc-photography-coney-island-boardwalk
Highlight: street scene gold
                NEW YORK, NYC, state print, NEW YORK City, NYC art print, NEW YORK Map, I Love NY, NEW YORK I Love You
        Eligible...Storm Photography, NEW YORK Photography, NEW YORK Wall Art Prints, NEW YORK City Prints, NYC Wall...Flowers, Florals, NEW YORK City Photography
                NEW YORK Skyline, NEW YORK, NEW YORK City, NEW YORK Art, Manhattan, Manhattan


Url: www.localdatabase.com/newyork/New_York
Highlight: Showroom
Photos of NEW YORK, NY
NEW YORK Population, Income...the English named it NEW YORK after the Duke of YORK.
NEW YORK City was once called...lost all their teeth
NEW YORK College Maps
NEW YORK Police Station Maps





************************************************************
Query:   empire state building   returned 47 results
************************************************************


Url: indulgy.com/post/9oS6UVpli2/empire-state-building-at-night-new-york-city
Highlight: this now for later
	                EMPIRE STATE BUILDING at night - New York...Bridge, Central Park, EMPIRE STATE BUILDING, Chrysler BUILDING and other popular...this now for later
                EMPIRE STATE BUILDING, New York BUILDING
Collect this now


Url: indulgy.com/post/nGdsQo4VJ2/george-rodger-new-york-city-the-empire-stat
Highlight: New York City. The EMPIRE STATE BUILDING. The observatory...City skyline and the EMPIRE STATE BUILDING
Collect this now...Chrysler BUILDING  The EMPIRE STATE BUILDING isnt the only New


Url: www.flickr.com/photos/danielmennerich/5443157673
Highlight: New York City USA - EMPIRE STATE BUILDING South Manhatten...A nice view from EMPIRE STATE BUILDING South Manhatten


Url: www.flickr.com/photos/danielmennerich/5205390702
Highlight: New York City USA - EMPIRE STATE BUILDING 01-TiltShift
The...EMPIRE STATE BUILDING rises to 381 m at...443.09 m. The BUILDING has 85 stories


Url: www.haikudeck.com/copy-of-richardson-stern-2-uncategorized-presentation-AUxDx8RhJJ
Highlight: up space between the EMPIRE STATE BUILDING ( nucleus ) and the...because the EMPIRE STATE BUILDING ( nucleolus ) is in...AND RNA
We chose the EMPIRE STATE BUILDING because it's the
```

### Introduction to Whoosh

[Whoosh](https://whoosh.readthedocs.io/en/latest/index.html) is a search engine implemented in pure python. It contains a everything you need for indexing documents and searching them, with several options for each feature. Specifically, for this assignment we will be exploring the effect of different tokenizers during indexing, different weighting methods during search, and different queries.

We covered an overview of search engines in [lecture 7](http://m.mr-pc.org/t/cisc7610/2018fa/lecture07.pdf). Whoosh indexes documents, processing different _fields_ separately. In the case of this homework, we are only indexing two fields, `url` and `body` with all of the action taking place in `body`.

Tokenization in Whoosh is accomplished by the `analyzer` used to analyze a field, for `body` this is defined on [Line 30 of runWhoosh.py](https://github.com/cisc7610/homework4/blob/master/runWhoosh.py#L30). Documentation for analyzers can be found [here](https://whoosh.readthedocs.io/en/latest/analysis.html). The standard analyzer is the `analysis.RegexTokenizer`. Multiple analyzers can be chained together using the pipe operator `|`.

Weighting methods determine how documents that are relevant to the query are ranked. In lecture 7 we discussed (term) frequency and TF-IDF. The weighting is selected on [Line 79 of runWhoosh.py](https://github.com/cisc7610/homework4/blob/master/runWhoosh.py#L79). The default weighting is BM25F, which is like TF-IDF but with several extra parameters to adjust its performance in various ways. Documentation about weightings can be found [here](https://whoosh.readthedocs.io/en/latest/api/scoring.html) listing the standard classes for weightings [here](https://whoosh.readthedocs.io/en/latest/api/scoring.html#scoring-algorithm-classes).

## Tasks

To complete the assignment, perform the following tasks and write the results in the file README.md in this repository.

### Compare different tokenizers

For this part, we will only use the "Top 20 terms" returned after indexing the documents.

Paste here the "Top 20 terms" that result from indexing using each of the following analysis pipelines:

1. `analysis.RegexTokenizer()`
1. `analysis.RegexTokenizer() | analysis.LowercaseFilter()`
1. `analysis.RegexTokenizer() | analysis.LowercaseFilter() | analysis.StopFilter()`

<!-- List the terms that are present in all cases here -->

List the terms that are only present in the last case

Paste here the "Top 20 terms" that result from indexing using the `analysis.StemmingAnalyzer()`.

How are these results different from those using the `analysis.RegexTokenizer()`?

Which top terms seem to be the most descriptive of the content of the web pages? Why?

Use the `analysis.RegexTokenizer() | analysis.LowercaseFilter() | analysis.StopFilter()` tokenizer for subsequent questions.

### Investigate the top term "de"

List the tokenizers under which "de" is a top 20 term.

One of the top terms is "de". List the URLs of the documents in which this term occurs (by running a query for it, see [Line 82 of runWhoosh.py](https://github.com/cisc7610/homework4/blob/master/runWhoosh.py#L82)).

What do these pages have in common?

### Compare different weightings

For this part, we will use the two queries, "new york" and "empire state building".

List the number of documents returned for each query and the URLs of the top 20 results for each query using the default weighting, `scoring.BM25F()`.

List the number of documents returned for each query and the URLs of the top 20 results for each query using the weightings:

1. `scoring.TF_IDF()`
1. `scoring.Frequency()`

List the URLs that are present for all weightings.

Which URLs seem to be the most relevant to the queries? Why?

Use the `scoring.BM25F()` weighting for subsequent questions.

### Measure the precision of several queries

Recall that _precision_ is a measure of retrieval performance calculated as the proportion of correct results returned to the total number of results returned. Normally the correct results are determined by hand, but in this case we will use a more specific query as the target correct results.

Measure the precision of the top 10 results returned by the query "empire state" with respect to retrieving the results of the query "empire state building". This means that correct results are those that are returned by the query "empire state building" and we are measuring the performance of the query "empire state" in retrieving those pages. Because the _highlights_ might be different between the two queries, make sure to compare URLs, which are unique.

Measure the precision of the top 20 results returned by the query "empire state" with respect to retrieving the results of the query "empire state building".

Measure the precision of the top 20 results returned by the query "new york" with respect to retrieving the results of the query "new york city".

### Describe any problems that you ran into in the course of this project

Describe any problems that you ran into in the course of this project

### student Assel Omarova

# results from (analysis.RegexTokenizer())

the 1.3038249658455618
of 1.28574691261295
and 1.2851435003033584
to 1.284734823441888
a 1.2731201647238295
in 1.2704127435365948
for 1.2292635229204252
you 1.2267466359126333
is 1.224275187676817
on 1.2152709697066606
The 1.2148034979913862
s 1.2135248297720869
New 1.1997292171352403
by 1.194215390624804
York 1.1898978880686921
I 1.188966592442376
with 1.1881898695277708
that 1.1749613590075554
your 1.1664312232771548
at 1.1601778328076626

# results from (analysis.RegexTokenizer() | analysis.LowercaseFilter())

the 1.30677969095649
to 1.2856196590751763
of 1.2855361232614977
and 1.2853774056335696
a 1.2765204940283563
in 1.2737363952337173
you 1.2380186056238358
for 1.2352154047456279
is 1.2260564526118427
on 1.218803879953794
new 1.21827311159241
s 1.215043267169989
by 1.200144482032648
york 1.1944926274732255
i 1.1940401847399407
with 1.1928693613708015
that 1.183154406423152
it 1.178874893334453
this 1.1754560794444615
your 1.175390010956249

# results from (analysis.RegexTokenizer() | analysis.LowercaseFilter() | analysis.StopFilter())

new 1.238054351312873
york 1.2138877407557376
was 1.1528091018625797
city 1.1521471877477851
all 1.1282244248428333
photos 1.123346974800077
flickr 1.120673627748619
de 1.1151258493496314
my 1.1135350567601834
but 1.0760340756525266
one 1.0677393268888629
art 1.0618331867941
has 1.0591524293950991
orleans 1.052347558290222
bridge 1.0393962386859077
world 1.035395129299458
la 1.0321754629743232
there 1.0315826984389482
their 1.0279772967904774
out 1.0169593132866073

Since the first analyzer RegexTokenizer tokenizes every word, second one RegexTokenizer and LowercaseFilter - 'lowercases' every word and the third one (RegexTokenizer + LowercaseFilter + StopFilter) cleans up all stop words, the intersection of all three results equals to an empty set (according to given documents)

# results from analysis.StemmingAnalyzer()

new 1.2405431017431423
york 1.2133945420217498
photo 1.168559113720724
citi 1.1626825869580462
wa 1.1526473615692756
all 1.1294746025111846
de 1.1279497413746589
flickr 1.1201340454080517
my 1.1128497272837399
us 1.1110749497463814
art 1.0887751522647737
but 1.0753718263005863
on 1.072072776527678
ha 1.0652208591072942
bridg 1.0649864005613447
la 1.0570173212879994
view 1.0534945496798322
orlean 1.0516998868974075
time 1.044017417581081
world 1.0359112400364108

StemmingAnalyzer() filters on base words, if we compare it's results with RegexTokenizer, stemming analyzer also lowercases words, and gives a neat list of words (also ignores stop words?)

Which top terms seem to be the most descriptive of the content of the web pages? Why?

        According to the results from RegexTokenizer, only 'York' suggests that it's a proper noun, so the page could be about York city in Pennsylvania, New York, or York college, etc.

        Results from RegexTokenizer() + analysis.LowercaseFilter don't give a clear understanding about the page.

        (analysis.RegexTokenizer()  analysis.LowercaseFilter() |analysis.StopFilter()) - knowing that lowercase and stop filter was applied on these words, we can assume that 'york', 'orleans', 'la' are proper nouns and webpages can tell about those places; 'flickr' is another unique name for image web service. Besides proper noun, any common, countable, uncountable, concrete, abstract noun from this list can tell us a little about the description of the content of the page.

'de' term occurs in the compund (analysis.RegexTokenizer() analysis.LowercaseFilter() | analysis.StopFilter()) filter and in analysis.StemmingAnalyzer().
