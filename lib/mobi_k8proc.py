#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, struct, re
from mobi_index import MobiIndex
from mobi_utils import fromBase32
from path import pathof

_guide_types = ['cover','title-page','toc','index','glossary','acknowledgements',
                'bibliography','colophon','copyright-page','dedication',
                'epigraph','foreward','loi','lot','notes','preface','text']

# locate beginning and ending positions of tag with specific aid attribute 
def locate_beg_end_of_tag(ml, aid):
    pattern = r'''<[^>]*\said\s*=\s*['"]%s['"][^>]*>''' % aid
    aid_pattern = re.compile(pattern,re.IGNORECASE)
    for m in re.finditer(aid_pattern, ml):
        plt = m.start()
        pgt = ml.find('>',plt+1)
        return plt, pgt
    return 0, 0


# iterate over all tags in block in reverse order, i.e. last ta to first tag
def reverse_tag_iter(block):
    end = len(block)
    while True:
        pgt = block.rfind(b'>', 0, end)
        if pgt == -1: break
        plt = block.rfind(b'<', 0, pgt)
        if plt == -1: break
        yield block[plt:pgt+1]
        end = plt


class K8Processor:
    def __init__(self, mh, sect, debug=False):
        self.sect = sect
        self.mi = MobiIndex(sect)
        self.mh = mh
        self.skelidx = mh.skelidx
        self.dividx = mh.dividx
        self.othidx = mh.othidx
        self.fdst = mh.fdst
        self.flowmap = {}
        self.flows = None
        self.flowinfo = []
        self.parts = None
        self.partinfo = []
        self.fdsttbl= [0,0xffffffff]
        self.DEBUG = debug

        # read in and parse the FDST info which is very similar in format to the Palm DB section
        # parsing except it provides offsets into rawML file and not the Palm DB file
        # this is needed to split up the final css, svg, etc flow section
        # that can exist at the end of the rawML file
        if self.fdst != 0xffffffff:
            header = self.sect.loadSection(self.fdst)
            if header[0:4] == "FDST":
                num_sections, = struct.unpack_from('>L', header, 0x08)
                self.fdsttbl = struct.unpack_from('>%dL' % (num_sections*2), header, 12)[::2] + (mh.rawSize, )
                sect.setsectiondescription(self.fdst,"KF8 FDST INDX")
                if self.DEBUG:
                    print "\nFDST Section Map:  %d sections" % num_sections
                    for j in xrange(num_sections):
                         print "Section %d: 0x%08X - 0x%08X" % (j, self.fdsttbl[j],self.fdsttbl[j+1])
            else:
                print "\nError: K8 Mobi with Missing FDST info"


        # read/process skeleton index info to create the skeleton table
        skeltbl = []
        if self.skelidx != 0xffffffff:
            # for i in xrange(2):
            #     fname = 'skel%04d.dat' % i
            #     data = self.sect.loadSection(self.skelidx + i)
            #     open(pathof(fname), 'wb').write(data)
            outtbl, ctoc_text = self.mi.getIndexData(self.skelidx, "KF8 Skeleton")
            fileptr = 0
            for [text, tagMap] in outtbl:
                # file number, skeleton name, divtbl record count, start position, length
                skeltbl.append([fileptr, text, tagMap[1][0], tagMap[6][0], tagMap[6][1]])
                fileptr += 1
        self.skeltbl = skeltbl
        if self.DEBUG:
            print "\nSkel Table:  %d entries" % len(self.skeltbl)
            print "table: filenum, skeleton name, div tbl record count, start position, length"
            for j in xrange(len(self.skeltbl)):
                print self.skeltbl[j]

        # read/process the div index to create to <div> (and <p>) table
        divtbl = []
        if self.dividx != 0xffffffff:
            # for i in xrange(3):
            #     fname = 'div%04d.dat' % i
            #     data = self.sect.loadSection(self.dividx + i)
            #     open(pathof(fname), 'wb').write(data)
            outtbl, ctoc_text = self.mi.getIndexData(self.dividx, "KF8 Division/Fragment")
            for [text, tagMap] in outtbl:
                # insert position, ctoc offset (aidtext), file number, sequence number, start position, length
                ctocoffset = tagMap[2][0]
                ctocdata = ctoc_text[ctocoffset]
                divtbl.append([int(text), ctocdata, tagMap[3][0], tagMap[4][0], tagMap[6][0], tagMap[6][1]])
        self.divtbl = divtbl
        if self.DEBUG:
            print "\nDiv (Fragment) Table: %d entries" % len(self.divtbl)
            print "table: file position, link id text, file num, sequence number, start position, length"
            for j in xrange(len(self.divtbl)):
                print self.divtbl[j]

        # read / process other index <guide> element of opf
        othtbl = []
        if self.othidx != 0xffffffff:
            # for i in xrange(3):
            #     fname = 'oth%04d.dat' % i
            #     data = self.sect.loadSection(self.othidx + i)
            #     open(pathof(fname), 'wb').write(data)
            outtbl, ctoc_text = self.mi.getIndexData(self.othidx, "KF8 Other (<guide> elements)")
            for [text, tagMap] in outtbl:
                # ref_type, ref_title, div/frag number
                ctocoffset = tagMap[1][0]
                ref_title = ctoc_text[ctocoffset]
                ref_type = text
                fileno = None
                if 3 in tagMap.keys():
                    fileno  = tagMap[3][0]
                if 6 in tagMap.keys():
                    fileno = tagMap[6][0]
                othtbl.append([ref_type, ref_title, fileno])
        self.othtbl = othtbl
        if self.DEBUG:
            print "\nOther (Guide) Table: %d entries" % len(self.othtbl)
            print "table: ref_type, ref_title, divtbl entry number"
            for j in xrange(len(self.othtbl)):
                print self.othtbl[j]


    def buildParts(self, rawML):
        # now split the rawML into its flow pieces
        self.flows = []
        for j in xrange(0, len(self.fdsttbl)-1):
            start = self.fdsttbl[j]
            end = self.fdsttbl[j+1]
            self.flows.append(rawML[start:end])

        # the first piece represents the xhtml text
        text = self.flows[0]
        self.flows[0] = ''

        # walk the <skeleton> and <div> tables to build original source xhtml files
        # *without* destroying any file position information needed for later href processing
        # and create final list of file separation start: stop points and etc in partinfo
        if self.DEBUG:
            print "\nRebuilding flow piece 0: the main body of the ebook"
        self.parts = []
        self.partinfo = []
        divptr = 0
        baseptr = 0
        cnt = 0
        for [skelnum, skelname, divcnt, skelpos, skellen] in self.skeltbl:
            baseptr = skelpos + skellen
            skeleton = text[skelpos: baseptr]
            for i in range(divcnt):
                [insertpos, idtext, filenum, seqnum, startpos, length] = self.divtbl[divptr]
                aidtext = idtext[12:-2]
                if i == 0:
                    filename = 'part%04d.xhtml' % filenum
                slice = text[baseptr: baseptr + length]
                insertpos = insertpos - skelpos
                head = skeleton[:insertpos]
                tail = skeleton[insertpos:]
                actual_inspos = insertpos
                if (tail.find(b'>') < tail.find(b'<') or head.rfind(b'>') < head.rfind(b'<')):
                    # There is an incomplete tag in either the head or tail.
                    # This can happen for some badly formed KF8 files
                    print 'The div table for %s has incorrect insert position. Calculating manually.' % skelname
                    bp, ep = locate_beg_end_of_tag(skeleton, aidtext)
                    if bp != ep:
                        actual_inspos = ep + 1 + startpos
                if insertpos != actual_inspos:
                    print "fixed corrupt div/frag table insert position", insertpos+skelpos, actual_inspos+skelpos
                    insertpos = actual_inspos
                    self.divtbl[divptr][0] = actual_inspos + skelpos
                skeleton = skeleton[0:insertpos] + slice + skeleton[insertpos:]
                baseptr = baseptr + length
                divptr += 1
            cnt += 1
            self.parts.append(skeleton)
            self.partinfo.append([skelnum, 'Text', filename, skelpos, baseptr, aidtext])

        # assembled_text = "".join(self.parts)
        # open(pathof('assembled_text.dat'),'wb').write(assembled_text)

        # The primary css style sheet is typically stored next followed by any
        # snippets of code that were previously inlined in the
        # original xhtml but have been stripped out and placed here.
        # This can include local CDATA snippets and and svg sections.

        # The problem is that for most browsers and ereaders, you can not
        # use <img src="imageXXXX.svg" /> to import any svg image that itself
        # properly uses an <image/> tag to import some raster image - it
        # should work according to the spec but does not for almost all browsers
        # and ereaders and causes epub validation issues because those  raster
        # images are in manifest but not in xhtml text - since they only
        # referenced from an svg image

        # So we need to check the remaining flow pieces to see if they are css
        # or svg images.  if svg images, we must check if they have an <image />
        # and if so inline them into the xhtml text pieces.

        # there may be other sorts of pieces stored here but until we see one
        # in the wild to reverse engineer we won't be able to tell
        self.flowinfo.append([None, None, None, None])
        svg_tag_pattern = re.compile(r'''(<svg[^>]*>)''', re.IGNORECASE)
        image_tag_pattern = re.compile(r'''(<image[^>]*>)''', re.IGNORECASE)
        for j in xrange(1,len(self.flows)):
            flowpart = self.flows[j]
            nstr = '%04d' % j
            m = re.search(svg_tag_pattern, flowpart)
            if m != None:
                # svg
                type = 'svg'
                start = m.start()
                m2 = re.search(image_tag_pattern, flowpart)
                if m2 != None:
                    format = 'inline'
                    dir = None
                    fname = None
                    # strip off anything before <svg if inlining
                    flowpart = flowpart[start:]
                else:
                    format = 'file'
                    dir = "Images"
                    fname = 'svgimg' + nstr + '.svg'
            else:
                # search for CDATA and if exists inline it
                if flowpart.find('[CDATA[') >= 0:
                    type = 'css'
                    flowpart = '<style type="text/css">\n' + flowpart + '\n</style>\n'
                    format = 'inline'
                    dir = None
                    fname = None
                else:
                    # css - assume as standalone css file
                    type = 'css'
                    format = 'file'
                    dir = "Styles"
                    fname = 'style' + nstr + '.css'

            self.flows[j] = flowpart
            self.flowinfo.append([type, format, dir, fname])


        if self.DEBUG:
            print "\nFlow Map:  %d entries" % len(self.flowinfo)
            for fi in self.flowinfo:
                print fi
            print "\n"

            print "\nXHTML File Part Position Information: %d entries" % len(self.partinfo)
            for pi in self.partinfo:
                print pi

        if False: #self.Debug:
            # dump all of the locations of the aid tags used in TEXT
            # find id links only inside of tags
            #    inside any < > pair find all "aid=' and return whatever is inside the quotes
            #    [^>]* means match any amount of chars except for  '>' char
            #    [^'"] match any amount of chars except for the quote character
            #    \s* means match any amount of whitespace
            print "\npositions of all aid= pieces"
            id_pattern = re.compile(r'''<[^>]*\said\s*=\s*['"]([^'"]*)['"][^>]*>''',re.IGNORECASE)
            for m in re.finditer(id_pattern, rawML):
                [filename, partnum, start, end] = self.getFileInfo(m.start())
                [seqnum, idtext] = self.getDivTblInfo(m.start())
                value = fromBase32(m.group(1))
                print "  aid: %s value: %d at: %d -> part: %d, start: %d, end: %d" % (m.group(1), value, m.start(), partnum, start, end)
                print "       %s  divtbl entry %d" % (idtext, seqnum)

        return


    # get information div table entry by pos
    def getDivTblInfo(self, pos):
        baseptr = 0
        for j in xrange(len(self.divtbl)):
            [insertpos, idtext, filenum, seqnum, startpos, length] = self.divtbl[j]
            if pos >= insertpos and pos < (insertpos + length):
                return seqnum, 'in: ' + idtext
            if pos < insertpos:
                return seqnum, 'before: ' + idtext
        return None, None


    # get information about the part (file) that exists at pos in original rawML
    def getFileInfo(self, pos):
        for [partnum, dir, filename, start, end, aidtext] in self.partinfo:
            if pos >= start and pos < end:
                return filename, partnum, start, end
        return None, None, None, None


    # accessor functions to properly protect the internal structure
    def getNumberOfParts(self):
        return len(self.parts)

    def getPart(self,i):
        if i >= 0 and i < len(self.parts):
            return self.parts[i]
        return None

    def getPartInfo(self, i):
        if i >= 0 and i < len(self.partinfo):
            return self.partinfo[i]
        return None

    def getNumberOfFlows(self):
        return len(self.flows)

    def getFlow(self,i):
        # note flows[0] is empty - it was all of the original text
        if i > 0 and i < len(self.flows):
            return self.flows[i]
        return None

    def getFlowInfo(self,i):
        # note flowinfo[0] is empty - it was all of the original text
        if i > 0 and i < len(self.flowinfo):
            return self.flowinfo[i]
        return None


    def getIDTagByPosFid(self, posfid, offset):
        # first convert kindle:pos:fid and offset info to position in file
        row = fromBase32(posfid)
        off = fromBase32(offset)
        [insertpos, idtext, filenum, seqnm, startpos, length] = self.divtbl[row]
        pos = insertpos + off
        fname, pn, skelpos, skelend = self.getFileInfo(pos)
        if fname is None:
            # pos does not exist
            # default to skeleton pos instead
            print "Link To Position", pos, "does not exist, retargeting to top of target"
            pos = self.skeltbl[filenum][3]
            fname, pn, skelpos, skelend = self.getFileInfo(pos)
        # an existing "id=" or "name=" attribute must exist in original xhtml otherwise it would not have worked for linking.
        # Amazon seems to have added its own additional "aid=" inside tags whose contents seem to represent
        # some position information encoded into Base32 name.
        # so find the closest "id=" before position the file  by actually searching in that file
        idtext = self.getIDTag(pos)
        return fname, idtext

    def getIDTag(self, pos):
        # find the first tag with a named anchor (name or id attribute) before pos
        fname, pn, skelpos, skelend = self.getFileInfo(pos)
        if pn is None and skelpos is None:
            print "Error: getIDTag - no file contains ", pos
        textblock = self.parts[pn]
        idtbl = []
        npos = pos - skelpos
        # if npos inside a tag then search all text before the its end of tag marker
        pgt = textblock.find('>',npos)
        plt = textblock.find('<',npos)
        if plt == npos or pgt < plt:
            npos = pgt + 1
        # find id and name attributes only inside of tags
        # use a reverse tag search since that is faster
        #    inside any < > pair find "id=" and "name=" attributes return it
        #    [^>]* means match any amount of chars except for  '>' char
        #    [^'"] match any amount of chars except for the quote character
        #    \s* means match any amount of whitespace
        textblock = textblock[0:npos]
        id_pattern = re.compile(r'''<[^>]*\sid\s*=\s*['"]([^'"]*)['"]''',re.IGNORECASE)
        name_pattern = re.compile(r'''<[^>]*\sname\s*=\s*['"]([^'"]*)['"]''',re.IGNORECASE)
        for tag in reverse_tag_iter(textblock):
            m = id_pattern.match(tag) or name_pattern.match(tag)
            if m is not None:
                return m.group(1)
        if self.DEBUG:
            print "Found no id in the textblock, link must be to top of file"
        return ''


    # do we need to do deep copying
    def setParts(self, parts):
        assert(len(parts) == len(self.parts))
        for i in range(len(parts)):
            self.parts[i] = parts[i]

    # do we need to do deep copying
    def setFlows(self, flows):
        assert(len(flows) == len(self.flows))
        for i in xrange(len(flows)):
            self.flows[i] = flows[i]


    # get information about the part (file) that exists at pos in original rawML
    def getSkelInfo(self, pos):
        for [partnum, dir, filename, start, end, aidtext] in self.partinfo:
            if pos >= start and pos < end:
                return [partnum, dir, filename, start, end, aidtext]
        return [None, None, None, None, None, None]

    # fileno is actually a reference into divtbl (a fragment)
    def getGuideText(self):
        guidetext = ''
        for [ref_type, ref_title, fileno] in self.othtbl:
            if ref_type == 'thumbimagestandard':
                continue
            if ref_type not in _guide_types and not ref_type.startswith('other.'):
                if ref_type == 'start':
                    ref_type = 'text'
                else:
                    ref_type = 'other.' + ref_type
            [pos, idtext, filenum, seqnm, startpos, length] = self.divtbl[fileno]
            [pn, dir, filename, skelpos, skelend, aidtext] = self.getSkelInfo(pos)
            idtext = self.getIDTag(pos)
            linktgt = filename
            if idtext != '':
                linktgt += '#' + idtext
            guidetext += '<reference type="%s" title="%s" href="%s/%s" />\n' % (ref_type, ref_title, dir, linktgt)
        # opf is encoded utf-8 so must convert any titles properly
        guidetext = unicode(guidetext, self.mh.codec).encode("utf-8")
        return guidetext
