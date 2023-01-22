import json
from waypoint import WayPoint
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
from pymavlink import mavutil
import math
import time


def validate_json():
    f=open('sample.json')
    try:
        data=json.load(f)
        f.close()
        return data
    except ValueError:
        print("JSON Invalid Error")
        exit()
    except FileNotFoundError:
        print("JSON does not exist")
        exit()
    
def parse_json(data):
    waypointList=[]
    for waypoint in data:
        waypointList.append(WayPoint(float(waypoint["lat"]),float(waypoint["long"]),int(waypoint["index"])))
        # cords.append((float(waypoint["latitude"]),float(waypoint["longitude"])))
    return waypointList

def create_mission(vehicle,waypoints):
    cmds = vehicle.commands

    print("GCS:Clear any existing commands")
    cmds.clear() 
    
    print("GCS:Define/add new commands.")
    # Add new commands. The meaning/order of the parameters is documented in the Command class. 
     
    initialAltitude=10.0
    #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, initialAltitude))
    
    for waypoint in waypoints:
        newcmd=Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 5, 0, 0, 0, waypoint.lat, waypoint.long, initialAltitude)
        cmds.add(newcmd)
    
    # add a dummy waypoint n+1 at n to let us know we have reached destination 
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, waypoints[-1].lat, waypoints[-1].long, initialAltitude))
        
    print("GCS:Uploading new commands to vehicle")
    cmds.upload()


def distance_to_current_waypoint(vehicle):
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def download_mission(vehicle):
    """
    Download the current mission from the vehicle.
    """
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready() # wait until download is complete.

def arm_and_takeoff(aTargetAltitude,vehicle):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("GCS:Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print("GCS:Waiting for vehicle to initialise...")
        time.sleep(1)

    print("GCS:Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print("GCS:Waiting for arming...")
        time.sleep(1)

    print("GCS:Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
    

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print("GCS:Altitude: ", vehicle.location.global_relative_frame.alt)      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print("GCS:Reached target altitude")
            break
        time.sleep(1)