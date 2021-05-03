import requests
import json

END_POINT = 'http://localhost:8124/WsEcl/submit/query/thor/{:s}/json'


def esp_call(query, **kwargs):
    # print('U', END_POINT.format(query), kwargs)
    r = requests.post(END_POINT.format(query), data=kwargs)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        raise ValueError(f"ESP call ({query}) failed ({r.status_code})")
