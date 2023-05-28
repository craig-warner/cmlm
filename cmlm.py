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
from time import sleep

# GUI 
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QCheckBox, QComboBox, QListWidget, QLineEdit,
    QLineEdit, QSpinBox, QDoubleSpinBox, QSlider,
    QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import ( 
    Qt
)

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
        self.addBody()
        self.show()

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


def CheckHealth():
    cluster_cfg = hjson.load(open(args.cfile))  
    health = hjson.load(open(args.hfile))
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

# CLI Parser
parser = argparse.ArgumentParser(description='CXL Memory Lake Monitor')
parser.add_argument("--cfile", help="Configuration file (.hjson)", default="cfg/two.hjson")
parser.add_argument("--pfile", help="Performance file (.hjson)",default="perf.hjson")
parser.add_argument("--hfile", help="Health file (.hjson)",default="health.hjson")
parser.add_argument("-v", "--verbose", help="Increase output verbosity",action ="store_true") 
parser.add_argument("--nogui", help="No Graphical User Interface",action ="store_true") 
args = parser.parse_args()

# Global Strings
health_str = "Health Alert:"

#  
if(args.nogui):
    health_file_check = os.path.isfile(args.hfile)
    if(health_file_check):
        CheckHealth()
    else:
        err_line = "Error: Health File (%s) not found" % args.hfile
        print(err_line)
        exit(1)
else:
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()