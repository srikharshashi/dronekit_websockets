from __future__ import print_function
import argparse

import json
from decimal import Decimal
import signal
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
from datetime import datetime
import math
from pymavlink import mavutil
from goprocam import GoProCamera, constants
import pymavlink
import logging
import os
import tempfile
import shutil

parser = argparse.ArgumentParser(
    description='Demonstrates basic mission operations.')
parser.add_argument('--connect',
                    help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


picCount=0


def getfilename(vehicle):
    datetime=datetime.now().strftime("%d/%m/%Y-%H:%M")
    location=vehicle.location.global_frame.lat+"-"+vehicle.location.global_frame.long
    filename=datetime+"-"+location+picCount
    picCount+=1
    return filename



def take_picture(vehicle):
    gpCam = GoProCamera.GoPro(
                ip_address=GoProCamera.GoPro.getWebcamIP("usb0"))
    gpCam.downloadLastMedia(gpCam.take_photo(), custom_filename=getfilename(vehicle=vehicle))

        
# Vehicle Connection 
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

x=0
@vehicle.on_message(['WAYPOINT_CURRENT', 'MISSION_CURRENT'])
def listener(self, name, m):
    global x
    if m.seq > x:
        take_picture(vehicle=vehicle)
        x += 1