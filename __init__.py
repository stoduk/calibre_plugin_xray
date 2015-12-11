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

    def is_customizable(self):
        '''
        This method must return True to enable customization via
        Preferences->Plugins
        '''
        return True

    def config_widget(self):
        '''
        Implement this method and :meth:`save_settings` in your plugin to
        use a custom configuration dialog.

        This method, if implemented, must return a QWidget. The widget can have
        an optional method validate() that takes no arguments and is called
        immediately after the user clicks OK. Changes are applied if and only
        if the method returns True.

        If for some reason you cannot perform the configuration at this time,
        return a tuple of two strings (message, details), these will be
        displayed as a warning dialog to the user and the process will be
        aborted.

        The base class implementation of this method raises NotImplementedError
        so by default no user configuration is possible.
        '''
        # It is important to put this import statement here rather than at the
        # top of the module as importing the config class will also cause the
        # GUI libraries to be loaded, which we do not want when using calibre
        # from the command line
        from calibre_plugins.xray_generator.xray_config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        '''
        Save the settings specified by the user with config_widget.

        :param config_widget: The widget returned by :meth:`config_widget`.
        '''
        config_widget.save_settings()

        # Apply the changes
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
