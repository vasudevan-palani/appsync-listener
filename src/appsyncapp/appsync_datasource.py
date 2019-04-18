import json
def handler(event,context):
    id = event.get("id","")
    secretString = event.get("secretString","")
    return {
            "id" : id,
            "secretString" : secretString
        }
