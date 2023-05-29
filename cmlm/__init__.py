#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
CXL Memory Lake Monitor
author: Craig Warner
"""

import os
import platform
import sys
import argparse
import hjson
from cmlm.version import __version__
from time import sleep

# GUI 
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QCheckBox, QComboBox, QListWidget, QLineEdit,
    QLineEdit, QSpinBox, QDoubleSpinBox, QSlider,
    QHBoxLayout, QVBoxLayout, QToolBar, QAction, QStatusBar,
    QDialog, QDialogButtonBox, QFileDialog
)
from PyQt5.QtCore import ( 
    Qt
)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("CMLM")

        QBtn = QDialogButtonBox.Ok 

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()

        message_str = "CXL Memory Lake Monitor\nWritten by: Craig Warner\nVersion: %s" % (__version__)
        message = QLabel(message_str)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        # Grab Configuration Settings
        self.cluster_cfg = hjson.load(open(args.cfile))  
        # Start the  
        self.initUI()

    def initUI(self):
        self.wid = QtWidgets.QWidget(self)
        self.setCentralWidget(self.wid)
        self.setGeometry(0,100,512,384)
        self.setWindowTitle("CXL Memory Lake Monitor")
        self.createActions()
        self.addMenuToWindow()
        self.addBody()
        self.show()

    def createActions(self):
        self.loadHealthLogAction = QAction()
        self.loadHealthLogAction.setText("Load Health Log")
        self.loadPerfLogAction= QAction()
        self.loadPerfLogAction.setText("Load Performance Log")
        self.exitAppAction= QAction()
        self.exitAppAction.setText("Quit")

        self.aboutAction= QAction()
        self.aboutAction.setText("About")

        self.updateHealthAction = QAction()
        # QAction(QIcon("bug.png"), "Your &button2", self)
        self.updateHealthAction.setText("Update Health Information")
        self.updateHealthAction.setStatusTip("Use this to update health status of the cluster")

    def addMenuToWindow(self):

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction(self.updateHealthAction)
        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.loadHealthLogAction)
        file_menu.addAction(self.loadPerfLogAction)
        file_menu.addAction(self.updateHealthAction)
        file_menu.addSeparator()
        file_menu.addAction(self.exitAppAction)

        help_menu = menu.addMenu("&Help")
        help_menu.addAction(self.aboutAction)

        self.loadHealthLogAction.triggered.connect(self.doLoadHealthLog)
        self.loadPerfLogAction.triggered.connect(self.doLoadPerfLog)
        self.exitAppAction.triggered.connect(self.doExitApp)
        self.aboutAction.triggered.connect(self.doAbout)
        self.updateHealthAction.triggered.connect(self.doUpdateHealth)

    def doUpdateHealth(self, s):
        print("Update Health")

    def doLoadHealthLog(self):
        print("Load Health Log")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.health_file_name, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","JSON Files (*.hjson)", options=options)
        CheckHealth(self.health_file_name)

    def doLoadPerfLog(self):
        print("Load Perf Log")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.perf_file_name, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","JSON Files (*.hjson)", options=options)

    def doExitApp(self):
        exit(0)

    def doAbout(self):
        print("About")
        dlg = AboutDialog(self)
        dlg.exec()

    def addBody(self):
        hbox1 = QtWidgets.QHBoxLayout()

        self.info_type_combo_box = QComboBox()
        self.info_type_combo_box.addItems(["Config", "Health", "Performance"])
                # There is an alternate signal to send the text.
        self.info_type_combo_box.currentTextChanged.connect( self.info_type_text_changed )

        hbox1.addWidget(self.info_type_combo_box)

        self.subcluster_combo_box = QComboBox()
        self.subcluster_combo_box.addItems(["1", "2"])
        self.subcluster_combo_box.currentIndexChanged.connect( self.subcluster_changed)
        hbox1.addWidget(self.subcluster_combo_box)

        self.comp_combo_box = QComboBox()
        self.comp_combo_box.addItems(["Devices", "LeafSwitch", "Hosts"])
        self.comp_combo_box.currentTextChanged.connect( self.comp_text_changed )
        hbox1.addWidget(self.comp_combo_box)

        #comp_num_combo_box = QComboBox()
        #comp_num_combo_box.addItems(["1", "2", "3","4","5","6","7","8"])
        #comp_num_combo_box.currentIndexChanged.connect( self.comp_num_changed)
        #hbox1.addWidget(comp_num_combo_box)
         
        label = QLabel("Capacity")
        font = label.font()
        font.setPointSize(30)
        label.setFont(font)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.setGeometry(QtCore.QRect(0, 0, 300, 600))
        hbox2.addWidget(label)

        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)

        self.wid.setLayout(vbox1)

    def info_type_text_changed(self,s):
        if(args.verbose):
            print("Info Type Changed to:",end='')
            print(s)

    def subcluster_changed(self,i):
        if(args.verbose):
            print("Subcluster Changed to:",i+1)

    def comp_text_changed(self,s):
        if(args.verbose):
            print("Component Type Changed to:",end='')
            print(s)

    #def comp_num_changed(self,i):
    #    if(args.verbose):
    #        print("Component Changed to:",i+1)

    def gen_cfg_devices_lines(self):
        devices = self.cluster_cfg["subcluster_settings"]  
        lines = []
        for i in range(0, devices["num_devices"]):
            line = "Capacity: %d GB" % (devices["device_cap"])
            lines.append(line)
        return lines

    def update_display(self):
        info_type = self.info_type_combo_box.currentText()
        comp_type = self.comp_type_combo_box.currentText()
        if(info_type == "Config"):
            if(comp_type == "Devices"):
                lines = self.gen_cfg_devices_lines()
            elif (comp_type == "LeafSwitch"):
                lines = self.gen_cfg_leafswitch_lines()
            elif (comp_type == "Hosts"):
                lines = self.gen_cfg_hosts_lines()
        elif(info_type == "Health"):
            if(comp_type == "Devices"):
                lines = self.gen_health_devices_lines()
            elif (comp_type == "LeafSwitch"):
                lines = self.gen_health_leafswitch_lines()
            elif (comp_type == "Hosts"):
                lines = self.gen_health_hosts_lines()
        elif(info_type == "Performance"):
            if(comp_type == "Devices"):
                lines = self.gen_perf_devices_lines()
            elif (comp_type == "LeafSwitch"):
                lines = self.gen_perf_leafswitch_lines()
            elif (comp_type == "Hosts"):
                lines = self.gen_perf_hosts_lines()

def CheckHealthDevice(sc,device_num,threshold,device):
    err_cnt = 0
    if(device["ErrorsPerDay"] > threshold):
        err_line = "%s: Subcluster %d: Device %d: Error Rate: Errors Per Day: (%d) exceeds threshold (%d)" % (health_str,sc, device, device["ErrorsPerDay"],threshold)
        print(err_line)
        err_cnt = err_cnt + 1 
    if(device["RdyForReplacement"]):
        err_line = "%s: Subcluster %d: Device %d: Ready for Replacement" % (health_str,sc, device)
        print(err_line)
        err_cnt = err_cnt + 1 
    return err_cnt

def CheckHealthSwitchPort(sc,sw_num,port_num,threshold,port):
    err_cnt = 0
    if(port["ErrorsPerDay"] > threshold):
        err_line = "%s: Subcluster %d: Switch %d: Port: %d Error Rate: Errors Per Day: (%d) exceeds threshold (%d)" % (health_str,sc, sw_num,port_num, port["ErrorsPerDay"],threshold) 
        print(err_line)
        err_cnt = err_cnt + 1 
    if(port["Broken"]):
        err_line = "%s: Subcluster %d: Switch %d: Port: %d Broken" % (health_str,sc, sw_num,port_num)
        print(err_line)
        err_cnt = err_cnt + 1 
    return err_cnt
      
def CheckHealthHost(sc,host_num,host):
    err_cnt = 0
    if(host["NonResponsive"]):
        err_line = "%s: Subcluster %d: Host %d: Is Not Responsive" % (health_str,sc, host_num)
        print(err_line)
        err_cnt = err_cnt + 1 
    return err_cnt


def CheckHealth(health_file_name):
    cluster_cfg = hjson.load(open(args.cfile))  
    health = hjson.load(open(health_file_name))
    err_cnt = 0
    for sc in range(0,cluster_cfg["num_subclusters"]):
        for device_num in range(0,cluster_cfg["subcluster_settings"]["num_devices"]):
            err_cnt = err_cnt + CheckHealthDevice(sc,device_num,
                              cluster_cfg["thresholds"]["device"],
                              health["scs"][sc]["devices"][device_num])
        for switch_num in range(0,cluster_cfg["subcluster_settings"]["num_switches"]):
            for port_num in range(0,cluster_cfg["subcluster_settings"]["num_switch_ports"]):
                err_cnt = err_cnt + CheckHealthSwitchPort(sc,switch_num,port_num,
                              cluster_cfg["thresholds"]["link"],
                              health["scs"][sc]["lsw"][switch_num]["ports"][port_num])
        for host_num in range(0,cluster_cfg["subcluster_settings"]["num_hosts"]):
            err_cnt = err_cnt + CheckHealthHost(sc,host_num,
                              health["scs"][sc]["hosts"][host_num])

    if(args.nogui):
        if(err_cnt == 0):
            print("The Cluster is Healthy")
    return err_cnt

#
# CMLM Start
#


# CLI Parser
parser = argparse.ArgumentParser(description='CXL Memory Lake Monitor')
parser.add_argument("--cfile", help="Configuration file (.hjson)", default="cfg/two.hjson")
parser.add_argument("--pfile", help="Performance file (.hjson)",default="perf.hjson")
parser.add_argument("--hfile", help="Health file (.hjson)",default="health.hjson")
parser.add_argument("-v", "--verbose", help="Increase output verbosity",action ="store_true") 
parser.add_argument("--nogui", help="No Graphical User Interface",action ="store_true") 
parser.add_argument('-V', '--version', action='version', version="%(prog)s ("+__version__+")")
args = parser.parse_args()

# Global Strings
health_str = "Health Alert:"

#  
if(args.nogui):
    health_file_check = os.path.isfile(args.hfile)
    if(health_file_check):
        CheckHealth(args.hfile)
    else:
        err_line = "Error: Health File (%s) not found" % args.hfile
        print(err_line)
        exit(1)
else:
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()