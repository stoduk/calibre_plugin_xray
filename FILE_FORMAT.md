# Summary
This tool aims to produce a series of meta-data files to be interpreted by the Kindle when reading a book.  This file aims to describe what the format is, with the hope the tool can create this!

# X-Ray
The X-Ray file is the one that the reader will see when selecting the X-Ray button while reading a book.  It will show various highlights, character summaries, frequency of a character being mentioned, etc.

## Versions
There have been two versions of this file, the old version which is JSON data, and the new version which is an SQLite DB.  The information in both is roughly equivalent.
XXX are there any differences?  I think so - the location data we have seems to be what JSON format wants, which is not what SQLite wants.

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
#### ```entity``` table
Describes all entities in the book (ie. characters, locations, etc.).  

#### ```book_metadata``` table
#### ```entity_excerpt``` table
#### ```source``` table
#### ```excerpt``` table
#### ```string``` table
#### ```entity_description``` table
#### ```occurrence``` table
#### ```type``` table

