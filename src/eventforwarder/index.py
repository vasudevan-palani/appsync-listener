import boto3
import logging

import sys
sys.path.append("./deps")

from logging import config
from os import path
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
config.fileConfig(log_file_path)


from secretmngrhandler import SecretMngrHandler
from s3handler import S3Handler
from dynamodbhandler import DynamodbHandler

registeredHandlers = {
    "aws.secretsmanager" : SecretMngrHandler(),
    "aws:s3" : S3Handler(),
    "aws:dynamodb" : DynamodbHandler()
}

logger = logging.getLogger("appsync-listener")

def unknownEventHandler():
    return {
        "statusCode" : 404,
        "body" : "{}"
    }

def exceptionHandler():
    return {
        "statusCode" : 500,
        "body" : "{}"
    }


def handler(originalEvent,context):

    event = originalEvent

    records = event.get("Records")

    if records != None:
        event = records[0]

    source = event.get("source") or event.get("eventSource")

    try:
        if source != None and registeredHandlers.get(source) != None:
            logger.info("Found handler for "+str(source))
            handler = registeredHandlers.get(source)
            response = handler.handle(event,context)
            logger.info("Returning response : "+str(response))
            return response

    except Exception as e:
        print(e)
        return exceptionHandler()
    return unknownEventHandler()
