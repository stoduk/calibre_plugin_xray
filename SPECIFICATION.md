* [Summary](#summary)
* [X-Ray](#x-ray)
* [Author Profile](#author-profile)
* [Start Actions](#start-actions)
* [End Actions](#end-actions)

# Summary
This tool aims to produce a series of meta-data files to be interpreted by the Kindle when reading a book.  This file aims to describe what the format is, with the hope the tool can create this!

## Versions
There have been two major versions of these file formats - the original format, and the "new" format.  The new format appeared in firmware version 5.6 and upwards.  The two main changes in the new file format were the move from JSON to SQLite3 format for X-Ray data, and the addition of the Start Actions file.

## Device Support

<table>
<tr><th>Generation</th><th>Model</th><th>Earliest firmware</th><th>Latest firmware</th><th>Supports touch?</th><th>Supports X-Ray?</th><th>Support new format</th></tr>
<tr><td>3</td><td>Kindle Keyboard</td><td>???</td><td>3.4.2</td><td>No</td><td></td><td></td></tr>
<tr><td>4</td><td>Kindle</td><td>??? [as 5th gen?]</td><td>4.1.3</td><td>No</td><td></td><td></td></tr>
<tr><td>4</td><td>Kindle Touch</td><td>&lt; 5.1</td><td>5.3.7.3</td><td>Yes</td><td>Yes (first)</td><td>No</td></tr>
<tr><td>5</td><td>Kindle</td><td>&lt;4.1.0</td><td>4.1.3</td><td>No</td><td>No</td><td>-</td></tr>
<tr><td>5</td><td>Kindle Paperwhite v1</td><td>&lt;=5.3.0</td><td>5.6.1.1</td><td>Yes</td><td>Yes</td><td>Some</td></tr>
<tr><td>6</td><td>Kindle Paperwhite v2</td><td>&lt;=5.4.2</td><td>5.6.5</td><td>Yes</td><td>Yes</td><td>Some</td></tr>
<tr><td>7</td><td>Kindle</td><td>???</td><td>5.6.5</td><td>Yes (implicit)</td><td>Yes</td><td>Always?</td></tr>
<tr><td>7</td><td>Kindle Voyage</td><td>???</td><td>5.6.5</td><td>Yes</td><td>Yes</td><td>Always?</td></tr>
<tr><td>7</td><td>Kindle Paperwhite v3</td><td>???</td><td>5.6.5</td><td>Yes</td><td>Yes</td><td>Always?</td></tr>
</table>

# X-Ray
The X-Ray file contains the information that the reader will see when selecting the X-Ray button while reading a book, or when highlighting a character/term in that book.  It will show various highlights, character summaries, frequency of a character being mentioned, etc.

## Versions
There have been two versions of this file, the old version which is JSON data, and the new version which is an SQLite DB.  The information in both is roughly equivalent.
XXX are there any differences?  I think so - the location data we have seems to be what JSON format wants, which is not what SQLite wants.
XXX when is old vs. new used?  .NET app guys probably know..

## Naming
XRAY.entities.{ASIN}.asc

## Contents
### Old format: JSON
TBC

### New format: SQLite
The file is an sqlite3 format database, with this schema:
```
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE type(id INTEGER, label INTEGER, singular_label INTEGER, icon INTEGER, top_mentioned_entities TEXT, PRIMARY KEY(id));
CREATE TABLE string(id INTEGER, language TEXT, text TEXT);
CREATE TABLE source(id INTEGER, label INTEGER, url INTEGER, license_label INTEGER, license_url INTEGER, PRIMARY KEY(id));
CREATE TABLE occurrence(entity INTEGER, start INTEGER, length INTEGER);
CREATE TABLE excerpt(id INTEGER, start INTEGER, length INTEGER, image TEXT, related_entities TEXT, goto INTEGER, PRIMARY KEY(id));
CREATE TABLE entity_excerpt(entity INTEGER, excerpt INTEGER);
CREATE TABLE entity_description(text TEXT, source_wildcard TEXT, source INTEGER, entity INTEGER, PRIMARY KEY(entity));
CREATE TABLE entity(id INTEGER, label TEXT, loc_label INTEGER, type INTEGER, count INTEGER, has_info_card TINYINT, PRIMARY KEY(id));
CREATE TABLE book_metadata(srl INTEGER, erl INTEGER, has_images TINYINT, has_excerpts TINYINT, show_spoilers_default TINYINT, num_people INTEGER, num_terms INTEGER, num_images INTEGER, preview_images TEXT);
CREATE INDEX idx_occurrence_start ON occurrence(start ASC);
CREATE INDEX idx_entity_type ON entity(type ASC);
CREATE INDEX idx_entity_excerpt ON entity_excerpt(entity ASC);
COMMIT;
```
#### `entity` table
Describes all entities in the book (ie. characters, locations, etc.).  

* id INTEGER PRIMARY KEY: unique ID
* label TEXT: Character's name, for example.
* loc_label INTEGER: XXX unknown, an integer.  Only seen it used for the first (zero id/null label) entry.
* type INTEGER: type.id defining what sort of entity this is.  Unclear what meaning of zero is here, which is only used in the always-present first null entry
* count INTEGER: number of times the entitiy is seen, should match an appropriate query on `occurrence` table
* has_info_card TINYINT: shows if the entity should appear in the entity list in X-Ray (only 0 for the empty row, as far as I've seen)

#### `entity_description` table

* text TEXT: Description of the entity (eg. character bio, term description)
* source_wildcard TEXT: String which combined with this entitiy's source URL will provide a link to the full entitiy description
* source INTEGER: source.id for this source.  Unknown if there are any assumptions here (eg. 0=Kindle Store)
* entity INTEGER PRIMARY KEY: entity (ie. `entity.id`)

#### `entity_excerpt` table
Maps between entities and excerpts.

* entity INTEGER: an entity (ie. `entity.id`)
* excerpt INTEGER: an excerpt (ie. `excerpt.id`)

#### `occurrence` table
Describes an occurrence of a particular entity in the book (ie. when a particular character, place, or concept is read about).

* entity INTEGER: ID of the entity (ie. `entity.id`)
* start INTEGER: location in the book
* length INTEGER: length of the entity (eg. length of the name).  This is used for highlighting the matching entity by the Kindle.

#### `excerpt` table
An excerpt from the book which contains one or more entities (detained in `entity_excerpt` table).

* id INTEGER PRIMARY KEY: unique ID for excerpt
* start INTEGER: start location
* length INTEGER: length of excerpt
* image TEXT: Normally null.  Can be a string that points to an image in the book (eg. 'kindle:embed:0001?mime=image/gif')
* related_entities TEXT: comma separated list of entities (ie. `entity.id`) that are in this excerpt.  [duplicate of information in `entity_excerpt` table]
* goto INTEGER: Normally null.  If 'image' exists then this is the location of the image in the book.

#### `book_metadata` table
Book meta-data.

* srl INTEGER: Start RL - seems to be the byte location of the start of the book (ie. beginning of first chapter), ie. excluding title pages, TOC, etc.
* erl INTEGER: End RL - seems to be the byte location of the end of the book (ie. end of last chapter), ie. excluding index, etc.
* has_images TINYINT: Always zero/False.  Would this indicate inline images or similar?  Need example book with this set.
* has_excerpts TINYINT: Always one/True.  We have excerpts!
* show_spoilers_default TINYINT: Always zero/False.  Hide spoilers.  XXX How are spoilers enabled/identified?
* num_people INTEGER: Count of people (ie. entities where type is 1)
* num_terms INTEGER: Count of people (ie. entities where type is 2)
* num_images INTEGER: Number of images referenced in 'preview_images' (if 'has_images' is 1)
* preview_images TEXT: Comma separated list of integers of excerpt.id for excerpts that have an associated image.  

#### `source` table
Data source information - each entity has a data source specified.

* id INTEGER PRIMARY KEY: unique id for the source.  Referenced in entity_description.source.
* label INTEGER: string.id for the name of this source.
* url INTEGER: string.id defining the URL for this source (eg. 'store://%s' for Kindle Store, 'http://en.wikipedia.org/wiki/%s' for Wikipedia).
* license_label INTEGER: string.id for the license name for this source.
* license_url INTEGER: string.id for the license URL for this source.

#### `string` table
Various strings, with translations.  Used for referencing sources (ie. source.label, source.license_label, and source.license_url).

* id INTEGER: unique ID (unique for a given string, there will normally be one entry per language).
* language TEXT: language string (eg. 'en').
* text TEXT: String being defined (can be a source's name, source's URL, source license's name or URL).

#### `type` table
* id INTEGER PRIMARY KEY: unique index, referenced in entity.type
* label INTEGER: string.id for type's description of multiple items of this type (eg. "People") 
* singular_label INTEGER: string.id for type's description of a single item if this type (eg. "Person")
* icon INTEGER: Select the icon in X-Ray view for this type (1=person logo; 2=book logo) 
* top_mentioned_entities TEXT: comma-separated ordered list of entities to appear in X-Ray summary (not all entities would need to appear here, some could just give information when highlighted in book)

# Start Actions
The Start Actions file describes what is shown to the reader when first opening a book, or when selecting the 'About This Book' option from the menu.  It contains a summary of the book, details of the author, other books from that author, etc. - basically the digital equivalent of what would be printed on the back cover of a book.

## Versions
This only exists in new format.

## Naming
StartActions.data.{ASIN}.asc

## Contents
### Format: JSON
The top level keys are all containers for a lot of information, so a section on each below.  The keys are bookInfo, data, layouts, widgets - the values are nested data.

#### bookInfo
Top level book information, all obvious
##### `bookInfo.asin`: String(ASIN)
##### `bookInfo.class`: String("BookInfo")
##### `bookInfo.contentType`: String("EBOK")
- could this be other things, eg. for audio books or videos?

##### `bookInfo.erl`: Int(-1)
- ERL or -1 if ERL unknown ???

##### `bookInfo.imageUrl`: String(URL for book cover)
- unknown if image is a specific size, colour depth, etc.  For sample book I had a 226x340 JPEG.

##### `bookInfo.refTagSuffix`: String(???)
- TBC

##### `bookInfo.timestamp`: Int(timestamp)
- Not sure what format this is, couldn't trivially decode in python.  Could just be used for the sort order on Kindle (ie. sort by: Recent)

#### data
More containers, so split them out.  The keys are currentBook. welcomeText, readingTime, readingPages, popularHighlightsText, authorRecs, bookDescription, authorBios, grokShelfInfo

#### data.currentBook
##### `data.currentBook.asin`: String(ASIN)
##### `data.currentBook.description`: String(Description)
##### `data.currentBook.title`: String(Title)
##### `data.currentBook.imageUrl`: String(URL)
- same as bookInfo.imageUrl

##### `data.currentBook.hasSample`: Bool
##### `data.currentBook.amazonRating`: Decimal(Rating)
##### `data.currentBook.numberOfReviews`: Int(Rating count)
##### `data.currentBook.authors`: List(String(author)..)
##### `data.currentBook.class`: String("featuredRecommendation")

#### data.welcomeText
Hardcoded selection of text (in various language) that are shown when "About this book" feature is used.  Odd to hardcode it, and in every book!
#### data.readingTime
Reading time both as numbers ("hours" and "minutes" keys), and as a set of strings ("formattedTime.{countrycode}")
##### `data.readingTime.hours`: Int(hours)
##### `data.readingTime.minutes`: Int(minutes)
##### `data.readingTime.formattedTime`: Dict(country code: human readable duration)
#### data.readingPages
##### `data.readingPages.class`: String("pages")
##### `data.readingPages.pagesInBook`: Int(pages in book)
#### data.popularHighlightsText
##### `data.popularHighlightsText.class`: String("dynamicText")
##### `data.popularHighlightsText.localizedText`: Dict(country code: human readable string)
- eg. u'1,266 passages have been highlighted 19,446 times'

#### data.authorRecs
##### `data.authorRecs.class`: String("recommendationList")
##### `data.authorRecs.localizedText`: List(recommendations)
- each entry is Dict containing asin, authors, class("recommendation"), hasSample, imageUrl, title

#### data.bookDescription
Exactly the same as data.currentBook it seems.  Always true?

#### data.authorBios
##### `data.authorBios.authors`: List(author bios)
- author bios is Dict containing asin, bio, class("authorBio"), imageUrl, name
- imageUrl is 250Hx365W image

##### `data.authorBios.class`: String("authorBiosList")
#### data.grokShelfInfo
##### `data.grokShelfInfo.asin`: String(ASIN)
##### `data.grokShelfInfo.class`: String("goodReadsShelfInfo")
##### `data.grokShelfInfo.shelves`: List(String(shelf))
- eg. "to-read"

# Author Profile
The Author Profile file describes what is shown to the reader when they choose to view the author's details when viewing a book.

## Versions
Only one version.

## Naming
AuthorProfile.profile.{ASIN}.asc

## Contents
### Format: JSON
Top level keys: a, d, o, u

#### a
Value is the ASIN.

#### d
Value is a timestamp.

#### o
Value is a list of other books, each item in the list being a Dict:

##### `o.a`: String(ASIN)
##### `o.e`: hard coded integer, 1.  ??Enable flag??
##### `o.t`: Title

#### u
Value is a list of Authors, with each item in the list being a Dict:

##### a
Value is a string containing the Author's ASIN.

##### b
Value is a string containing a biography of the author.

##### i
Value is a Base64 encoded greyscale image of the author.  278 pixels high x 185 pixels wide.

##### l
Value is a list, with each entry being a string containing the ASIN of a book.

##### n
Value is Author's name.

##### y
Value is an integer, the hight of the author's image.

# End Actions
## Versions
There have been two major versions of this file, the old version was encoded in XML, the new version is encoded in JSON.

## Naming
EndActions.data.{ASIN}.asc

## Contents
### Old format: XML
TBC.  Contains similar data, but much less of it - eg. no imageUrl or descriptions for recommendations (does it not show those, or does it grab them separately?)

Some notes:
- rather than timestamp it has date/time I think (s=readable datetime, zzz=timezone info ?)

### New format: JSON
There are four top level keys, two whose values are lists of Dict (widgets, layouts), two whose values are just a Dict (bookInfo, data)

#### bookinfo
Data for this current book, no other books are referenced, some external data is needed.

bookinfo.class: String("bookInfo")
bookinfo.asin: String(ASIN)
bookinfo.contentType: String("EBOK")
bookinfo.timestamp: Int(timestamp)
bookinfo.regTagSuffix: String(???)
bookinfo.imageUrl: String(image url)
bookinfo.embeddedId: String("{database name}:{unique id}")
- example: "A_Christmas_Carol:BA862274"
- database name and unique ID are both from the MOBI file (unique ID is not ASIN, some just look a bit like them).  Not sure what happens if these values don't match what a kindle edition would have..
bookinfo.erl: Int(erl)

#### data
Data for this book and other related books (either recommendations, or cited books), so plenty of external data needed.

All the rating related data should not be added, as the device will add it when a rating is given (indeed, prepopulating it with rating information using Amazon's average rating is perhaps both confusing and *may* interfere with submitting your own rating).

##### `data.nextBook`: OPTIONAL Dict(???)
- was empty in my example.  Does this link to next book in series in bookshop?  Or perhaps it could even open the next one on the device.
- XXX need to find an example where this works..
- GUI handles this, I imagine it is dumping an entry as for the other recommendation sections, but for the next book in the series.

##### `data.customerProfile`: Dict()
##### `data.customerProfile.class`: String("customerProfile")
##### `data.customerProfile.penName`: String(???)
##### `data.customerProfile.realName`: String(???)
- seem to be full name, and first name (or perhaps any nickname).  
- XXX Where is this from?  Amazon?  Goodreads?
- XXX What is it used for and does it matter?  Could make it a config option to let users set what they want.  Ah, GUI seems to do exactly that.

##### `data.authorBios`: Dict()
##### `data.authorBios.class`: String("authorBio")
##### `data.authorBios.authors`: List(Dict(class="authorBioList", asin, name, bio, imageUrl))

##### `data.authorRecs`: Dict()
##### `data.authorRecs.class`: String("authorBio")
##### `data.authorRecs.recommendations`: List(Dict(class="featuredRecommendation", asin, title, authors[], imageUrl, hasSample, description, amazingRating, numberOfReviews))

##### `data.customerWhoBoughtRecs`: Dict()
##### `data.customerWhoBoughtRecs.class` = String("featuredRecommendationList")
##### `data.customerWhoBoughtRecs.recommendations` = List(Dict(class="featuredRecommendation", asin, title, authors[], imageUrl, hasSample, description, amazonRating, numberOfReviews))

##### `data.publicSharedRating`: OPTIONAL KINDLE-ADDS Dict()
##### `data.publicSharedRating.class`: String("publicSharedRating")
##### `data.publicSharedRating.timestamp`: Int(timestamp)
##### `data.publicSharedRating.value`: Int(rating)

##### `data.rating`: OPTIONAL KINDLE-ADDS Dict()
##### `data.rating.class`: String('personalizationRating')
##### `data.rating.timestamp`: Int(timestamp)
##### `data.rating.value`: Int(rating)

##### `data.goodReadsReview`: OPTIONAL KINDLE-ADDS Dict()
##### `data.goodReadsReview.class`: String('goodReadsReview')
##### `data.goodReadsReview.rating`: Int(rating)
##### `data.goodReadsReview.reviewId`: String('NoReviewId')
##### `data.goodReadsReview.submissionDateMs`: Int(timestamp of review in ms since epoch)

#### layouts
A list of layouts, each being a single Dict.  Seems to be two rather similar looking Dict's in my example, not sure what the difference in use is.

Might be useful to look closer at this, but for now it seems that the GUI doesn't modify this at all - so could follow suit for now.

XXX figure this out
#### widgets
A list of widgets, each being a single Dict.  Minimal set of keys is id/class/metricsTag, there are plenty of optional ones, especially where internationalised strings are used.

As with 'layouts', could copy wholesale, as the GUI does.

XXX figure this out
