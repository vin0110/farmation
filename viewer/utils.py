import requests
import json
from django.conf import settings

HPCC_END_POINT = settings.HPCC_END_POINT


def esp_call(query, **kwargs):
    # print('U', HPCC_END_POINT.format(query), kwargs)
    try:
        r = requests.post(HPCC_END_POINT.format(query), data=kwargs)
    except requests.exceptions.RequestException as e:
        raise ValueError("request POST failed: '{:s}'".format(str(e)))

    if r.status_code == 200:
        return json.loads(r.text)
    else:
        raise ValueError(f"ESP call ({query}) failed ({r.status_code})")
