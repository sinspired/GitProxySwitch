# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ContextMenu.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QPushButton, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget)

class Ui_ContextMenuWidget(object):
    def setupUi(self, ContextMenuWidget):
        if not ContextMenuWidget.objectName():
            ContextMenuWidget.setObjectName(u"ContextMenuWidget")
        ContextMenuWidget.setWindowModality(Qt.WindowModality.WindowModal)
        ContextMenuWidget.setEnabled(True)
        ContextMenuWidget.resize(190, 212)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ContextMenuWidget.sizePolicy().hasHeightForWidth())
        ContextMenuWidget.setSizePolicy(sizePolicy)
        ContextMenuWidget.setMinimumSize(QSize(190, 212))
        ContextMenuWidget.setMaximumSize(QSize(190, 212))
        font = QFont()
        font.setKerning(True)
        ContextMenuWidget.setFont(font)
        ContextMenuWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        ContextMenuWidget.setStyleSheet(u"")
        ContextMenuWidget.setProperty(u"toolTipsVisible", False)
        self.verticalLayout = QVBoxLayout(ContextMenuWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 9, 0, 9)
        self.statusLabel = QLabel(ContextMenuWidget)
        self.statusLabel.setObjectName(u"statusLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.statusLabel.sizePolicy().hasHeightForWidth())
        self.statusLabel.setSizePolicy(sizePolicy1)
        self.statusLabel.setMinimumSize(QSize(180, 30))
        self.statusLabel.setMaximumSize(QSize(200, 30))
        font1 = QFont()
        font1.setBold(False)
        font1.setKerning(True)
        self.statusLabel.setFont(font1)
        self.statusLabel.setMouseTracking(False)
        self.statusLabel.setLineWidth(0)
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)

        self.verticalLayout.addWidget(self.statusLabel)

        self.proxyButton = QPushButton(ContextMenuWidget)
        self.proxyButton.setObjectName(u"proxyButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.proxyButton.sizePolicy().hasHeightForWidth())
        self.proxyButton.setSizePolicy(sizePolicy2)
        self.proxyButton.setMinimumSize(QSize(180, 40))
        self.proxyButton.setMaximumSize(QSize(200, 50))
        font2 = QFont()
        font2.setBold(True)
        font2.setKerning(True)
        self.proxyButton.setFont(font2)
        self.proxyButton.setMouseTracking(True)
        self.proxyButton.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.proxyButton.setAutoFillBackground(False)
        self.proxyButton.setCheckable(True)
        self.proxyButton.setAutoRepeat(False)
        self.proxyButton.setAutoExclusive(False)
        self.proxyButton.setAutoDefault(False)
        self.proxyButton.setFlat(True)

        self.verticalLayout.addWidget(self.proxyButton)

        self.verticalLayout_bottom = QVBoxLayout()
        self.verticalLayout_bottom.setSpacing(0)
        self.verticalLayout_bottom.setObjectName(u"verticalLayout_bottom")
        self.verticalLayout_bottom.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(ContextMenuWidget)
        self.frame.setObjectName(u"frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy3)
        self.frame.setMinimumSize(QSize(180, 50))
        self.frame.setMaximumSize(QSize(200, 50))
        self.portLayout = QHBoxLayout(self.frame)
        self.portLayout.setSpacing(0)
        self.portLayout.setObjectName(u"portLayout")
        self.portLayout.setContentsMargins(9, 1, 9, 18)
        self.portlabel = QLabel(self.frame)
        self.portlabel.setObjectName(u"portlabel")
        self.portlabel.setMinimumSize(QSize(60, 0))

        self.portLayout.addWidget(self.portlabel)

        self.portInput = QLineEdit(self.frame)
        self.portInput.setObjectName(u"portInput")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.portInput.sizePolicy().hasHeightForWidth())
        self.portInput.setSizePolicy(sizePolicy4)
        self.portInput.setMinimumSize(QSize(0, 20))
        self.portInput.setMaximumSize(QSize(100, 24))
        self.portInput.setTabletTracking(True)
        self.portInput.setAutoFillBackground(False)
        self.portInput.setInputMethodHints(Qt.InputMethodHint.ImhPreferNumbers)
        self.portInput.setText(u"10808")
        self.portInput.setMaxLength(5)
        self.portInput.setCursorPosition(5)
        self.portInput.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.portInput.setDragEnabled(False)
        self.portInput.setPlaceholderText(u"")
        self.portInput.setClearButtonEnabled(False)

        self.portLayout.addWidget(self.portInput)

        self.portListButton = QToolButton(self.frame)
        self.portListButton.setObjectName(u"portListButton")
        self.portListButton.setMinimumSize(QSize(24, 24))
        self.portListButton.setMaximumSize(QSize(24, 24))
        self.portListButton.setFont(font)
        self.portListButton.setMouseTracking(True)
        self.portListButton.setTabletTracking(True)
        self.portListButton.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.portListButton.setToolTipDuration(-1)
        self.portListButton.setAutoFillBackground(False)
        self.portListButton.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.portListButton.setText(u"\u25bc")

        self.portLayout.addWidget(self.portListButton)

        self.portInput.raise_()
        self.portListButton.raise_()
        self.portlabel.raise_()

        self.verticalLayout_bottom.addWidget(self.frame)

        self.autoStartButton = QPushButton(ContextMenuWidget)
        self.autoStartButton.setObjectName(u"autoStartButton")
        self.autoStartButton.setMinimumSize(QSize(180, 30))
        self.autoStartButton.setMaximumSize(QSize(200, 16777215))
        self.autoStartButton.setCheckable(True)
        self.autoStartButton.setFlat(False)

        self.verticalLayout_bottom.addWidget(self.autoStartButton)

        self.exitButton = QPushButton(ContextMenuWidget)
        self.exitButton.setObjectName(u"exitButton")
        self.exitButton.setMinimumSize(QSize(180, 30))
        self.exitButton.setMaximumSize(QSize(200, 16777215))
        self.exitButton.setCheckable(True)
        self.exitButton.setFlat(False)

        self.verticalLayout_bottom.addWidget(self.exitButton)


        self.verticalLayout.addLayout(self.verticalLayout_bottom)

#if QT_CONFIG(shortcut)
        self.statusLabel.setBuddy(self.proxyButton)
        self.portlabel.setBuddy(self.portInput)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(ContextMenuWidget)
        self.portListButton.triggered["QAction*"].connect(self.portInput.selectAll)
        self.portListButton.clicked.connect(self.portInput.selectAll)

        self.proxyButton.setDefault(False)


        QMetaObject.connectSlotsByName(ContextMenuWidget)
    # setupUi

    def retranslateUi(self, ContextMenuWidget):
        ContextMenuWidget.setWindowTitle(QCoreApplication.translate("ContextMenuWidget", u"ContextMenu", None))
#if QT_CONFIG(tooltip)
        ContextMenuWidget.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.statusLabel.setText(QCoreApplication.translate("ContextMenuWidget", u"\u6b63\u5728\u68c0\u67e5\u4ee3\u7406\u72b6\u6001...", None))
        self.proxyButton.setText(QCoreApplication.translate("ContextMenuWidget", u"\u5207\u6362git\u4ee3\u7406\u72b6\u6001", None))
        self.portlabel.setText(QCoreApplication.translate("ContextMenuWidget", u"\u4ee3\u7406\u7aef\u53e3\uff1a", None))
        self.portInput.setInputMask("")
#if QT_CONFIG(tooltip)
        self.portListButton.setToolTip(QCoreApplication.translate("ContextMenuWidget", u"\u5e38\u7528\u7aef\u53e3", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.portListButton.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.portListButton.setWhatsThis(QCoreApplication.translate("ContextMenuWidget", u"\u4f7f\u7528\u5e38\u7528\u9884\u8bbe\u4ee3\u7406\u7aef\u53e3", None))
#endif // QT_CONFIG(whatsthis)
        self.autoStartButton.setText(QCoreApplication.translate("ContextMenuWidget", u"\u8bbe\u7f6e\u81ea\u52a8\u5f00\u673a\u542f\u52a8", None))
        self.exitButton.setText(QCoreApplication.translate("ContextMenuWidget", u"\u9000\u51fa", None))
    # retranslateUi

