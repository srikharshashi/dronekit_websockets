from __future__ import print_function
import codecs
import json
import time
from location_monitor import LocationMonitor
from request_helper import RequestHelper
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
from util_funs import arm_and_takeoff, create_mission, distance_to_current_waypoint, parse_json ,validate_json

def do_mission(vehicle,data):
    # Validate the JSON File
    print('GCS:Validating JSON')
    data=json.loads(data)


    # print("GCS: Fetching missions")

    # thread=RequestHelper()
    # thread.start()
    # thread.join()
    # data=thread.wayPoints


    # Sort the JSON 
    print('GCS:Sorting JSON by waypoint order')
    data = sorted(data, key=lambda d: d['index'])

    n_points=len(data)
    print(*data)



    # Parsing the JSON file for Waypoints 
    print('GCS:Parsing JSON and adding waypoints')
    waypoints =parse_json(data)


    # Create a new mission from the parsed waypoints 
    create_mission(vehicle=vehicle,waypoints= waypoints)



    # Arm the Drone and Take Off with to a specified altitiude
    print('GCS:Starting to Arm')


    altitude=10
    arm_and_takeoff(aTargetAltitude= altitude,vehicle=vehicle)



    print("GCS:Starting mission")
    # Reset mission set to first (0) waypoint
    vehicle.commands.next=0


    # Set mode to AUTO to start mission
    vehicle.mode = VehicleMode("AUTO")



    # Mission Monitoring 
    while True:
        nextwaypoint=vehicle.commands.next
        print('GCS:Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint(vehicle=vehicle)))
        
    
        if nextwaypoint==n_points+1: #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
            print("Exit 'standard' mission when start heading to final waypoint (5)")
            break
        time.sleep(1)


    print('GCS:Return to launch')
    vehicle.mode = VehicleMode("RTL")
    
    
   

