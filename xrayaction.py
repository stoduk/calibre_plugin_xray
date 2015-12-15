# -*- coding: utf-8 -*-

# Credits:
# XRay generation code based on code at http://www.mobileread.com/forums/showthread.php?t=157770
# Plug-in structure based on APNX Generator
# Icon from http://openclipart.org/image/128px/svg_to_png/32149/HandXray.png
# Unpack code from KindleUnpack

from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__ = 'GPL 3'
__copyright__ = '2012-15, Matthew Wilson <matthew@mjwilson.demon.co.uk>'
__docformat__ = 'restructuredtext en'

import os, time, re, errno, io
import tempfile, shutil
import cStringIO
from array import *
import html5lib
from lxml.cssselect import CSSSelector
from threading import Thread
from Queue import Queue
import httplib, socket # just for urllib2.urlopen() exceptions

try:
    from PyQt4.Qt import Qt, QMenu, QFileDialog, QIcon, QPixmap, QMessageBox, QInputDialog, QDialog
except ImportError:
    from PyQt5.Qt import Qt, QMenu, QFileDialog, QIcon, QPixmap, QMessageBox, QInputDialog, QDialog

from calibre import sanitize_file_name
from calibre.gui2 import Dispatcher, warning_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.library.save_to_disk import get_components
from calibre.library.save_to_disk import config
from calibre.ptempfile import PersistentTemporaryFile
from calibre.utils.filenames import shorten_components_to
from calibre.utils.ipc.job import BaseJob
from calibre_plugins.xray_generator.xray_ui import Ui_XRay
from calibre_plugins.xray_generator.xray_config import prefs
import calibre_plugins.xray_generator.lib.kindleunpack as _ku
from calibre_plugins.xray_generator.xray_utils import OrderedDefaultdict

class XRayAction(InterfaceAction):

    name = 'XRay'
    action_spec = (_('XRay'), None, None, None)
    
    def genesis(self):
        self.xray_mixin = XRayMixin(self.gui)
        # Read the icons and assign to our global for potential sharing with the configuration dialog
        # Assign our menu to this action and an icon
        self.qaction.setIcon(get_icons('images/plugin_xray_xray.png'))
        self.qaction.triggered.connect(self.generate_selected)
        self.xray_menu = QMenu()
        self.load_menu()
        
    def load_menu(self):
        self.xray_menu.clear()
        self.xray_menu.addAction(_('Generate from selected books...'), self.generate_selected)
        #self.xray_menu.addAction(_('Generate from file...'), self.generate_file)
        self.qaction.setMenu(self.xray_menu)

    def generate_selected(self):
        self.xray_mixin.genesis()

        #xraydir = unicode(QFileDialog.getExistingDirectory(self.gui, _('Directory to save XRay file'), self.gui.library_path, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        #if not xraydir:
        #    return
            
        #unpackdir = unicode(QFileDialog.getExistingDirectory(self.gui, _('Directory to unpack files into'), self.gui.library_path, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        #if not unpackdir:
        #    return
        
        self._generate_selected()
        
    def _generate_selected(self, ids=None, do_auto_convert=False):
        if not ids:
            ids = [self.gui.library_view.model().id(r) for r in self.gui.library_view.selectionModel().selectedRows()]
        
        _files, _auto_ids = self.gui.library_view.model().get_preferred_formats_from_ids(ids, ['mobi', 'azw', 'prc'], exclude_auto=do_auto_convert)
        if do_auto_convert:
            ok_ids = list(set(ids).difference(_auto_ids))
            ids = [i for i in ids if i in ok_ids]
        else:
            _auto_ids = []
            
        metadata = self.gui.library_view.model().metadata_for(ids)
        ids = iter(ids)
        imetadata = iter(metadata)

        bad, good = [], []
        for f in _files:
            mi = imetadata.next()
            id = ids.next()
            if f is None:
                bad.append(mi.title)
            else:
                good.append((f, mi, id))

        template = config().parse().template
        if not isinstance(template, unicode):
            template = template.decode('utf-8')

        for f, mi, id in good:
            components = get_components(template, mi, f)
            if not components:
                components = [sanitize_file_name(mi.title)]

            def remove_trailing_periods(x):
                ans = x
                while ans.endswith('.'):
                    ans = ans[:-1].strip()
                if not ans:
                    ans = 'x'
                return ans
            
            self.xray_mixin.generate_xray(mi.title, f, id)

        if bad:
            bad = '\n'.join('%s'%(i,) for i in bad)
            d = warning_dialog(self.gui, _('No suitable formats'),
                    _('Could not generate an XRay for the following books, '
                'as no suitable formats were found. Convert the book(s) to '
                'MOBI first.'
                ), bad)
            d.exec_()
    
    def generate_file(self):
        self.xray_mixin.genesis()
        
        filename = unicode(QFileDialog.getOpenFileName(self.gui, _('MOBI file for generating XRay'), self.gui.library_path, 'MOBI files (*.mobi *.azw *.prc)'))
        if not filename:
            return

        xraydir = unicode(QFileDialog.getExistingDirectory(self.gui, _('Directory to save XRay file'), self.gui.library_path, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        if not xraydir:
            return
        
        unpackdir = unicode(QFileDialog.getExistingDirectory(self.gui, _('Directory to unpack files into'), self.gui.library_path, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        if not unpackdir:
            return
        
        self.xray_mixin.generate_xray("specified file", filename, None)
        
    def show_dialog(self):
        
        ##
        ## ARTWTF - why is this here, what is it doing?  DemoDialog shouldn't be working
        ## Not being called ATM - but I probably want ot be able to call config from my dialog, so need to replicate this basics..
        ##
        
        # The base plugin object defined in __init__.py
        base_plugin_object = self.interface_action_base_plugin
        # Show the config dialog
        # The config dialog can also be shown from within
        # Preferences->Plugins, which is why the do_user_config
        # method is defined on the base plugin class
        do_user_config = base_plugin_object.do_user_config
    
        # self.gui is the main calibre GUI. It acts as the gateway to access
        # all the elements of the calibre user interface, it should also be the
        # parent of the dialog
        d = DemoDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()
        
    def apply_settings(self):
        #
        # Nothing to do currently, 'prefs' will be updated already
        #
        print(prefs) # ARTHACK: this dumps to syslog, get rid of this once debugged

class XRayJob(BaseJob):
    
    def __init__(self, callback, description, job_manager, filename, xraydir, rawml, asin, database, uniqid, shelfariUrl, wikiUrl, aliasFile, offset, tempdir, newFormat):
        BaseJob.__init__(self, description)
        self.exception = None
        self.job_manager = job_manager
        self.args = (filename, xraydir, rawml, asin, database, uniqid, shelfariUrl, wikiUrl, aliasFile, offset, tempdir, newFormat)
        self.callback = callback
        self.log_path = None
        self._log_file = cStringIO.StringIO()
        self._log_file.write(self.description.encode('utf-8') + '\n')

    @property
    def log_file(self):
        if self.log_path is not None:
            return open(self.log_path, 'rb')
        return cStringIO.StringIO(self._log_file.getvalue())

    def start_work(self):
        self.start_time = time.time()
        self.job_manager.changed_queue.put(self)

    def job_done(self):
        self.duration = time.time() - self.start_time
        self.percent = 1
        # Dump log onto disk
        lf = PersistentTemporaryFile('xray_generate_log')
        lf.write(self._log_file.getvalue())
        lf.close()
        self.log_path = lf.name
        self._log_file.close()
        self._log_file = None

        self.job_manager.changed_queue.put(self)

    def log_write(self, what):
        self._log_file.write(what)

class XRayGenerator(Thread):
    
    def __init__(self, job_manager):
        Thread.__init__(self)
        self.daemon = True
        self.jobs = Queue()
        self.job_manager = job_manager
        self._run = True
        self.xray_builder = XRayBuilder()
        
    def stop(self):
        self._run = False
        self.jobs.put(None)
        
    def run(self):
        while self._run:
            try:
                job = self.jobs.get()
            except:
                break
            if job is None or not self._run:
                break
            
            failed, exc = False, None
            job.start_work()
            if job.kill_on_start:
                self._abort_job(job)
                continue
            
            try:
                self._generate_xray(job)
            except Exception as e:
                if not self._run:
                    return
                import traceback
                failed = True
                exc = e
                job.log_write('\nXRAY generation failed...\n')
                job.log_write(traceback.format_exc())

            if not self._run:
                break

            job.failed = failed
            job.exception = exc
            job.job_done()
            try:
                job.callback(job)
            except:
                import traceback
                traceback.print_exc()

    def _abort_job(self, job):
        job.log_write('Aborted\n')
        job.failed = False
        job.killed = True
        job.job_done()

    def _generate_xray(self, job):

        filename, xraydir, rawml, asin, database, uniqid, shelfariUrl, wikiUrl, aliasFile, offset, tempdir, newFormat = job.args
        if not filename:
            raise Exception(_('No filename specified.'))
        if not rawml:
            raise Exception(_('No rawml specified.'))
        if not xraydir:
            raise Exception(_('No XRay directory specified.'))
        if not asin:
            raise Exception(_('No ASIN specified.'))
        if len(asin) != 10: # can I compare to the DB ID and say if that is the problem?
            raise Exception(_('ASIN is invalid (should be 10 characters): %s' % (asin)))
        if asin[0] != 'B':
            raise Exception(_('ASIN is invalid (Kindle E-books look like B012345678)'))
        if not database:
            raise Exception(_('No information available to generate GUID.'))
        if not uniqid:
            raise Exception(_('No uniqid specified'))
        if not shelfariUrl:
            raise Exception(_('No Shelfari URL specified.'))
        if not os.path.exists(xraydir):
            os.makedirs(xraydir)

        job.notifications.put((0.00, "Starting"))

        data = XRayData()
        job.log_write ("Loading Shelfari from " + shelfariUrl + "...\n")
        data.readShelfari (shelfariUrl, job)

        if wikiUrl:
            job.notifications.put((0.25, "Read Shelfari"))
            job.consume_notifications()
            job.log_write ("Loading Wikipedia from " + wikiUrl + "...\n")
            data.readWikipedia (wikiUrl)
            job.notifications.put((0.50, "Read Wikipedia"))
        else:
            job.notifications.put((0.50, "Read Shelfari"))
            job.consume_notifications()

        data.processAliases (job, aliasFile)
        job.log_write ("Parsing book...\n")
        data.rawml (rawml, offset, job)
        job.notifications.put((0.75, "Parsed book"))
        job.consume_notifications()
        job.log_write ("Parsed.\n")
        self.xray_builder.write_xray(filename, xraydir, asin, database, uniqid, data, job, newFormat)

        if tempdir is not None:
            try:
                shutil.rmtree(tempdir)
            except Error as e:
                job.log_write ("Unexpected error clearing out temporary directory " + e)
        
    def generate_xray(self, callback, title, filename, xraydir, rawml, asin, database, uniqid, shelfariUrl, wikiUrl, aliasFile, offset, tempdir, newFormat):

        description = _('Generating XRay for %s') % (title)
        job = XRayJob(callback, description, self.job_manager, filename, xraydir, rawml, asin, database, uniqid, shelfariUrl, wikiUrl, aliasFile, offset, tempdir, newFormat)
        self.job_manager.add_job(job)
        self.jobs.put(job)


class XRayMixin(object):

    def __init__(self, gui):
        self.gui = gui
    
    def genesis(self):
        '''
        Genesis must always be called before using an XRayMixin object.
        Plugins are initalized before the GUI initalizes the job_manager.
        We cannot create the XRayGenerator during __init__. Instead call
        genesis before using generate_xray to ensure the XRayGenerator
        has been properly created with the job_manager.
        '''
        self.db = self.gui.current_db
        if not hasattr(self.gui, 'xray_generator'):
            self.gui.xray_generator = XRayGenerator(self.gui.job_manager)

    def generate_xray(self, title, filename, id):
        from calibre.ebooks.metadata.meta import get_metadata
        from calibre.ebooks.metadata.mobi import MetadataUpdater
        from struct import unpack

        if not self.gui.xray_generator.is_alive():
            self.gui.xray_generator.start()

        file = open(filename, 'r+b')
        ext  = os.path.splitext(filename)[-1][1:].lower()
        mi = get_metadata(file, ext)

        mu = MetadataUpdater (file)
        db = mu.data[0:32]
        db = re.sub ( r'\u0000', '', db)
        uniqid, = unpack ('>I', mu.record0[32:36])

        docType = mu.original_exth_records.get(501, None)
        if docType != 'EBOK':
            d = warning_dialog(self.gui, _('Bad document type'),
                    _('Need a document type of EBOK for XRay, but got type of ' + str(docType)), mi.title.decode('utf-8'))
            d.exec_()

        try:
            asin = mu.original_exth_records[113]
        except KeyError:
            d = warning_dialog(self.gui, _('No ASIN'),
                    _('Could not find ASIN in book'), mi.title.decode('utf-8'))
            d.exec_()
            return

        defaultShelfariUrl = ''
        if id is not None:
            defaultShelfariUrl = self.db.get_custom_book_data ( id, 'xray.url.shelfari');
            if defaultShelfariUrl is None:
                defaultShelfariUrl = ''

        defaultWikiUrl = ''
        if id is not None:
            defaultWikiUrl = self.db.get_custom_book_data ( id, 'xray.url.wikipedia');
            if defaultWikiUrl is None:
                defaultWikiUrl = ''

        defaultAliasesFile = ''
        if id is not None:
            defaultAliasesFile = self.db.get_custom_book_data ( id, 'xray.file.aliases');

        defaultXrayDir = ''
        if id is not None:
            defaultXrayDir = self.db.get_custom_book_data ( id, 'xray.dir.xray');

        defaultNewFormat = prefs['newFormat']    

        dialog = StartDialog(self.gui, defaultShelfariUrl, defaultWikiUrl, defaultAliasesFile, defaultXrayDir, defaultNewFormat)
        result = dialog.exec_()
        if not result:
            return

        values = dialog.getValues()

        shelfariUrl = values[0]
        wikiUrl     = values[1]
        aliasFile   = values[2]
        offset      = values[3]
        xraydir     = values[4]
        unpackdir   = values[5]
        newFormat   = values[6]

        #d = warning_dialog(self.gui, _('XRay type'), _('newFormat set to ' + str(newFormat)), 'Xray type'.decode('utf-8'))
        #d.exec_()

        tempdir = None
        if not unpackdir:
            tempdir = tempfile.mkdtemp()
            unpackdir = tempdir

        if id is not None:
            self.db.add_custom_book_data ( id, 'xray.url.shelfari', str(shelfariUrl));
        if xraydir is not None and id is not None:
            self.db.add_custom_book_data ( id, 'xray.dir.xray', str(xraydir));
        if aliasFile is not None and id is not None:
            self.db.add_custom_book_data ( id, 'xray.file.aliases', aliasFile )
        if wikiUrl is not None and id is not None:
            self.db.add_custom_book_data ( id, 'xray.url.wikipedia', str(wikiUrl));

        prefs['newFormat'] = newFormat
        
        _ku.unpackBook(filename, unpackdir, dodump=True, dowriteraw=True)

        fn = _ku.fileNames (filename, unpackdir)
        k8dir = os.path.join (unpackdir, 'mobi8')
        if os.path.exists (k8dir):
            mobidir = k8dir
        else:
            mobidir = fn.mobi7dir
        rawml = os.path.join (mobidir, fn.getInputFileBasename() + '.rawml')

        self.gui.xray_generator.generate_xray(Dispatcher(self.xray_generated), title, filename, xraydir, rawml, asin, db, uniqid, shelfariUrl, wikiUrl, aliasFile, offset, tempdir, newFormat)
        self.gui.status_bar.show_message(_('Generating XRay for %s') % (title), 3000)
    
    def xray_generated(self, job):
        if job.failed:
            self.gui.job_exception(job, dialog_title=_('Failed to generate XRay'))
            return
        self.gui.status_bar.show_message(job.description + ' ' + _('finished'), 5000)

class XRayBuilder(object):

    def wikireplace(self, str):
        result = re.sub (r'\s?\([^)]+\)', '', str)
        result = re.sub (r'\s?["\'(]\\w+["\')]', '', result)
        result = re.sub ('[.,\u201c\u201d()\/\"?\':\[\]]', '', result)
        result = re.sub (r'\s', '_', result)
        return result

    def charreplace(self, str):
        result = re.sub (r'"', '', str)
        # Replace all non-ASCII characters. Can we be smarter and just escape them?
        result = re.sub (r'[^ -~]', '', result)
        return result

    def write_xray(self, mobi_file_path, xraydir, asin, database, uniqid, data, job, newFormat):

        asJson = { 'asin' : asin, 'guid' : database +':'+ re.sub ('L$', '', str(hex(uniqid)[2:]).upper()), 'version': '1', 'terms': [] }

        if data.wikiUrl != '' :
            asJson['terms'].append ( {'type' : 'topic', 'term' : 'Wikipedia Info', \
            'desc': str(data.wikiText), 'descSrc':'wiki', 'descUrl': str(data.wikiUrl), \
            'locs': [[100,100,100,5]] \
            } )

        # TODO: need to assign to data.characters afterwards?
        sorted(data.characters, key=lambda char: char.term)
        for c in data.characters:
            key   = c.term
            value = c.desc
            locs  = c.locs
            url   = c.url

            if (url == ''):
                url = 'http://www.shelfari.com/characters/' + self.wikireplace(key)

            if (len(locs) == 0):
                locs = [[100,100,100,6]]
                job.log_write("WARNING: Didn't find any matches for " + c.term + ". Consider creating aliases to resolve this.\n");

            asJson['terms'].append ( {'type' : 'character', 'term' : key, \
            'desc': value.strip(), 'descSrc':'shelfari', 'descUrl': url, \
            'locs': locs \
            } )

        # TODO is this right? aren't we discarding the results of the sort?
        sorted(data.topics, key=lambda topic: topic.term)
        for t in data.topics:
            key   = t.term
            value = t.desc
            locs  = t.locs
            url   = t.url

            if (len(locs) == 0):
                locs = [[100,100,100,6]]

            asJson['terms'].append ( {'type' : 'topic', 'term' : key.strip(), \
            'desc': value.strip(), 'descSrc':'shelfari', 'descUrl': url, \
            'locs': locs \
            } )

        if (len(data.chapters) == 0):
            asJson['chapters'] = [ { 'name': 'null', 'start' : 1, 'end' : data.end } ]
        else:
            asJson['chapters'] = data.chapters

        asJson['srl'] = 1
        asJson['erl'] = data.end

        xrayfile = os.path.join (xraydir, "XRAY.entities." + asin + ".asc")

        if newFormat:
            self.write_sqlite (job, xrayfile, data, asJson)
        else:
            self.write_json (job, xrayfile, data, asJson)

    def write_sqlite(self, job, xrayfile, data, asJson):
        import sqlite3
        import codecs
        # remove the file before starting so that we don't try to try and old-format file as an sqlite file
        try:
            os.remove(xrayfile)
        except OSError as e:
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occured

        con = sqlite3.connect(xrayfile)

        with con:
            cur = con.cursor()    
            cur.execute( "PRAGMA user_version = 1;" )
            cur.execute( "PRAGMA encoding = 'UTF-8';" )

            baseSql = get_resources('BaseDB.sql')
            #job.log_write (baseSql)
            #job.log_write (str(type(baseSql)))
            #decoded = codecs.decode(baseSql, 'utf8')
            #job.log_write (str(type(decoded)))
            #reader = codecs.getreader('utf8') (baseSql)
            for sql in baseSql.split ("\n"):
                #job.log_write ("[" + sql + "]")
                cur.execute(sql)

            #with codecs.open('BaseDB.sql','r',encoding='utf8') as f:
            #    for sql in f:
            #        cur.execute(sql)

            # cur.execute( "update string set text=? where id=15" , (shelfariURL,) ) # why are trying to keep shelfariUrl?

            entity = 1
            excerpt = 1
            personCount = 0
            termCount = 0

            for idx, character in enumerate(data.characters + data.topics):

                charName = character.term
                if isinstance(character, XRayCharacter):
                    personCount += 1
                else:
                    termCount += 1

                cur.execute ( "insert into entity (id, label, loc_label, type, count, has_info_card) values (?, ?, null, ?, ?, 1);",
                    ( character.id,
                      character.term,
                      1 if isinstance(character, XRayCharacter) else 2,
                      len(character.locs),
                     ))

                cur.execute ( "insert into entity_description (text, source_wildcard, source, entity) values (?, ?, ?, ?);",
                              ( character.desc,
                                character.term, 
                                2, # 2 if character.descSrc == "shelfari" else 4,
                                character.id ))

                # ART: quick fix, this could be nicer (namedtuple at least)
                for loc in character.locs:
                    cur.execute ( "insert into occurrence (entity, start, length) values (?, ?, ?)",
                        (character.id,
                         loc[0] + loc[2],
                         loc[3]));

            for excerpt in data.excerpts:
                cur.execute ( "insert into excerpt (id, start, length, image, related_entities, goto) values (?, ?, ?, null, ?, null);",
                              ( excerpt['id'],
                                excerpt['start'], 
                                excerpt['length'],
                                ','.join ( [str(r) for r in excerpt['related_entities']] )))

                for rel in excerpt['related_entities']:
                    cur.execute ( "insert into entity_excerpt (entity, excerpt) values (?, ?)",
                                  ( rel, excerpt['id'] ))

            sortedChars = data.characters
            sortedChars = sorted (sortedChars, key=lambda char: len(char.locs), reverse=True)
            sortedChars = map (lambda char: str(char.id), sortedChars)
            if len(sortedChars) > 10:
                sortedChars = sortedChars[:10]
            sortedCharsString = ','.join(sortedChars)
            cur.execute ( "update type set top_mentioned_entities=? where id=1", (str(sortedCharsString), ))

            sortedTopics = data.topics
            sortedTopics = sorted (sortedTopics, key=lambda topic: len(topic.locs), reverse=True)
            sortedTopics = map (lambda topic: str(topic.id), sortedTopics)
            if len(sortedTopics) > 10:
                sortedTopics = sortedTopics[:10]
            sortedTopicsString = ','.join(sortedTopics)
            cur.execute ( "update type set top_mentioned_entities=? where id=2", (str(sortedTopicsString), ))

            cur.execute ( "insert into book_metadata (srl, erl, has_images, has_excerpts, show_spoilers_default, num_people, num_terms, num_images, preview_images) " +
                          "values (?, ?, 0, 1, 0, ?, ?, 0, null);",
                          ( 1, data.end, personCount, termCount ));
            

    def write_json(self, job, xrayfile, data, asJson):
        import json
        with open(xrayfile, 'wb') as xrayf:
            xrayf.write(json.dumps (asJson, separators=(',', ':')))

class XRayEntity(object):
    entity_idx = 1
    def __init__(self, text, url, type):
        try:
            self.term, self.desc = map(lambda value: value.strip(), text.split(':', 1))
        except ValueError:
            self.term = text.strip()
            self.desc = self.term
            
        self.entity_type = type
        self.locs = []
        self.searchFor = None
        self.url = url
        self.aliases = []
        
        self.id = XRayEntity.entity_idx
        XRayEntity.entity_idx += 1
        
    def addLoc(self, a, b, c, d):
        self.locs.append([a, b, c, d])
        
    def addAliases(self, aliases):
        self.aliases.extend(aliases)
        
    @classmethod    
    def reset(cls):
        """
        Reset the Entity object between parsing books - required to reset the starting ID for entities
        """
        XRayEntity.entity_idx = 1
        
class XRayTerm(XRayEntity):
    def __init__(self, text, url):
        
        super(XRayTerm, self).__init__(text, url, 2)

class XRayCharacter(XRayEntity):
    def __init__(self, text, url):
        super(XRayCharacter, self).__init__(text, url, 1)

class XRayData(object):
    honorifics = "Mr Mrs Ms Miss Master Sir Madam Lord Dame Lady Prof Professor Doctor Dr Father Reverend".split()
    honorifics.extend([x + "." for x in honorifics])
    
    def __init__(self):
        self.characters = []
        self.excerpts = []
        self.topics = []
        self.wikiText = ''
        self.wikiUrl = ''
        self.chapters = []
        self.shelfari_regex = re.compile("https?://(?:.*\.)?shelfari.com/books/([0-9]*)(?:/?.*)")
        self.aka_regex = re.compile("(.*) +\(aka.? (.*)\)")

    def readShelfari (self, shelfariUrl, job):
        import urllib2

        XRayEntity.reset()
        
        cache_dirname = prefs['cacheDir']
        res = self.shelfari_regex.match(shelfariUrl)
        bookid = None if not res.groups else res.groups()[0]
        fname = None if not (cache_dirname and bookid) else os.path.join(cache_dirname, bookid)
        if cache_dirname and os.path.isdir(cache_dirname) and res and os.path.isfile(fname):
            job.log_write("Loading Shelfari data from cache for '%s'\n" % (bookid))
            shelHtml = open(fname)
        else:
            start_time = time.time()
            try_count = 0
            max_tries = 3
            while try_count < max_tries:
                try_count += 1
                try:
                    response = urllib2.urlopen(str(shelfariUrl))
                    break
                except (httplib.BadStatusLine, socket.timeout):
                    job.log_write("Fetching Shelfari page failed - retry\n")
                    
            job.log_write("Fetched Shelfairi page in %u seconds after %s attempts\n" % (int(time.time() - start_time), try_count))
            shelHtml = response.read()
            if cache_dirname:
                job.log_write("Saving Shelfari data for '%s'\n" % (bookid))
                if not os.path.exists(cache_dirname):
                    os.mkdir(cache_dirname)
                with open(fname, 'w') as fd:
                    fd.write(shelHtml)
            else:
                job.log_write("Shelfari data not being saved, no cache directory specified in config\n")

        shelDoc = html5lib.parse(shelHtml, treebuilder='lxml', namespaceHTMLElements=False)

        characters = CSSSelector("#WikiModule_Characters ul.li_6 li")
        a = CSSSelector("a")
        for character in characters (shelDoc):
            url = ''  # TODO default
            links = a(character)
            if (len(links) > 0):
                url = links[0].get("href")
            self.characters.append ( XRayCharacter ("".join (character.itertext()), url))

        settings = CSSSelector("#WikiModule_Settings ul.li_6 li")
        for setting in settings (shelDoc):
            url = ''  # TODO default
            links = a(setting)
            if (len(links) > 0):
                url = links[0].get("href")
            self.topics.append ( XRayTerm ("".join (setting.itertext()), url))

        orgs = CSSSelector("#WikiModule_Organizations ul.li_6 li")
        for org in orgs (shelDoc):
            url = ''  # TODO default
            links = a(org)
            if (len(links) > 0):
                url = links[0].get("href")
            self.topics.append ( XRayTerm ("".join (org.itertext()), url))

        glossary = CSSSelector("#WikiModule_Glossary ul.li_6 li")
        for gloss in glossary (shelDoc):
            url = ''  # TODO default
            links = a(gloss)
            if (len(links) > 0):
                url = links[0].get("href")
            self.topics.append ( XRayTerm ("".join (gloss.itertext()), url))

        #themes = CSSSelector("#WikiModule_Themes ul.li_6 li")
        #for theme in themes (shelDoc):
        #    self.topics.append ( "".join (theme.itertext()) )

    def readWikipedia (self, wikiUrl):
        import urllib2
        self.wikiUrl = wikiUrl
        if wikiUrl != '':
            req = urllib2.Request(str(wikiUrl), headers={'User-Agent' : "Calibre"}) 
            con = urllib2.urlopen(req)
            wikiHtml = con.read()
            wikiDoc = html5lib.parse(wikiHtml, treebuilder='lxml', namespaceHTMLElements=False)
            selector = CSSSelector(".mw-content-ltr p")
            self.wikiText = "".join(selector(wikiDoc)[0].itertext())

    def addAliases (self, character, aliases):
        for char in self.characters:
            if (char.term == character):
                char.addAliases (aliases)
                break
        else: # ie if for loop didn't break
            c = XRayCharacter (character, None)
            c.addAliases (aliases)
            self.characters.append (c)

    @staticmethod
    def fullname_to_possible_aliases(fullname):
        """
        Given a full name ("{Title} ChristianName {Middle Names} {Surname}"), return a list of possible aliases
        
        ie. Title Surname, ChristianName Surname, Title ChristianName, {the full name}
        
        The returned aliases are in the order they should match
        """
        aliases = []
        aliases.append(fullname)
        
        parts = fullname.split()
        
        if parts[0] in XRayData.honorifics:
            title = parts.pop(0)
        else:
            title = None
            
        if len(parts) >= 2:
            # Assume: {Title} Firstname {Middlenames} Lastname
            # Already added the full form, also add Title Lastname, and for some Title Firstname
            surname = parts.pop() # This will cover double barrel surnames, we split on whitespace only
            christian_name = parts.pop(0)
            middlenames = parts
            
            if title:
                aliases.append("%s %s" % (title, surname))
                if title in "Lord":
                    aliases.append("%s %s" % (title, christian_name))
            aliases.append(christian_name)
            aliases.append(surname)   
        elif title:
            # Odd, but got Title Name (eg. Lord Buttsworth), so see if we can alias
            aliases.append(parts[0])
        else:
            # We've got no title, so just a single word name.  No alias needed
            pass
        return aliases
    def auto_expand_aliases(self, job):
        #
        # Do all easy expansion - but check  to make sure what we
        # are adding is unique
        #
        # eg. if we have "Sir Richard Branson", we can expand to
        # Sir Branson, Sir Richard, Richard Branson.  But make sure
        # there isn't a second Sir Branson/Sir Richard first.
        #
        # We can also add just surnames as a last resort alias, but
        # only if they are unique (in the Reacher novels, "Reacher"
        # nearly always refers to Jack Reacher, but where there are
        # other Reacher family members we can't guess this automatically)
        #
        
        #
        # ARTTODO: if we have a character name with akas we could just replace it with the right thing
        # (as the book is never going to have eg. "Bob Hoskins (aka Bobby)" in it..
        #
        if len(set(self.characters)) != len(self.characters):
            job.log_write("ERROR: have probable duplicate characters (%s vs. %s)")
            return
        
        potential_aliases = OrderedDefaultdict(list)
        
        for char in self.characters:
            name = char.term
            if "(aka" in name:
                # Some Name (aka othername1, othername2)
                res = self.aka_regex.match(name)
                if not res:
                    jog.log_write("ERROR: name looked like having AKA but matching failed: %s\n" % (name))
                    continue
                real_name, aliases = res.groups()
                aliases = [x.strip() for x in aliases.split(",")]
                
                # char.term looks like "Bob Hoskins (aka Rob)", so replace it with a more suitable name - just the real_name
                char.term = real_name
                
                real_name_aliases = self.fullname_to_possible_aliases(real_name)
                for found_alias in real_name_aliases:
                    potential_aliases[found_alias].append(char)
                for alias in aliases:
                    for found_alias in self.fullname_to_possible_aliases(alias):
                        if not found_alias in real_name_aliases:
                            # If we have "Jane Marriedname (aka Jane Maidenname)" we don't want to consider
                            # the two "Jane" too be clashing, and exclude them later - so skip one now
                            # (and only exclude if it clashes with a separate character)
                            # ARTTBD - how much do we care about the ordering here?  Could just create a set (to get uniqueness) then sort by longest first
                            potential_aliases[found_alias].append(char)
                continue
            
            if "/" in name or "\\" in name:
                job.log_write("ERROR: skippping strangely formed name or name with poorly formed akas: %s\n" % (name))
                continue # Should return to make it clearer things failed hard?
            
            for alias in self.fullname_to_possible_aliases(name):
                if alias != name:
                    potential_aliases[alias].append(char)
        
        for alias in potential_aliases:
            if len(potential_aliases[alias]) == 1:
                char = potential_aliases[alias][0]
                job.log_write("Unique alias: %s for %s\n" % (alias, potential_aliases[alias][0].term))
                char.addAliases([alias])
            else:
                job.log_write("INFO: Duplicate alias, ignore both: [%s] for %s\n" % (alias, ",".join([x.term for x in potential_aliases[alias]])))
                                    
    def processAliases (self, job, aliasFile):
        if aliasFile is not None and aliasFile != '':
            if os.path.exists(aliasFile):
                job.log_write("Reading alias file %s\n" % (aliasFile))
                # Windows app creates UTF-8-sig files, so cope with them
                # (if the file has the optional/unnecessary \ufeff sig it will be removed, if it doesn't it works fine)
                with io.open(aliasFile, "r", encoding='UTF-8-sig') as aliases:
                    for line in aliases:
                        line = line.rstrip()
                        pos = line.find('|')
                        if (pos > 0):
                            term = line[0:pos]
                            a = line[pos+1:].strip()
                            if len(a) == 0:
                                job.log_write("No aliases found for %s, skip\n" % (term))
                                continue
                            al = a.split (",")
                            job.log_write("Adding alias for %s: %s\n" % (term, al))
                            self.addAliases (term, al)

            else:
                if prefs['autoExpandAliases']:
                    self.auto_expand_aliases(job)
                                                
                job.log_write ("Writing aliases\n")
                with io.open(aliasFile, "w", encoding='UTF-8') as aliases:
                    for char in self.characters:
                        aliases.write("%s|%s\n" % (char.term, ",".join(char.aliases)))
        else:
            job.log_write("No alias file specified\n")


    # http://stackoverflow.com/questions/15343218/get-divs-html-content-with-lxml
    def innerHTML(self, node): 
        from lxml import html
        buildString = ''
        for child in node:
            buildString += html.tostring(child)
        return buildString

    def rawml (self, rawml, offset, job):

        from lxml import etree

        self.end = os.path.getsize(str(rawml))

        # Different parsers in play, trying to work out the best one to use.
        newParser = False

        rawmlFile = open(str(rawml))

        if newParser:
            parser = etree.XMLParser(recover=True)
            raw = etree.parse(rawmlFile, parser)
        else:
            raw = html5lib.parse(rawmlFile, treebuilder='lxml', namespaceHTMLElements=False)

        rawmlFile.close();

        # TODO unnecessary duplication of file reading
        rawmlFile = open(rawml)
        rawMlAsString = rawmlFile.read()
        rawmlFile.close()

        try:
            locOffset = int(offset)
        except ValueError:
            locOffset = 0

        shortEx = True

        # disabled temporarily
        toc = False # raw.iterfind ("//reference[translate(@title,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='TABLE OF CONTENTS']")
        if toc:
            tocloc = int (re.sub ('^0*', '', toc[0].get("filepos")));

            mbp = rawMlAsString.find("<mbp:pagebreak/>", tocloc)
            tochtml = rawMlAsString[tocloc:mbp]

            tocdoc = html5lib.parse (tochtml, treebuilder='lxml', namespaceHTMLElements=False)
            tocnodes = tocdoc.find ("//a");
            for chapter in tocnodes:

                if (chapter.get("filepos")):

                    chapterName = ''.join([child for child in chapter.itertext()])
                    filepos = int (re.sub ('^0*', '', chapter.get("filepos")));
                    if (len(self.chapters) > 0):
                        self.chapters[-1]['end'] = filepos;

                    #    if (chapters[chapters.Count - 1].start > filepos):
                    #         chapters.RemoveAt(chapters.Count - 1); //remove broken chapters

                    self.chapters.append ( { 'name': chapterName, 'start' : filepos, 'end':  len(rawMlAsString) } )

            #print (self.chapters)

        # TODO if no chapters etc.

        # Even though we've already parsed the rawml, we used a library that
        # doesn't give us content positions. So re-parse using a different library.
        # (The original parser gives us XPath functionality).
        # TODO optimise this
        parser = ParserWithPosition()
        parser.feed(rawMlAsString)

        from lxml import html

        try:
            if newParser:
                paras = raw.iterfind ("//p")
            else:
                paras = raw.xpath ("//p")

            ix=0
            excerptID = 0
            for p in paras:
                # TODO skip if chapter empty

                ptext = (p.text or '') + ''.join([html.tostring(child) for child in p.iterdescendants()])
                #job.log_write(str(ix) + ":" + ptext + "\n")

                lenQuote = len(ptext)
                location = parser.ppos[ix]
                ix=ix+1
                job.log_write("Processing paragraph " + str(ix) + "\n");

                # if (location < srl || location > erl) continue; //Skip paragraph if outside chapter range
                for character in self.characters + self.topics:

                    charName = character.term
                    #print ("Searching for " + charName)
                    #Search for character name and aliases in either the html-less text. If failed, try in the HTML for rare situations.
                    #TODO: Improve location searching, as IndexOf will not work if book length exceeds 2,147,483,647...
                    #List<string> search = character.aliases.ToList<string>();
                    #search.Insert(0, character.termName);

                    searchItems = [ charName ]
                    if isinstance(character, XRayCharacter):
                        searchItems.extend (character.aliases)

                    searchFor = character.searchFor
                    if not searchFor:
                        # Ensure non-word characters before and after match.
                        character.searchFor = re.compile('(^|\W)(' + "|".join ( [ re.escape(a) for a in searchItems ] )  + ')(\W|$)', flags=re.IGNORECASE )
                        searchFor = character.searchFor

                    match = searchFor.search (ptext)
                    if match is not None:
                        locHighlight = match.start(2)
                        # Make sure we get the length from the matched item (possibly an alias)
                        lenHighlight = match.end(2) - match.start(2)

                        lengthLimit = 135
                        if (shortEx and (locHighlight + lenHighlight > lengthLimit)):

                            #job.log_write("Excerpt is too long for character " + charName + " location="+str(location) + " shortEx="+ str(shortEx) + " locHighlight="+str(locHighlight) + " lenHighlight="+str(lenHighlight) + "\n")

                            inner = (p.text or '') + ''.join([html.tostring(child) for child in p.iterdescendants()]) # innerHTML
                            start = locHighlight
                            at = 0
                            newLoc = -1
                            newLenQuote = 0
                            newLocHighlight = 0

                            while ((start > -1) and (at > -1)):
                                at = inner.rfind(". ", 1, start)
                                #job.log_write ("at="+str(at) + "\n")
                                if (at > -1):
                                    start = at - 1

                                    if ((locHighlight + lenHighlight + 1 - at - 2) <= lengthLimit):
                                        newLoc = location + at + 2
                                        newLenQuote = lenQuote - at - 2
                                        newLocHighlight = locHighlight - at - 2
                                        #job.log_write ("updating to at="+str(at) + " newLoc=" + str(newLoc) + " newLenQuote=" + str(newLenQuote) + " newLocHighlight=" + str(newLocHighlight) + "\n");

                                    else:
                                        break
                                else:
                                    break

                            # Only add new locs if shorter excerpt was found
                            if (newLoc >= 0):
                                character.addLoc (newLoc + locOffset, newLenQuote, newLocHighlight, lenHighlight)
                                continue

                        character.addLoc (location+locOffset, lenQuote, locHighlight, lenHighlight)

                        # Either add a new excerpt, or add a new entity to an existing excerpt

                        excerptCheck = filter (lambda e: e['start'] == (location+locOffset), self.excerpts)
                        if (len(excerptCheck) > 0):
                            if ( len(filter (lambda rel: rel == character.id, excerptCheck[0]['related_entities'])) == 0):
                                excerptCheck[0]['related_entities'].append(character.id)

                        else:
                            self.excerpts.append ( { 'id': excerptID, 'start': location+locOffset, 'length': lenQuote, 'related_entities': [ character.id ] } )
                            excerptID += 1
                            #Excerpt newExcerpt = new Excerpt(excerptID++, location + locOffset, lenQuote);
                            #newExcerpt.related_entities.Add(character.id);
                            #excerpts.Add(newExcerpt);

                    #doesn't seem to work
                    #pct=0.50 + 0.25*ix/len(paras)
                    #job.log_write("percent="+str(pct) + "\n");
                    #job.notifications.put(pct, "Parsing...")
                    #job.consume_notifications()

        except IndexError:
            import traceback
            job.log_write("WARNING: An internal error occurred parsing the book. Some information may be missing from the generated XRay file.\n")
            job.log_write(traceback.format_exc())

from HTMLParser import HTMLParser

# Store the starting location of all the 'p' elements
class ParserWithPosition(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.ppos = []
        self.lastWasP = False

    def handle_starttag(self, tag, attrs):
        if (tag == 'p'):
            #print ("handle_starttag p " + str(self.getpos()[1]))
            self.lastWasP = True

    def handle_endtag(self, tag):
        if (tag == 'p'):
            if self.lastWasP:
                #print ("handle_endtag pos:" + str(self.getpos()[1]))
                self.ppos.append (self.getpos()[1])
                #print ("added at pos " + str(len(self.ppos)))
                self.lastWasP = False

    def handle_data(self, data):
        if self.lastWasP:
            #print ("handle_data pos:" + str(self.getpos()[1]) + " " + str(data))
            self.ppos.append (self.getpos()[1])
            #print ("added at pos " + str(len(self.ppos)))
            self.lastWasP = False

class StartDialog(QDialog, Ui_XRay):
    def __init__(self,parent=None,shelfari=None,wiki=None,aliases=None,outputDir=None,newFormat=None):
        QDialog.__init__(self,parent)
        self.parent=parent
        self.setupUi(self)
        if shelfari is not None:
            self.shelfariEdit.setText(shelfari)
        if wiki is not None:
            self.wikipediaEdit.setText(wiki)
        if aliases is not None:
            self.aliasesEdit.setText(aliases)
        if outputDir is not None:
            self.xrayDirEdit.setText(outputDir)
        if newFormat is not None:
            self.newFormatCheckbox.setChecked(newFormat)
        self.aliasBrowseButton.clicked.connect(self.onAliasBrowseButtonClicked)
        self.xrayBrowseButton.clicked.connect(self.onXrayBrowseButtonClicked)
        self.unpackBrowseButton.clicked.connect(self.onUnpackBrowseButtonClicked)

    def onXrayBrowseButtonClicked(self):
        xraydir = unicode(QFileDialog.getExistingDirectory(self.parent, _('Directory to save XRay file'), self.parent.library_path, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        if xraydir:
            self.xrayDirEdit.setText(xraydir)

    def onUnpackBrowseButtonClicked(self):
        unpackdir = unicode(QFileDialog.getExistingDirectory(self.parent, _('Directory to unpack files into'), self.parent.library_path, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        if unpackdir:
            self.unpackDirEdit.setText(unpackdir)

    def onAliasBrowseButtonClicked(self):
        result = QFileDialog.getSaveFileName(self.parent, _('Aliases file'), self.parent.library_path)
        aliasFile = result[0] if isinstance(result, tuple) else result
        if aliasFile:
            self.aliasesEdit.setText(unicode(aliasFile))

    def getValues(self):
        return [ str(self.shelfariEdit.text()), str(self.wikipediaEdit.text()), str(self.aliasesEdit.text()), str(self.offsetEdit.text()), str(self.xrayDirEdit.text()), str(self.unpackDirEdit.text()), self.newFormatCheckbox.isChecked() ]
