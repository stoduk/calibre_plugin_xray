from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox

from calibre.utils.config import JSONConfig

# Config name should be unique and begin with "plugins/" to avoid clashing with Calibre's config
prefs = JSONConfig('plugins/xray_generator')
prefs.defaults['newFormat'] = True
prefs.defaults['hello_world_msg'] = 'Hello, World!'

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel('Generate &new format data (SQLite3)')
        self.l.addWidget(self.label)

        self.newFormatCheckbox = QCheckBox(self)
        self.newFormatCheckbox.setObjectName("newFormatCheckbox")
        self.l.addWidget(self.newFormatCheckbox) #, 2, 0, 1, 1)
        self.newFormatCheckbox.setChecked(prefs['newFormat'])

    def save_settings(self):
        prefs['newFormat'] = self.newFormatCheckbox.isChecked()