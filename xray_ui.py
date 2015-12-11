# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xray.ui'
#
# Created: Sun Jan  4 19:30:29 2015
#      by: PyQt4 UI code generator 4.10.1
#

try:
    from PyQt4.Qt import QtCore, QtGui
except ImportError:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5 import Qt as QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_XRay(object):
    def setupUi(self, XRay):
        XRay.setObjectName(_fromUtf8("XRay"))
        XRay.resize(507, 387)
        self.gridLayout_9 = QtGui.QGridLayout(XRay)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.gridLayout_6 = QtGui.QGridLayout()
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.xrayDirEdit = QtGui.QLineEdit(XRay)
        self.xrayDirEdit.setObjectName(_fromUtf8("xrayDirEdit"))
        self.gridLayout_6.addWidget(self.xrayDirEdit, 1, 0, 1, 1)
        self.label_6 = QtGui.QLabel(XRay)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_6.addWidget(self.label_6, 0, 0, 1, 1)
        self.xrayBrowseButton = QtGui.QPushButton(XRay)
        self.xrayBrowseButton.setObjectName(_fromUtf8("xrayBrowseButton"))
        self.gridLayout_6.addWidget(self.xrayBrowseButton, 1, 1, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_6, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(XRay)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.shelfariEdit = QtGui.QLineEdit(XRay)
        self.shelfariEdit.setObjectName(_fromUtf8("shelfariEdit"))
        self.gridLayout.addWidget(self.shelfariEdit, 1, 0, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.wikipediaEdit = QtGui.QLineEdit(XRay)
        self.wikipediaEdit.setObjectName(_fromUtf8("wikipediaEdit"))
        self.gridLayout_2.addWidget(self.wikipediaEdit, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(XRay)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_2, 2, 0, 1, 1)
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_5 = QtGui.QLabel(XRay)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_5.addWidget(self.label_5, 0, 0, 1, 1)
        self.unpackDirEdit = QtGui.QLineEdit(XRay)
        self.unpackDirEdit.setObjectName(_fromUtf8("unpackDirEdit"))
        self.gridLayout_5.addWidget(self.unpackDirEdit, 1, 0, 1, 1)
        self.unpackBrowseButton = QtGui.QPushButton(XRay)
        self.unpackBrowseButton.setObjectName(_fromUtf8("unpackBrowseButton"))
        self.gridLayout_5.addWidget(self.unpackBrowseButton, 1, 1, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_5, 3, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_3 = QtGui.QLabel(XRay)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)
        self.offsetEdit = QtGui.QLineEdit(XRay)
        self.offsetEdit.setObjectName(_fromUtf8("offsetEdit"))
        self.gridLayout_3.addWidget(self.offsetEdit, 1, 0, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_3, 4, 0, 1, 1)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.aliasesEdit = QtGui.QLineEdit(XRay)
        self.aliasesEdit.setObjectName(_fromUtf8("aliasesEdit"))
        self.gridLayout_4.addWidget(self.aliasesEdit, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(XRay)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_4.addWidget(self.label_4, 0, 0, 1, 1)
        self.aliasBrowseButton = QtGui.QPushButton(XRay)
        self.aliasBrowseButton.setObjectName(_fromUtf8("aliasBrowseButton"))
        self.gridLayout_4.addWidget(self.aliasBrowseButton, 1, 1, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_4, 5, 0, 1, 1)
        self.gridLayout_8 = QtGui.QGridLayout()
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.newFormatCheckbox = QtGui.QCheckBox(XRay)
        self.newFormatCheckbox.setObjectName(_fromUtf8("newFormatCheckbox"))
        self.gridLayout_8.addWidget(self.newFormatCheckbox, 2, 0, 1, 1)
        self.gridLayout_9.addLayout(self.gridLayout_8, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(XRay)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_9.addWidget(self.buttonBox, 7, 0, 1, 1)

        self.retranslateUi(XRay)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), XRay.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), XRay.reject)
        #QtCore.QMetaObject.connectSlotsByName(XRay)
        self.buttonBox.accepted.connect(XRay.accept)
        self.buttonBox.rejected.connect(XRay.reject)

    def retranslateUi(self, XRay):
        XRay.setWindowTitle(_translate("XRay", "XRay", None))
        self.label_6.setText(_translate("XRay", "Directory for saving X-Ray file", None))
        self.xrayBrowseButton.setText(_translate("XRay", "Browse", None))
        self.label.setText(_translate("XRay", "Shelfari URL", None))
        self.label_2.setText(_translate("XRay", "Wikipedia URL (optional)", None))
        self.label_5.setText(_translate("XRay", "Directory for unpacking book (optional, will use temporary directory if blank)", None))
        self.unpackBrowseButton.setText(_translate("XRay", "Browse", None))
        self.label_3.setText(_translate("XRay", "Offset (optional)", None))
        self.label_4.setText(_translate("XRay", "Aliases file (optional, will be created if necessary)", None))
        self.aliasBrowseButton.setText(_translate("XRay", "Browse", None))
        self.newFormatCheckbox.setText(_translate("XRay", "Create new XRay format", None))

