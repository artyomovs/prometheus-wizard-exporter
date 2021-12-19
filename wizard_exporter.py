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
import yaml
import urllib3
import importlib


DEBUG = strtobool(os.getenv("DEBUG", "False"))
HTTP_PORT = int(os.getenv("HTTP_PORT", "9118"))
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



def read_input_file(file_path):
    """Read input file"""

    return yaml.load(
        Path(file_path).read_text(encoding="utf_8"), Loader=yaml.FullLoader
    )


def add_prometheus_metrics(name, target):
    """Add prometheus metrics to write data in."""

    METRICS[name] = Gauge(name, target["description"])
    METRICS[f"{name}_counter"] = Counter(f"{name}_counter", target["description"])
    for metric in target.get("metrics", []):
        METRICS[metric] = Gauge(metric, f"{target.get('description', '')} {metric}")


def schedule_task(name, target):
    """Create a thread and run command by timer with custom interval."""

    imported_module = importlib.import_module(target["lib_name"])
    func = getattr(imported_module, target["func_name"])
    result = func(target.get("options", {}))
    for metric in target["metrics"]:
        METRICS[metric].set(result.get(metric, 100))
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
