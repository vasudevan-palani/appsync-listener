import sys
sys.path.append("./deps")
sys.path.append(".")
import json

from appsyncapp.appsync_datasource import handler
def test_ok():
    response = handler({
        "id" : "123",
        "secretString" : "12355"
    },{})
    assert json.loads(response.get("id")) == 123
    assert json.loads(response.get("secretString")) == 12355
