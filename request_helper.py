from __future__ import print_function
import requests
import json
from threading import Thread


class RequestHelper(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.wayPoints=None
    
    def run(self):
        URL1="http://127.0.0.1:4000/missions/query/all"
        URL2="http://127.0.0.1:4000/missions/query/"
        try:
            response1=requests.get(URL1)
            responseJson1=json.loads(response1.content)
            c=0
            print("GCS:Choose a mission from the following")
            for dictt in responseJson1:
                print(c,str(dictt["name"]))
                c+=1
            n=int(input())
            selectedMission=responseJson1[n]["name"]
            URL2=URL2+selectedMission
            print("GCS:Downloading coordinates for",selectedMission)
            response2=requests.get(URL2)
            responseJson2=json.loads(response2.content)
            wayPoint=json.loads(responseJson2["waypoints"])
            print("GCS:Downloading waypoints complete")
            self.wayPoints=wayPoint
            
            
        except Exception as err:
            print("There was an error")
            print(err)
            