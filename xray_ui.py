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
        
        # Window is setup with a main grid, in to which
        # one sub-grid is added for each item
        # (where an item is typically a label on one line, 
        #  then an edit box on the next, optionally with a button)
        # Could make it all one grid, but this perhaps makes some sense..
        
        # gridLayoutMain - grid for the whole window
        self.gridLayoutMain = QtGui.QGridLayout(XRay)
        self.gridLayoutMain.setObjectName(_fromUtf8("gridLayoutMain"))
        
        # gridLayout1 - Directory for saving X-Ray file
        self.gridLayout1 = QtGui.QGridLayout()
        self.gridLayout1.setObjectName(_fromUtf8("gridLayout1"))
        self.gridLayoutMain.addLayout(self.gridLayout1, 0, 0, 1, 1)

        self.xrayDirEdit = QtGui.QLineEdit(XRay)
        self.xrayDirEdit.setObjectName(_fromUtf8("xrayDirEdit"))
        self.gridLayout1.addWidget(self.xrayDirEdit, 1, 0, 1, 1)
        
        self.label_6 = QtGui.QLabel(XRay)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout1.addWidget(self.label_6, 0, 0, 1, 1)
        
        self.xrayBrowseButton = QtGui.QPushButton(XRay)
        self.xrayBrowseButton.setObjectName(_fromUtf8("xrayBrowseButton"))
        self.gridLayout1.addWidget(self.xrayBrowseButton, 1, 1, 1, 1)
        
        
        # gridLayout2 - Shelfari URL
        self.gridLayout2 = QtGui.QGridLayout()
        self.gridLayout2.setObjectName(_fromUtf8("gridLayout2"))
        self.gridLayoutMain.addLayout(self.gridLayout2, 1, 0, 1, 1)

        self.label = QtGui.QLabel(XRay)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout2.addWidget(self.label, 0, 0, 1, 1)
        
        self.shelfariEdit = QtGui.QLineEdit(XRay)
        self.shelfariEdit.setObjectName(_fromUtf8("shelfariEdit"))
        self.gridLayout2.addWidget(self.shelfariEdit, 1, 0, 1, 1)
        
        # gridLayout3 - Wikipedia URL
        self.gridLayout3 = QtGui.QGridLayout()
        self.gridLayout3.setObjectName(_fromUtf8("gridLayout3"))
        self.gridLayoutMain.addLayout(self.gridLayout3, 2, 0, 1, 1)

        self.wikipediaEdit = QtGui.QLineEdit(XRay)
        self.wikipediaEdit.setObjectName(_fromUtf8("wikipediaEdit"))
        self.gridLayout3.addWidget(self.wikipediaEdit, 1, 0, 1, 1)

        self.label_2 = QtGui.QLabel(XRay)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout3.addWidget(self.label_2, 0, 0, 1, 1)

        # gridLayout4 - Unpack directory
        self.gridLayout4 = QtGui.QGridLayout()
        self.gridLayout4.setObjectName(_fromUtf8("gridLayout4"))
        self.gridLayoutMain.addLayout(self.gridLayout4, 3, 0, 1, 1)
        
        self.label_5 = QtGui.QLabel(XRay)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout4.addWidget(self.label_5, 0, 0, 1, 1)
        
        self.unpackDirEdit = QtGui.QLineEdit(XRay)
        self.unpackDirEdit.setObjectName(_fromUtf8("unpackDirEdit"))
        self.gridLayout4.addWidget(self.unpackDirEdit, 1, 0, 1, 1)
        
        self.unpackBrowseButton = QtGui.QPushButton(XRay)
        self.unpackBrowseButton.setObjectName(_fromUtf8("unpackBrowseButton"))
        self.gridLayout4.addWidget(self.unpackBrowseButton, 1, 1, 1, 1)
        
        # gridLayout5 - offset
        self.gridLayout5 = QtGui.QGridLayout()
        self.gridLayout5.setObjectName(_fromUtf8("gridLayout5"))
        self.gridLayoutMain.addLayout(self.gridLayout5, 4, 0, 1, 1)

        self.label_3 = QtGui.QLabel(XRay)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout5.addWidget(self.label_3, 0, 0, 1, 1)

        self.offsetEdit = QtGui.QLineEdit(XRay)
        self.offsetEdit.setObjectName(_fromUtf8("offsetEdit"))
        self.gridLayout5.addWidget(self.offsetEdit, 1, 0, 1, 1)
        
        # gridLayout6  - 
        self.gridLayout6 = QtGui.QGridLayout()
        self.gridLayout6.setObjectName(_fromUtf8("gridLayout6"))
        self.gridLayoutMain.addLayout(self.gridLayout6, 5, 0, 1, 1)

        self.aliasesEdit = QtGui.QLineEdit(XRay)
        self.aliasesEdit.setObjectName(_fromUtf8("aliasesEdit"))
        self.gridLayout6.addWidget(self.aliasesEdit, 1, 0, 1, 1)

        self.label_4 = QtGui.QLabel(XRay)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout6.addWidget(self.label_4, 0, 0, 1, 1)
        
        self.aliasBrowseButton = QtGui.QPushButton(XRay)
        self.aliasBrowseButton.setObjectName(_fromUtf8("aliasBrowseButton"))
        self.gridLayout6.addWidget(self.aliasBrowseButton, 1, 1, 1, 1)
        
        # gridLayout7 - new/old format checkbox
        self.gridLayout7 = QtGui.QGridLayout()
        self.gridLayout7.setObjectName(_fromUtf8("gridLayout7"))
        self.gridLayoutMain.addLayout(self.gridLayout7, 6, 0, 1, 1)
        
        self.newFormatCheckbox = QtGui.QCheckBox(XRay)
        self.newFormatCheckbox.setObjectName(_fromUtf8("newFormatCheckbox"))
        self.gridLayout7.addWidget(self.newFormatCheckbox, 2, 0, 1, 1)
        
        # OK/cancel buttons
        self.buttonBox = QtGui.QDialogButtonBox(XRay)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayoutMain.addWidget(self.buttonBox, 7, 0, 1, 1)

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

