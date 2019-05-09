import json
def handler(event,context):
    id = event.get("id","")
    secretString = event.get("data","")
    return {
            "id" : id,
            "data" : secretString
        }
