import boto3
import os
from handler import Handler

from appsyncclient import AppSyncClient

import logging
import json, base64

region = os.environ.get("region","us-east-2")
apiId = os.environ.get("appsync_api_id","")

logger = logging.getLogger("appsync-listener")
s3client = boto3.client("s3",region_name=region)

class S3Handler(Handler):
    def __init__(self,*args,**kargs):
        pass

    def handle(self,event,context):
        logger.info(event)
        bucketName = event.get("s3",{}).get("bucket",{}).get("name",None)
        objectKey = event.get("s3",{}).get("object",{}).get("key",None)
        
        if bucketName != None and objectKey != None :
            
            logger.info(f"Received event for {bucketName} for file {objectKey}")
            
            file = s3client.get_object(Bucket=bucketName,Key=objectKey)
            filecontent = file.get("Body").read().decode("utf-8")
            self.pushUpdates(f"arn:aws:s3:::{bucketName}:{objectKey}",str(filecontent))
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
        datab64 = base64.b64encode(data.encode('utf-8'))
        logger.info(datab64.decode('utf-8'))
        query = json.dumps({"query": "mutation {\n  updateResource(id:\""+id+"\",data:\""+datab64.decode('utf-8')+"\") {\n    id\n    data\n  }\n}\n"})
        logger.info(query)
        response = appsyncClient.execute(data=query)
        logger.info({
            "response" : response
        })
