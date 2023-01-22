import json
from websockets import connect as wsconnect
from location_monitor import LocationMonitor
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import argparse
import asyncio
from mission import do_mission


from util_funs import arm_and_takeoff, create_mission, distance_to_current_waypoint, parse_json ,validate_json
parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = "tcp:127.0.0.1:5763"



# Connect to vehicle 
print('GCS:Connecting to vehicle on:  %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

WSS_URL=r"ws://18.234.187.114:4000/socket/command?device=drone"

# create a thread to connect to the websocket to broadcast location

locationMonitorThread=LocationMonitor(vehicle=vehicle)
locationMonitorThread.start()


# Write a WebSocket Exactly here to listen to launch command and launch the drone 

async def hello(uri):
    async with wsconnect(uri) as websocket:
        await websocket.send(json.dumps({"message":"gs_update","status":"unarmed"}))
        print("connecting to Server")
        while True:
            message= await websocket.recv()
            print(message)
            print("Waiting for commands")
            message=json.loads(message)
            if("command" in message): 
                if(message["command"]=="LAUNCH"):
                    print("LAUNCH")
                    await websocket.send(json.dumps({"message":"gs_update","status":"armed"}))
                    do_mission(vehicle=vehicle,data=message["waypoints"])
                    asyncio.sleep(8)
                    await websocket.send(json.dumps({"message":"gs_update","status":"unarmed"}))

            

asyncio.run(hello(WSS_URL))



