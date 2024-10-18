# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'SyncDogUI.ui'
##
# Created by: Qt User Interface Compiler version 6.7.0
##
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QMainWindow, QPushButton, QSizePolicy,
                               QSpacerItem, QStatusBar, QWidget)


class Ui_SyncDog(object):
    def setupUi(self, SyncDog):
        if not SyncDog.objectName():
            SyncDog.setObjectName(u"SyncDog")
        SyncDog.setEnabled(True)
        SyncDog.resize(492, 229)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SyncDog.sizePolicy().hasHeightForWidth())
        SyncDog.setSizePolicy(sizePolicy)
        SyncDog.setMinimumSize(QSize(0, 0))
        SyncDog.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setPointSize(10)
        SyncDog.setFont(font)
        self.centralwidget = QWidget(SyncDog)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setMinimumSize(QSize(0, 0))
        self.centralwidget.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_6 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.layout_options = QGridLayout()
        self.layout_options.setSpacing(0)
        self.layout_options.setObjectName(u"layout_options")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.button_AtoB = QPushButton(self.centralwidget)
        self.button_AtoB.setObjectName(u"button_AtoB")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.button_AtoB.sizePolicy().hasHeightForWidth())
        self.button_AtoB.setSizePolicy(sizePolicy2)
        self.button_AtoB.setMinimumSize(QSize(70, 40))
        self.button_AtoB.setMaximumSize(QSize(70, 40))

        self.horizontalLayout_3.addWidget(self.button_AtoB)

        self.button_BtoA = QPushButton(self.centralwidget)
        self.button_BtoA.setObjectName(u"button_BtoA")
        sizePolicy2.setHeightForWidth(
            self.button_BtoA.sizePolicy().hasHeightForWidth())
        self.button_BtoA.setSizePolicy(sizePolicy2)
        self.button_BtoA.setMinimumSize(QSize(70, 40))
        self.button_BtoA.setMaximumSize(QSize(70, 40))

        self.horizontalLayout_3.addWidget(self.button_BtoA)

        self.button_mirror = QPushButton(self.centralwidget)
        self.button_mirror.setObjectName(u"button_mirror")
        self.button_mirror.setMinimumSize(QSize(70, 40))
        self.button_mirror.setMaximumSize(QSize(70, 40))

        self.horizontalLayout_3.addWidget(self.button_mirror)

        self.layout_options.addLayout(self.horizontalLayout_3, 6, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.label_a = QLabel(self.centralwidget)
        self.label_a.setObjectName(u"label_a")
        sizePolicy.setHeightForWidth(
            self.label_a.sizePolicy().hasHeightForWidth())
        self.label_a.setSizePolicy(sizePolicy)
        self.label_a.setMinimumSize(QSize(0, 20))
        self.label_a.setFrameShape(QFrame.Shape.WinPanel)
        self.label_a.setFrameShadow(QFrame.Shadow.Sunken)
        self.label_a.setLineWidth(1)
        self.label_a.setMidLineWidth(0)

        self.horizontalLayout.addWidget(self.label_a)

        self.button_a = QPushButton(self.centralwidget)
        self.button_a.setObjectName(u"button_a")
        self.button_a.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout.addWidget(self.button_a)

        self.layout_options.addLayout(self.horizontalLayout, 0, 0, 2, 1)

        self.verticalSpacer_5 = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_options.addItem(self.verticalSpacer_5, 5, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.label_b = QLabel(self.centralwidget)
        self.label_b.setObjectName(u"label_b")
        sizePolicy.setHeightForWidth(
            self.label_b.sizePolicy().hasHeightForWidth())
        self.label_b.setSizePolicy(sizePolicy)
        self.label_b.setMinimumSize(QSize(0, 20))
        self.label_b.setFrameShape(QFrame.Shape.WinPanel)
        self.label_b.setFrameShadow(QFrame.Shadow.Sunken)
        self.label_b.setLineWidth(1)
        self.label_b.setMidLineWidth(0)

        self.horizontalLayout_2.addWidget(self.label_b)

        self.button_b = QPushButton(self.centralwidget)
        self.button_b.setObjectName(u"button_b")
        self.button_b.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_2.addWidget(self.button_b)

        self.layout_options.addLayout(self.horizontalLayout_2, 3, 0, 2, 1)

        self.verticalSpacer_4 = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_options.addItem(self.verticalSpacer_4, 7, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(
            20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.layout_options.addItem(self.verticalSpacer_3, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.button_action = QPushButton(self.centralwidget)
        self.button_action.setObjectName(u"button_action")
        self.button_action.setMinimumSize(QSize(120, 40))
        self.button_action.setMaximumSize(QSize(0, 40))

        self.horizontalLayout_4.addWidget(self.button_action)

        self.horizontalSpacer_3 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.button_refresh = QPushButton(self.centralwidget)
        self.button_refresh.setObjectName(u"button_refresh")
        self.button_refresh.setMinimumSize(QSize(120, 40))
        self.button_refresh.setMaximumSize(QSize(70, 40))

        self.horizontalLayout_4.addWidget(self.button_refresh)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.layout_options.addLayout(self.horizontalLayout_4, 8, 0, 2, 1)

        self.horizontalLayout_6.addLayout(self.layout_options)

        SyncDog.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(SyncDog)
        self.statusbar.setObjectName(u"statusbar")
        SyncDog.setStatusBar(self.statusbar)

        self.retranslateUi(SyncDog)

        QMetaObject.connectSlotsByName(SyncDog)
    # setupUi

    def retranslateUi(self, SyncDog):
        SyncDog.setWindowTitle(
            QCoreApplication.translate("SyncDog", u"SyncDog", None))
        self.button_AtoB.setText(
            QCoreApplication.translate("SyncDog", u"A to B", None))
        self.button_BtoA.setText(
            QCoreApplication.translate("SyncDog", u"B to A", None))
        self.button_mirror.setText(
            QCoreApplication.translate("SyncDog", u"Mirror", None))
        self.label.setText(QCoreApplication.translate(
            "SyncDog", u"Directory A", None))
        self.label_a.setText(QCoreApplication.translate(
            "SyncDog", u"Select a path...", None))
        self.button_a.setText(
            QCoreApplication.translate("SyncDog", u"...", None))
        self.label_2.setText(QCoreApplication.translate(
            "SyncDog", u"Directory B", None))
        self.label_b.setText(QCoreApplication.translate(
            "SyncDog", u"Select a path...", None))
        self.button_b.setText(
            QCoreApplication.translate("SyncDog", u"...", None))
        self.button_action.setText(
            QCoreApplication.translate("SyncDog", u"Synchronize", None))
        self.button_refresh.setText(
            QCoreApplication.translate("SyncDog", u"Refresh", None))
    # retranslateUi
