import boto3
import os
from handler import Handler

from appsyncclient import AppSyncClient

import logging
import json

region = os.environ.get("region","us-east-2")
apiId = os.environ.get("appsync_api_id","")

logger = logging.getLogger("appsync-listener")

class DynamodbHandler(Handler):
    def __init__(self,*args,**kargs):
        pass

    def handle(self,event,context):
        logger.info(event)
        keys = event.get("dynamodb",{}).get("Keys",{})
        newimage = event.get("dynamodb",{}).get("NewImage",{})
        eventSourceARN = event.get("eventSourceARN","")

        try:
            tableName = eventSourceARN.split(":")[5].split("/")[1]
        except IndexError as e:
            pass
        keystring = ""
        for key in keys:
            for keyvalue in keys.get(key,{}):
                if(keystring != ""):
                    keystring = keystring +":"
                keystring=keystring+keys.get(key).get(keyvalue,"")


        data = {}
        for key in newimage:
            for keyvalue in newimage.get(key,{}):
                data.update({key:newimage.get(key,{}).get(keyvalue)})
        
        if tableName != None and newimage != None :
            
            logger.info(f"Received event for {tableName} for {keystring}")
            
            self.pushUpdates(f"arn:aws:dynamodb:::{tableName}:{keystring}",json.dumps(data))
            return {
                "statusCode":200,
                "body" : "{}"
            }
        return {
            "statusCode":400,
            "body" : "{}"
        }

    def pushUpdates(self,id,data):
        appsyncClient = AppSyncClient(authenticationType="API_KEY",apiId=apiId,region=region)
        data = data.replace('\\"','"')
        data = data.replace("\"","\\\"")
        logger.info(data)
        query = json.dumps({"query": "mutation {\n  updateResource(id:\""+id+"\",data:\""+data+"\") {\n    id\n    data\n  }\n}\n"})
        logger.info(query)
        response = appsyncClient.execute(data=query)
        logger.info({
            "response" : response
        })
