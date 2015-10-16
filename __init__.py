# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__ = 'GPL 3'
__copyright__ = '2012-15, Matthew Wilson <matthew@mjwilson.demon.co.uk>'
__docformat__ = 'restructuredtext en'

from calibre.customize import InterfaceActionBase

class ActionXRay(InterfaceActionBase):

    name = 'XRay Generator'
    description = 'Generate XRay info file'
    supported_platforms = ['windows', 'osx', 'linux']
    author = """Calibre plugin by Matthew Wilson.
Based on code by shinew and Ephemerality.
Also packages KindleUnpack by DiapDealer.
Original mobiunpack.py, Copyright © 2009 Charles M. Hannum <root@ihack.net>.
Extensions / Improvements Copyright © 2009-2012 P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding.\n"""

    version = (0, 2, 14)
    minimum_calibre_version = (2, 0, 0)
    
    actual_plugin = 'calibre_plugins.xray_generator.xrayaction:XRayAction'
