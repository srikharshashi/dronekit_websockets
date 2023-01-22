import datetime
import requests

SERVER_URL="http://18.234.187.114:4000/flight/upload"

def make_request(id):
    date=datetime.datetime.now()
    body={
        "mission_id":id,
        "date":str(date)
    }
    
    result=requests.post(SERVER_URL,json=body)
    print(result.text)
    