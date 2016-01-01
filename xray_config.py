try:
    from PyQt4.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox,  QGridLayout
except ImportError:
    from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGridLayout

from calibre.utils.config import JSONConfig

# Config name should be unique and begin with "plugins/" to avoid clashing with Calibre's config
prefs = JSONConfig('plugins/xray_generator')
prefs.defaults['newFormat'] = True
prefs.defaults['cacheDir'] = None
prefs.defaults['autoExpandAliases'] = True
prefs.defaults['logfile'] = ""

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QGridLayout()
        self.setLayout(self.l)

        self.newFormatCheckboxLabel = QLabel('Generate &new format data (SQLite3)')
        self.l.addWidget(self.newFormatCheckboxLabel, 0, 0, 1, 1)
        self.newFormatCheckbox = QCheckBox(self)
        self.l.addWidget(self.newFormatCheckbox, 0, 1, 1, 1)
        self.newFormatCheckbox.setChecked(prefs['newFormat'])

        # ARTTBD Maybe should be a native directory picker?  Works for now..
        self.cacheDirLabel = QLabel("Caching directory (optional, useful if re-running for a given book)")
        self.l.addWidget(self.cacheDirLabel, 1, 0, 1, 1)
        self.cacheDirEdit = QLineEdit(self)
        self.l.addWidget(self.cacheDirEdit, 1, 1, 1, 1)
        self.cacheDirEdit.setText(prefs['cacheDir'])
        
        self.autoExpandAliasesLabel = QLabel('Auto-generate aliases from character names')
        self.l.addWidget(self.autoExpandAliasesLabel, 2, 0, 1, 1)
        self.autoExpandAliasesCheckbox = QCheckBox(self)
        self.l.addWidget(self.autoExpandAliasesCheckbox, 2, 1, 1, 1)
        self.autoExpandAliasesCheckbox.setChecked(prefs['autoExpandAliases'])
        
        self.logfileLabel = QLabel('Log file (optional)')
        self.l.addWidget(self.logfileLabel, 3, 0, 1, 1)
        self.logfileEdit = QLineEdit(self)
        self.l.addWidget(self.logfileEdit, 3, 1, 1, 1)
        self.logfileEdit.setText(prefs['logfile'])


    def save_settings(self):
        prefs['newFormat'] = self.newFormatCheckbox.isChecked()
        prefs['cacheDir'] = unicode(self.cacheDirEdit.text())
        prefs['autoExpandAliases'] = self.autoExpandAliasesCheckbox.isChecked()
        prefs['logfile'] = unicode(self.logfileEdit.text())
