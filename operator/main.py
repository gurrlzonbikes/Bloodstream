import threading

import kopf
import uvicorn
from prometheus_client import start_http_server

import bloodstream.controller  # noqa: F401 — register kopf handlers
from bloodstream.execution_api import app as execution_app


def run_metrics():
    start_http_server(8080)


def run_execution_api():
    uvicorn.run(execution_app, host="0.0.0.0", port=9091, log_level="warning")


if __name__ == "__main__":
    threading.Thread(target=run_metrics, daemon=True).start()
    threading.Thread(target=run_execution_api, daemon=True).start()
    kopf.run()
