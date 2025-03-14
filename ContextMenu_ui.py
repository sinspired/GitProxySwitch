# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ContextMenu.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QFont,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
)


class Ui_ContextMenu(object):
    def setupUi(self, ContextMenu):
        if not ContextMenu.objectName():
            ContextMenu.setObjectName("ContextMenu")
        ContextMenu.setEnabled(True)
        ContextMenu.resize(190, 212)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ContextMenu.sizePolicy().hasHeightForWidth())
        ContextMenu.setSizePolicy(sizePolicy)
        ContextMenu.setMinimumSize(QSize(190, 212))
        ContextMenu.setMaximumSize(QSize(250, 220))
        font = QFont()
        font.setKerning(True)
        ContextMenu.setFont(font)
        ContextMenu.setProperty("toolTipsVisible", False)
        self.verticalLayout = QVBoxLayout(ContextMenu)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSizeConstraint(
            QLayout.SizeConstraint.SetDefaultConstraint
        )
        self.verticalLayout.setContentsMargins(2, 9, 2, 9)
        self.statusLabel = QLabel(ContextMenu)
        self.statusLabel.setObjectName("statusLabel")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.statusLabel.sizePolicy().hasHeightForWidth())
        self.statusLabel.setSizePolicy(sizePolicy1)
        self.statusLabel.setMinimumSize(QSize(0, 30))
        self.statusLabel.setMaximumSize(QSize(16777215, 30))
        font1 = QFont()
        font1.setBold(False)
        font1.setKerning(True)
        self.statusLabel.setFont(font1)
        self.statusLabel.setMouseTracking(False)
        self.statusLabel.setLineWidth(0)
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )

        self.verticalLayout.addWidget(self.statusLabel)

        self.proxyButton = QPushButton(ContextMenu)
        self.proxyButton.setObjectName("proxyButton")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.proxyButton.sizePolicy().hasHeightForWidth())
        self.proxyButton.setSizePolicy(sizePolicy2)
        self.proxyButton.setMinimumSize(QSize(0, 40))
        self.proxyButton.setMaximumSize(QSize(1000, 50))
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
        self.verticalLayout_bottom.setObjectName("verticalLayout_bottom")
        self.verticalLayout_bottom.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(ContextMenu)
        self.frame.setObjectName("frame")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy3)
        self.frame.setMinimumSize(QSize(0, 50))
        self.frame.setMaximumSize(QSize(1000, 50))
        self.portLayout = QHBoxLayout(self.frame)
        self.portLayout.setSpacing(0)
        self.portLayout.setObjectName("portLayout")
        self.portLayout.setContentsMargins(9, 1, 9, 18)
        self.portlabel = QLabel(self.frame)
        self.portlabel.setObjectName("portlabel")
        self.portlabel.setMinimumSize(QSize(60, 0))

        self.portLayout.addWidget(self.portlabel)

        self.portInput = QLineEdit(self.frame)
        self.portInput.setObjectName("portInput")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.portInput.sizePolicy().hasHeightForWidth())
        self.portInput.setSizePolicy(sizePolicy4)
        self.portInput.setMinimumSize(QSize(0, 20))
        self.portInput.setMaximumSize(QSize(1000, 24))
        self.portInput.setTabletTracking(True)
        self.portInput.setAutoFillBackground(False)
        self.portInput.setInputMethodHints(Qt.InputMethodHint.ImhPreferNumbers)
        self.portInput.setText("10808")
        self.portInput.setMaxLength(5)
        self.portInput.setCursorPosition(5)
        self.portInput.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.portInput.setDragEnabled(False)
        self.portInput.setPlaceholderText("")
        self.portInput.setClearButtonEnabled(False)

        self.portLayout.addWidget(self.portInput)

        self.portListButton = QToolButton(self.frame)
        self.portListButton.setObjectName("portListButton")
        self.portListButton.setMinimumSize(QSize(24, 24))
        self.portListButton.setMaximumSize(QSize(24, 24))
        self.portListButton.setFont(font)
        self.portListButton.setMouseTracking(True)
        self.portListButton.setTabletTracking(True)
        self.portListButton.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.portListButton.setToolTipDuration(-1)
        self.portListButton.setAutoFillBackground(False)
        self.portListButton.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.portListButton.setText("\u25bc")

        self.portLayout.addWidget(self.portListButton)

        self.verticalLayout_bottom.addWidget(self.frame)

        self.autoStartButton = QPushButton(ContextMenu)
        self.autoStartButton.setObjectName("autoStartButton")
        self.autoStartButton.setMinimumSize(QSize(0, 30))
        self.autoStartButton.setCheckable(True)
        self.autoStartButton.setFlat(True)

        self.verticalLayout_bottom.addWidget(self.autoStartButton)

        self.exitButton = QPushButton(ContextMenu)
        self.exitButton.setObjectName("exitButton")
        self.exitButton.setMinimumSize(QSize(0, 30))
        self.exitButton.setCheckable(True)
        self.exitButton.setFlat(True)

        self.verticalLayout_bottom.addWidget(self.exitButton)

        self.verticalLayout.addLayout(self.verticalLayout_bottom)

        # if QT_CONFIG(shortcut)
        self.statusLabel.setBuddy(self.proxyButton)
        self.portlabel.setBuddy(self.portInput)
        # endif // QT_CONFIG(shortcut)

        self.retranslateUi(ContextMenu)
        self.portListButton.triggered["QAction*"].connect(self.portInput.selectAll)
        self.portListButton.clicked.connect(self.portInput.selectAll)

        self.proxyButton.setDefault(False)

        QMetaObject.connectSlotsByName(ContextMenu)

    # setupUi

    def retranslateUi(self, ContextMenu):
        ContextMenu.setWindowTitle(
            QCoreApplication.translate("ContextMenu", "ContextMenu", None)
        )
        self.statusLabel.setText(
            QCoreApplication.translate(
                "ContextMenu",
                "\u6b63\u5728\u68c0\u67e5\u4ee3\u7406\u72b6\u6001...",
                None,
            )
        )
        self.proxyButton.setText(
            QCoreApplication.translate(
                "ContextMenu", "\u5207\u6362git\u4ee3\u7406\u72b6\u6001", None
            )
        )
        self.portlabel.setText(
            QCoreApplication.translate(
                "ContextMenu", "\u4ee3\u7406\u7aef\u53e3\uff1a", None
            )
        )
        self.portInput.setInputMask("")
        # if QT_CONFIG(tooltip)
        self.portListButton.setToolTip(
            QCoreApplication.translate("ContextMenu", "\u5e38\u7528\u7aef\u53e3", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(statustip)
        self.portListButton.setStatusTip("")
        # endif // QT_CONFIG(statustip)
        # if QT_CONFIG(whatsthis)
        self.portListButton.setWhatsThis(
            QCoreApplication.translate(
                "ContextMenu",
                "\u4f7f\u7528\u5e38\u7528\u9884\u8bbe\u4ee3\u7406\u7aef\u53e3",
                None,
            )
        )
        # endif // QT_CONFIG(whatsthis)
        self.autoStartButton.setText(
            QCoreApplication.translate(
                "ContextMenu", "\u8bbe\u7f6e\u81ea\u52a8\u5f00\u673a\u542f\u52a8", None
            )
        )
        self.exitButton.setText(
            QCoreApplication.translate("ContextMenu", "\u9000\u51fa", None)
        )

    # retranslateUi
