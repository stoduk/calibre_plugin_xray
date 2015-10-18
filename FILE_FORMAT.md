# Summary
This tool aims to produce a series of meta-data files to be interpreted by the Kindle when reading a book.  This file aims to describe what the format is, with the hope the tool can create this!

# X-Ray
The X-Ray file is the one that the reader will see when selecting the X-Ray button while reading a book.  It will show various highlights, character summaries, frequency of a character being mentioned, etc.

## Versions
There have been two versions of this file, the old version which is JSON data, and the new version which is an SQLite DB.  The information in both is roughly equivalent.
XXX are there any differences?  I think so - the location data we have seems to be what JSON format wants, which is not what SQLite wants.
XXX when is old vs. new used?  .NET app guys probably know..

## Naming
XRAY.entities.{ASIN}.asc

## Contents
### JSON
TBC

### SQLite
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
* loc_label INTEGER: XXX unknown, an integer.  Point in to the book for character info?
* type INTEGER: 0=??? (there seems to be an 'empty' first row always), 1=character, 2=topic (anything else!)
* count INTEGER: number of times the entitiy is seen, should match an appropriate query on `occurrence` table
* has_info_card TINYINT: shows if the entity should appear in the entity list in X-Ray (only 0 for the empty row, as far as I've seen)

#### `entity_description` table

* text TEXT: Description of the entity (eg. character bio)
* source_wildcard TEXT: ??? Seems to be repetition of `entity.label`, not sure when one would be used over the other
* source INTEGER: ??? 
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
* image TEXT: XXX
* related_entities TEXT: entities (ie. `entity.id`) that are in this excerpt.  Not clear why this duplication is needed, `entity_excerpt` tables covers it.
* goto INTEGER: XXX seems to be NULL for the book I have

#### `book_metadata` table
#### `source` table
Not a scooby..  Seems to be some 

* id INTEGER PRIMARY KEY
* label INTEGER
* url INTEGER
* license_label INTEGER
* license_url INTEGER

#### `string` table
Clueless.. Seems to be a bunch of locale based strings, not sure where these are used.  (ie. for a given `id` we'll have multiple language ('en', 'jp', etc.) and text pairs).

* id INTEGER
* language TEXT
* text TEXT

#### `type` table
* id INTEGER PRIMARY KEY: unique index
* label INTEGER: XXX 
* singular_label INTEGER
* icon INTEGER: Select the icon in X-Ray view for this type (1=person logo, used for `entity.type=1` type; 2=book logo, used for `entity.type=2` type) 
* top_mentioned_entities TEXT: comma-separated ordered list of entities to appear in X-Ray summary (not all entities would need to appear here, some could just give information when highlighted in book)
