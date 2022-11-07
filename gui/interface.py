# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/interface.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(618, 449)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.orchestrator = QtWidgets.QWidget()
        self.orchestrator.setEnabled(True)
        self.orchestrator.setObjectName("orchestrator")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.orchestrator)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.start_group = QtWidgets.QGroupBox(self.orchestrator)
        self.start_group.setObjectName("start_group")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.start_group)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.s_l1a = QtWidgets.QRadioButton(self.start_group)
        self.s_l1a.setProperty("data", "L1_A")
        self.s_l1a.setObjectName("s_l1a")
        self.horizontalLayout.addWidget(self.s_l1a)
        self.s_l1b = QtWidgets.QRadioButton(self.start_group)
        self.s_l1b.setProperty("data", "L1_B")
        self.s_l1b.setObjectName("s_l1b")
        self.horizontalLayout.addWidget(self.s_l1b)
        self.s_l2fb = QtWidgets.QRadioButton(self.start_group)
        self.s_l2fb.setProperty("data", "L2_FB")
        self.s_l2fb.setObjectName("s_l2fb")
        self.horizontalLayout.addWidget(self.s_l2fb)
        self.s_l2sm = QtWidgets.QRadioButton(self.start_group)
        self.s_l2sm.setProperty("data", "L2_SM")
        self.s_l2sm.setObjectName("s_l2sm")
        self.horizontalLayout.addWidget(self.s_l2sm)
        self.s_l2si = QtWidgets.QRadioButton(self.start_group)
        self.s_l2si.setProperty("data", "L2_SI")
        self.s_l2si.setObjectName("s_l2si")
        self.horizontalLayout.addWidget(self.s_l2si)
        self.s_l2ft = QtWidgets.QRadioButton(self.start_group)
        self.s_l2ft.setProperty("data", "L2_FT")
        self.s_l2ft.setObjectName("s_l2ft")
        self.horizontalLayout.addWidget(self.s_l2ft)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_5.addWidget(self.start_group)
        self.end_group = QtWidgets.QGroupBox(self.orchestrator)
        self.end_group.setObjectName("end_group")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.end_group)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.e_l1a = QtWidgets.QRadioButton(self.end_group)
        self.e_l1a.setProperty("data", "L1_A")
        self.e_l1a.setObjectName("e_l1a")
        self.horizontalLayout_2.addWidget(self.e_l1a)
        self.e_l1b = QtWidgets.QRadioButton(self.end_group)
        self.e_l1b.setProperty("data", "L1_B")
        self.e_l1b.setObjectName("e_l1b")
        self.horizontalLayout_2.addWidget(self.e_l1b)
        self.e_l2fb = QtWidgets.QRadioButton(self.end_group)
        self.e_l2fb.setProperty("data", "L2_FB")
        self.e_l2fb.setObjectName("e_l2fb")
        self.horizontalLayout_2.addWidget(self.e_l2fb)
        self.e_l2sm = QtWidgets.QRadioButton(self.end_group)
        self.e_l2sm.setProperty("data", "L2_SM")
        self.e_l2sm.setObjectName("e_l2sm")
        self.horizontalLayout_2.addWidget(self.e_l2sm)
        self.e_l2si = QtWidgets.QRadioButton(self.end_group)
        self.e_l2si.setProperty("data", "L2_SI")
        self.e_l2si.setObjectName("e_l2si")
        self.horizontalLayout_2.addWidget(self.e_l2si)
        self.e_l2ft = QtWidgets.QRadioButton(self.end_group)
        self.e_l2ft.setProperty("data", "L2_FT")
        self.e_l2ft.setObjectName("e_l2ft")
        self.horizontalLayout_2.addWidget(self.e_l2ft)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5.addWidget(self.end_group)
        self.data_group = QtWidgets.QGroupBox(self.orchestrator)
        self.data_group.setObjectName("data_group")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.data_group)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.data_group)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.in_dataRoot = QtWidgets.QLineEdit(self.data_group)
        self.in_dataRoot.setReadOnly(True)
        self.in_dataRoot.setObjectName("in_dataRoot")
        self.horizontalLayout_3.addWidget(self.in_dataRoot)
        self.btn_browse_dataRoot = QtWidgets.QPushButton(self.data_group)
        self.btn_browse_dataRoot.setObjectName("btn_browse_dataRoot")
        self.horizontalLayout_3.addWidget(self.btn_browse_dataRoot)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_16 = QtWidgets.QLabel(self.data_group)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_9.addWidget(self.label_16)
        self.in_bkpRoot = QtWidgets.QLineEdit(self.data_group)
        self.in_bkpRoot.setReadOnly(True)
        self.in_bkpRoot.setObjectName("in_bkpRoot")
        self.horizontalLayout_9.addWidget(self.in_bkpRoot)
        self.btn_browse_bkpRoot = QtWidgets.QPushButton(self.data_group)
        self.btn_browse_bkpRoot.setObjectName("btn_browse_bkpRoot")
        self.horizontalLayout_9.addWidget(self.btn_browse_bkpRoot)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_4 = QtWidgets.QLabel(self.data_group)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.in_bkpFile = QtWidgets.QLineEdit(self.data_group)
        self.in_bkpFile.setText("")
        self.in_bkpFile.setReadOnly(True)
        self.in_bkpFile.setObjectName("in_bkpFile")
        self.horizontalLayout_6.addWidget(self.in_bkpFile)
        self.btn_browse_bkpFile = QtWidgets.QPushButton(self.data_group)
        self.btn_browse_bkpFile.setObjectName("btn_browse_bkpFile")
        self.horizontalLayout_6.addWidget(self.btn_browse_bkpFile)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_5.addWidget(self.data_group)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.chk_pam = QtWidgets.QCheckBox(self.orchestrator)
        self.chk_pam.setObjectName("chk_pam")
        self.horizontalLayout_7.addWidget(self.chk_pam)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.btn_save = QtWidgets.QPushButton(self.orchestrator)
        self.btn_save.setObjectName("btn_save")
        self.horizontalLayout_7.addWidget(self.btn_save)
        self.verticalLayout_5.addLayout(self.horizontalLayout_7)
        self.tabWidget.addTab(self.orchestrator, "")
        self.l1a = QtWidgets.QWidget()
        self.l1a.setObjectName("l1a")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.l1a)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.l1a)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.l1a)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.in_l1a_wd = QtWidgets.QLineEdit(self.l1a)
        self.in_l1a_wd.setObjectName("in_l1a_wd")
        self.gridLayout.addWidget(self.in_l1a_wd, 0, 1, 1, 1)
        self.in_l1a_exe = QtWidgets.QLineEdit(self.l1a)
        self.in_l1a_exe.setObjectName("in_l1a_exe")
        self.gridLayout.addWidget(self.in_l1a_exe, 1, 1, 1, 1)
        self.btn_l1a_browse = QtWidgets.QPushButton(self.l1a)
        self.btn_l1a_browse.setObjectName("btn_l1a_browse")
        self.gridLayout.addWidget(self.btn_l1a_browse, 2, 1, 1, 1)
        self.chk_l1a_script = QtWidgets.QCheckBox(self.l1a)
        self.chk_l1a_script.setObjectName("chk_l1a_script")
        self.gridLayout.addWidget(self.chk_l1a_script, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tabWidget.addTab(self.l1a, "")
        self.l1b = QtWidgets.QWidget()
        self.l1b.setObjectName("l1b")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.l1b)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_5 = QtWidgets.QLabel(self.l1b)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.l1b)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 0, 0, 1, 1)
        self.in_l1b_wd = QtWidgets.QLineEdit(self.l1b)
        self.in_l1b_wd.setObjectName("in_l1b_wd")
        self.gridLayout_3.addWidget(self.in_l1b_wd, 0, 1, 1, 1)
        self.in_l1b_exe = QtWidgets.QLineEdit(self.l1b)
        self.in_l1b_exe.setObjectName("in_l1b_exe")
        self.gridLayout_3.addWidget(self.in_l1b_exe, 1, 1, 1, 1)
        self.btn_l1b_browse = QtWidgets.QPushButton(self.l1b)
        self.btn_l1b_browse.setObjectName("btn_l1b_browse")
        self.gridLayout_3.addWidget(self.btn_l1b_browse, 2, 1, 1, 1)
        self.chk_l1b_script = QtWidgets.QCheckBox(self.l1b)
        self.chk_l1b_script.setObjectName("chk_l1b_script")
        self.gridLayout_3.addWidget(self.chk_l1b_script, 2, 0, 1, 1)
        self.verticalLayout_11.addLayout(self.gridLayout_3)
        self.tabWidget.addTab(self.l1b, "")
        self.l2fb = QtWidgets.QWidget()
        self.l2fb.setObjectName("l2fb")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.l2fb)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_7 = QtWidgets.QLabel(self.l2fb)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 1, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.l2fb)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 0, 0, 1, 1)
        self.in_l2fb_wd = QtWidgets.QLineEdit(self.l2fb)
        self.in_l2fb_wd.setObjectName("in_l2fb_wd")
        self.gridLayout_4.addWidget(self.in_l2fb_wd, 0, 1, 1, 1)
        self.in_l2fb_exe = QtWidgets.QLineEdit(self.l2fb)
        self.in_l2fb_exe.setObjectName("in_l2fb_exe")
        self.gridLayout_4.addWidget(self.in_l2fb_exe, 1, 1, 1, 1)
        self.btn_l2fb_browse = QtWidgets.QPushButton(self.l2fb)
        self.btn_l2fb_browse.setObjectName("btn_l2fb_browse")
        self.gridLayout_4.addWidget(self.btn_l2fb_browse, 2, 1, 1, 1)
        self.chk_l2fb_script = QtWidgets.QCheckBox(self.l2fb)
        self.chk_l2fb_script.setObjectName("chk_l2fb_script")
        self.gridLayout_4.addWidget(self.chk_l2fb_script, 2, 0, 1, 1)
        self.verticalLayout_10.addLayout(self.gridLayout_4)
        self.tabWidget.addTab(self.l2fb, "")
        self.l2sm = QtWidgets.QWidget()
        self.l2sm.setObjectName("l2sm")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.l2sm)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_9 = QtWidgets.QLabel(self.l2sm)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 1, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.l2sm)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 0, 0, 1, 1)
        self.in_l2sm_wd = QtWidgets.QLineEdit(self.l2sm)
        self.in_l2sm_wd.setObjectName("in_l2sm_wd")
        self.gridLayout_5.addWidget(self.in_l2sm_wd, 0, 1, 1, 1)
        self.in_l2sm_exe = QtWidgets.QLineEdit(self.l2sm)
        self.in_l2sm_exe.setObjectName("in_l2sm_exe")
        self.gridLayout_5.addWidget(self.in_l2sm_exe, 1, 1, 1, 1)
        self.btn_l2sm_browse = QtWidgets.QPushButton(self.l2sm)
        self.btn_l2sm_browse.setObjectName("btn_l2sm_browse")
        self.gridLayout_5.addWidget(self.btn_l2sm_browse, 2, 1, 1, 1)
        self.chk_l2sm_script = QtWidgets.QCheckBox(self.l2sm)
        self.chk_l2sm_script.setObjectName("chk_l2sm_script")
        self.gridLayout_5.addWidget(self.chk_l2sm_script, 2, 0, 1, 1)
        self.verticalLayout_9.addLayout(self.gridLayout_5)
        self.tabWidget.addTab(self.l2sm, "")
        self.l2si = QtWidgets.QWidget()
        self.l2si.setObjectName("l2si")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.l2si)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_11 = QtWidgets.QLabel(self.l2si)
        self.label_11.setObjectName("label_11")
        self.gridLayout_6.addWidget(self.label_11, 1, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.l2si)
        self.label_12.setObjectName("label_12")
        self.gridLayout_6.addWidget(self.label_12, 0, 0, 1, 1)
        self.in_l2si_wd = QtWidgets.QLineEdit(self.l2si)
        self.in_l2si_wd.setObjectName("in_l2si_wd")
        self.gridLayout_6.addWidget(self.in_l2si_wd, 0, 1, 1, 1)
        self.in_l2si_exe = QtWidgets.QLineEdit(self.l2si)
        self.in_l2si_exe.setObjectName("in_l2si_exe")
        self.gridLayout_6.addWidget(self.in_l2si_exe, 1, 1, 1, 1)
        self.btn_l2si_browse = QtWidgets.QPushButton(self.l2si)
        self.btn_l2si_browse.setObjectName("btn_l2si_browse")
        self.gridLayout_6.addWidget(self.btn_l2si_browse, 2, 1, 1, 1)
        self.chk_l2si_script = QtWidgets.QCheckBox(self.l2si)
        self.chk_l2si_script.setObjectName("chk_l2si_script")
        self.gridLayout_6.addWidget(self.chk_l2si_script, 2, 0, 1, 1)
        self.verticalLayout_8.addLayout(self.gridLayout_6)
        self.tabWidget.addTab(self.l2si, "")
        self.l2ft = QtWidgets.QWidget()
        self.l2ft.setObjectName("l2ft")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.l2ft)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_13 = QtWidgets.QLabel(self.l2ft)
        self.label_13.setObjectName("label_13")
        self.gridLayout_7.addWidget(self.label_13, 1, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.l2ft)
        self.label_14.setObjectName("label_14")
        self.gridLayout_7.addWidget(self.label_14, 0, 0, 1, 1)
        self.in_l2ft_wd = QtWidgets.QLineEdit(self.l2ft)
        self.in_l2ft_wd.setObjectName("in_l2ft_wd")
        self.gridLayout_7.addWidget(self.in_l2ft_wd, 0, 1, 1, 1)
        self.in_l2ft_exe = QtWidgets.QLineEdit(self.l2ft)
        self.in_l2ft_exe.setObjectName("in_l2ft_exe")
        self.gridLayout_7.addWidget(self.in_l2ft_exe, 1, 1, 1, 1)
        self.btn_l2ft_browse = QtWidgets.QPushButton(self.l2ft)
        self.btn_l2ft_browse.setObjectName("btn_l2ft_browse")
        self.gridLayout_7.addWidget(self.btn_l2ft_browse, 2, 1, 1, 1)
        self.chk_l2ft_script = QtWidgets.QCheckBox(self.l2ft)
        self.chk_l2ft_script.setObjectName("chk_l2ft_script")
        self.gridLayout_7.addWidget(self.chk_l2ft_script, 2, 0, 1, 1)
        self.verticalLayout_7.addLayout(self.gridLayout_7)
        self.tabWidget.addTab(self.l2ft, "")
        self.pam = QtWidgets.QWidget()
        self.pam.setObjectName("pam")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pam)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_15 = QtWidgets.QLabel(self.pam)
        self.label_15.setObjectName("label_15")
        self.gridLayout_8.addWidget(self.label_15, 1, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.pam)
        self.label_17.setObjectName("label_17")
        self.gridLayout_8.addWidget(self.label_17, 0, 0, 1, 1)
        self.in_pam_wd = QtWidgets.QLineEdit(self.pam)
        self.in_pam_wd.setObjectName("in_pam_wd")
        self.gridLayout_8.addWidget(self.in_pam_wd, 0, 1, 1, 1)
        self.in_pam_exe = QtWidgets.QLineEdit(self.pam)
        self.in_pam_exe.setObjectName("in_pam_exe")
        self.gridLayout_8.addWidget(self.in_pam_exe, 1, 1, 1, 1)
        self.btn_pam_browse = QtWidgets.QPushButton(self.pam)
        self.btn_pam_browse.setObjectName("btn_pam_browse")
        self.gridLayout_8.addWidget(self.btn_pam_browse, 2, 1, 1, 1)
        self.chk_pam_script = QtWidgets.QCheckBox(self.pam)
        self.chk_pam_script.setObjectName("chk_pam_script")
        self.gridLayout_8.addWidget(self.chk_pam_script, 2, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_8)
        self.tabWidget.addTab(self.pam, "")
        self.horizontalLayout_8.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "E2ES Orchestrator - Configuration Setup"))
        self.start_group.setTitle(_translate("MainWindow", "Start"))
        self.s_l1a.setText(_translate("MainWindow", "L1A"))
        self.s_l1b.setText(_translate("MainWindow", "L1B"))
        self.s_l2fb.setText(_translate("MainWindow", "L2FB"))
        self.s_l2sm.setText(_translate("MainWindow", "L2SM"))
        self.s_l2si.setText(_translate("MainWindow", "L2SI"))
        self.s_l2ft.setText(_translate("MainWindow", "L2FT"))
        self.end_group.setTitle(_translate("MainWindow", "End"))
        self.e_l1a.setText(_translate("MainWindow", "L1A"))
        self.e_l1b.setText(_translate("MainWindow", "L1B"))
        self.e_l2fb.setText(_translate("MainWindow", "L2FB"))
        self.e_l2sm.setText(_translate("MainWindow", "L2SM"))
        self.e_l2si.setText(_translate("MainWindow", "L2SI"))
        self.e_l2ft.setText(_translate("MainWindow", "L2FT"))
        self.data_group.setTitle(_translate("MainWindow", "Data"))
        self.label_3.setText(_translate("MainWindow", "Data Root:"))
        self.btn_browse_dataRoot.setText(_translate("MainWindow", "Browse"))
        self.label_16.setText(_translate("MainWindow", "Backup Root:"))
        self.btn_browse_bkpRoot.setText(_translate("MainWindow", "Browse"))
        self.label_4.setText(_translate("MainWindow", "Backup File:"))
        self.btn_browse_bkpFile.setText(_translate("MainWindow", "Browse"))
        self.chk_pam.setText(_translate("MainWindow", "Use PAM"))
        self.btn_save.setText(_translate("MainWindow", "Save and Close"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.orchestrator), _translate("MainWindow", "Orchestrator"))
        self.label_2.setText(_translate("MainWindow", "Executable:"))
        self.label.setText(_translate("MainWindow", "Working Directory:"))
        self.btn_l1a_browse.setText(_translate("MainWindow", "Browse"))
        self.chk_l1a_script.setText(_translate("MainWindow", "Script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.l1a), _translate("MainWindow", "L1A"))
        self.label_5.setText(_translate("MainWindow", "Executable:"))
        self.label_6.setText(_translate("MainWindow", "Working Directory:"))
        self.btn_l1b_browse.setText(_translate("MainWindow", "Browse"))
        self.chk_l1b_script.setText(_translate("MainWindow", "Script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.l1b), _translate("MainWindow", "L1B"))
        self.label_7.setText(_translate("MainWindow", "Executable:"))
        self.label_8.setText(_translate("MainWindow", "Working Directory:"))
        self.btn_l2fb_browse.setText(_translate("MainWindow", "Browse"))
        self.chk_l2fb_script.setText(_translate("MainWindow", "Script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.l2fb), _translate("MainWindow", "L2FB"))
        self.label_9.setText(_translate("MainWindow", "Executable:"))
        self.label_10.setText(_translate("MainWindow", "Working Directory:"))
        self.btn_l2sm_browse.setText(_translate("MainWindow", "Browse"))
        self.chk_l2sm_script.setText(_translate("MainWindow", "Script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.l2sm), _translate("MainWindow", "L2SM"))
        self.label_11.setText(_translate("MainWindow", "Executable:"))
        self.label_12.setText(_translate("MainWindow", "Working Directory:"))
        self.btn_l2si_browse.setText(_translate("MainWindow", "Browse"))
        self.chk_l2si_script.setText(_translate("MainWindow", "Script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.l2si), _translate("MainWindow", "L2SI"))
        self.label_13.setText(_translate("MainWindow", "Executable:"))
        self.label_14.setText(_translate("MainWindow", "Working Directory:"))
        self.btn_l2ft_browse.setText(_translate("MainWindow", "Browse"))
        self.chk_l2ft_script.setText(_translate("MainWindow", "Script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.l2ft), _translate("MainWindow", "L2FT"))
        self.label_15.setText(_translate("MainWindow", "Executable:"))
        self.label_17.setText(_translate("MainWindow", "Working Directory:"))
        self.btn_pam_browse.setText(_translate("MainWindow", "Browse"))
        self.chk_pam_script.setText(_translate("MainWindow", "Script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pam), _translate("MainWindow", "PAM"))
