import boto3
import os
from handler import Handler

from appsyncclient import AppSyncClient

import logging
import json

region = os.environ.get("region","us-east-2")

logger = logging.getLogger("appsync-listener")
secretmngr = boto3.client("secretsmanager",region_name=region)

class SecretMngrHandler(Handler):
    def __init__(self,*args,**kargs):
        pass

    def handle(self,event,context):
        print(event)
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

    def pushUpdates(self,secretId,secretString):
        appsyncClient = AppSyncClient(authenticationType="API_KEY")
        secretString = secretString.replace("\"","\\\"")
        query = json.dumps({"query": "mutation {\n  updateSecret(id:\""+secretId+"\",secretString:\""+secretString+"\") {\n    id\n    secretString\n  }\n}\n"})
        response = appsyncClient.execute(data=query)
        logger.info({
            "response" : response
        })
