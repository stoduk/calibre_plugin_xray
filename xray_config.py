try:
    from PyQt4.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox,  QGridLayout
except ImportError:
    from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGridLayout

from calibre.utils.config import JSONConfig

# Config name should be unique and begin with "plugins/" to avoid clashing with Calibre's config
prefs = JSONConfig('plugins/xray_generator')
prefs.defaults['newFormat'] = True
prefs.defaults['cacheDir'] = None

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QGridLayout()
        self.setLayout(self.l)

        self.label = QLabel('Generate &new format data (SQLite3)')
        self.l.addWidget(self.label, 0, 0, 1, 1)

        self.newFormatCheckbox = QCheckBox(self)
        self.newFormatCheckbox.setObjectName("newFormatCheckbox")
        self.l.addWidget(self.newFormatCheckbox, 0, 1, 1, 1)
        self.newFormatCheckbox.setChecked(prefs['newFormat'])

        # ARTTBD Maybe should be a native directory picker?  Works for now..
        self.cacheDirLabel = QLabel("Caching directory (optional, useful if re-running for a given book)")
        self.l.addWidget(self.cacheDirLabel, 1, 0, 1, 1)
        self.cacheDirEdit = QLineEdit(self)
        self.l.addWidget(self.cacheDirEdit, 1, 1, 1, 1)
        self.cacheDirEdit.setText(prefs['cacheDir'])

    def save_settings(self):
        prefs['newFormat'] = self.newFormatCheckbox.isChecked()
        prefs['cacheDir'] = unicode(self.cacheDirEdit.text())
