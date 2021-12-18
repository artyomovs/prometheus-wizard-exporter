""" Custom prometheus exporter. Reads input from YAML."""

import json
import logging
import os
import threading
from datetime import datetime
from distutils.util import strtobool
from pathlib import Path

from prometheus_client import (
    start_http_server,
    Counter,
    Gauge,
    Info
)
import requests
import yaml
import urllib3
import importlib


DEBUG = strtobool(os.getenv("DEBUG", "False"))
HTTP_PORT = int(os.getenv("HTTP_PORT", "9118"))
HEADERS = {"Content-Type": "application/json"}
SCRIPT_PATH = str(Path(__file__).parent)
IMPUT_FILE_NAME = os.getenv("IMPUT_FILE_NAME", f"{SCRIPT_PATH}/config/wizard_exporter.yaml")

# Prometheus metrics
METRICS = {}
METRICS["main_info"] = Info("info", "Version: 0.0.1")


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_secret(secret_str):
    """Get secret from env according to prefix"""

    if not secret_str:
        result = None
    elif "ENV_" in secret_str[:4]:
        secret_str = secret_str[4:]
        secret = os.getenv(secret_str, None)
        if not secret:
            logging.error("Unable to find environment variable %s", secret_str)
            result = None
        else:
            result = secret
    else:
        result = secret_str
    return result


def read_input_file(file_path):
    """Read input file"""

    return yaml.load(
        Path(file_path).read_text(encoding="utf_8"), Loader=yaml.FullLoader
    )


def add_prometheus_metrics(name, target):
    """Add prometheus metrics to write data in."""

    METRICS[name] = Gauge(name, target["description"])
    METRICS[f"{name}_hits"] = Gauge(f"{name}_hits", f"{target['description']} hits count")
    METRICS[f"{name}_counter"] = Counter(f"{name}_counter", target["description"])


def schedule_task(name, target):
    """Create a thread and run command by timer with custom interval."""

    if target["type"].lower() == "elastic":
        username = get_secret(target["username"])
        password = get_secret(target["password"])

        start = datetime.now()
        response = requests.request(
            method="GET",
            url=target["url"],
            headers=HEADERS,
            auth=requests.auth.HTTPBasicAuth(username, password),
            data=json.dumps(target["payload"]),
            verify=False,
            timeout=120,
        )
        end = datetime.now()
        diff_seconds = (end - start).seconds

        try:
            hits = response.json()["hits"]["hits"]
            METRICS[f"{name}_hits"].set(len(hits))
            METRICS[name].set(diff_seconds)
            logging.info("%s completed. time: %i sec, hits: %i", name, diff_seconds, len(hits))
        except Exception as exception:
            logging.error("Failed to parse response: %s", str(exception))
            METRICS[name].set(1000)  # set 1000 sec. to trigger monitoring

    if target["type"].lower() == "imported_lib":
        imported_module = importlib.import_module(target["lib_name"])
        func = getattr(imported_module, target["func_name"])
        result = func()
        METRICS[name].set(result.get(target["metric_field"], 100))
        logging.error("WebSite sign in result: %s" % str(result))

    METRICS[f"{name}_counter"].inc()

    threading.Timer(target["interval"], schedule_task, [name, target]).start()


def main():
    """ Main func. """

    input_data = read_input_file(file_path=IMPUT_FILE_NAME)
    if input_data.get("default", False):
        logging.error("Exporter has been started with default yaml file!!")

    targets = input_data.get("targets", [])
    if not targets:
        logging.error("Unable to read targets in yaml")
    else:
        for n, t in targets.items():
            add_prometheus_metrics(name=n, target=t)  # add related prometheus metric
            schedule_task(name=n, target=t)
        start_http_server(HTTP_PORT)


if __name__ == "__main__":
    main()
