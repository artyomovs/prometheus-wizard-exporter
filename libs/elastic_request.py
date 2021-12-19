import requests
from datetime import datetime
# import json

HEADERS = {"Content-Type": "application/json"}


def get_elastic_index_state(options):
    start = datetime.now()
    response = requests.request(
        method="GET",
        url=options.get("url"),
        headers=HEADERS,
        data=options.get("payload", {}),
        verify=False,
        timeout=120,
    )
    print(response.json())
    end = datetime.now()
    seconds = (end - start).seconds
    hits = response.json()["hits"]["hits"]

    result = {"seconds": seconds, "hits": hits}
    return result
