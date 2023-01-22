import json
from threading import Thread
import time
import asyncio
from websockets import connect

from util_funs import parse_json

WSS_URL="ws://18.234.187.114:4000/socket/command?device=transmitter"

class LocationMonitor(Thread):
    def __init__(self,vehicle,):
        Thread.__init__(self)
        self.vehicle=vehicle
        self.isRunning=True
    
    def terminate(self):
        self.isRunning=False
        
    async def broadcast(self,url):
        async with connect(url) as websocket:
            while self.isRunning:
                await websocket.send(json.dumps({"message":"location_update","lat":self.vehicle.location.global_frame.lat,"long":self.vehicle.location.global_frame.lon}))
                await asyncio.sleep(0.5)
        
        
    def run(self):
        asyncio.run(self.broadcast(WSS_URL))
        
            
