import sys,os
sys.path.append("./deps")
sys.path.append(".")
sys.path.append("./eventforwarder")

os.environ["region"] ="us-east-2"
os.environ["appsync_url"] ="https://XXXX.appsync-api.us-east-2.amazonaws.com/graphql"
os.environ["appsync_api_id"] ="XXXX"

import json
from mockito import when, mock, unstub, ANY

from eventforwarder.index import handler

from eventforwarder.secretmngrhandler import SecretMngrHandler
from appsyncclient import AppSyncClient


def test_unknownevent():
    response = handler({
        "id" : "123",
        "secret" : "12355"
    },{})
    assert response.get("statusCode") == 404

def test_unknownevent():
    response = handler({
        "id" : "123",
        "secret" : "12355"
    },{})
    assert response.get("statusCode") == 404

def test_querySecretOK():

    event = {
        "source" : "aws.secretsmanager",
        "detail" : {
                "requestParameters" : {
                    "secretId" : "XXXX"
            }
        }
    }
    when(SecretMngrHandler).getSecretValue(...).thenReturn(json.dumps({
        "secretString" : "{\"clientId\":\"sdsdf\"}"
    }))
    when(AppSyncClient).subscribe(...).thenReturn({})
    when(AppSyncClient).sendRequest(...).thenReturn({})
    when(AppSyncClient).getApiKey(...).thenReturn("dsfsdf")

    response = handler(event,{})
    assert response.get("statusCode") == 200

def test_querySecretNotValidEvent():
    event = {
        "source" : "aws.secretsmanager",
        "detail" : {
            "userIdentity" : {
                "requestParameters" : {
                }
            }
        }
    }
    when(SecretMngrHandler).getSecretValue(...).thenReturn(json.dumps({
        "secretString" : "{\"clientId\":\"sdsdf\"}"
    }))
    when(AppSyncClient).subscribe(...).thenReturn({})
    when(AppSyncClient).sendRequest(...).thenReturn({})
    when(AppSyncClient).getApiKey(...).thenReturn("dsfsdf")


    response = handler(event,{})
    assert response.get("statusCode") == 400

def test_querySecretNotValidSecretId():
    event = {
        "source" : "aws.secretsmanager",
        "detail" : {
                "requestParameters" : {
                    "secretId" : "XXX"
            }
        }
    }
    when(SecretMngrHandler).getSecretValue(...).thenReturn(json.dumps({
        "secretString" : "{\"clientId\":\"sdsdf\"}"
    }))
    when(AppSyncClient).subscribe(...).thenReturn({})
    when(AppSyncClient).sendRequest(...).thenRaise(Exception)
    when(AppSyncClient).getApiKey(...).thenReturn("dsfsdf")


    response = handler(event,{})
    assert response.get("statusCode") == 500
