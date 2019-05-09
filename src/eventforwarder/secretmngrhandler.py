import boto3
import os
from handler import Handler

from appsyncclient import AppSyncClient

import logging
import json

region = os.environ.get("region","us-east-2")
apiId = os.environ.get("appsync_api_id","")

logger = logging.getLogger("appsync-listener")
secretmngr = boto3.client("secretsmanager",region_name=region)

class SecretMngrHandler(Handler):
    def __init__(self,*args,**kargs):
        pass

    def handle(self,event,context):
        secretId = event.get("detail",{}).get("requestParameters",{}).get("secretId",None)
        if secretId != None:
            logger.info("Received event with secretId : "+str(secretId))
            secretString = self.getSecretValue(secretId)
            self.pushUpdates(secretId,secretString)
            return {
                "statusCode":200,
                "body" : "{}"
            }
        return {
            "statusCode":400,
            "body" : "{}"
        }

    def getSecretValue(self,secretId):
        secretValue = secretmngr.get_secret_value(SecretId=secretId)
        return secretValue.get("SecretString")

    def pushUpdates(self,id,data):
        appsyncClient = AppSyncClient(authenticationType="API_KEY",apiId=apiId,region=region)
        data = data.replace("\"","\\\"")
        query = json.dumps({"query": "mutation {\n  updateResource(id:\"arn:aws:secretsmanager:::"+id+"\",data:\""+data+"\") {\n    id\n    data\n  }\n}\n"})
        response = appsyncClient.execute(data=query)
        logger.info({
            "response" : response
        })
