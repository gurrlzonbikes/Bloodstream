from fastapi import FastAPI
from pydantic import BaseModel

from .metrics import EXECUTIONS_TOTAL
from .store import STORE

app = FastAPI(title="Bloodstream Execution Ingress")


class ExecutionEvent(BaseModel):
    config: str
    trafficClass: str = "satellite"
    passed: bool = False
    driftGap: float = 0
    selectorEpoch: int = 0
    reconciledEpoch: int = 0


@app.post("/execution")
def record_execution(event: ExecutionEvent, namespace: str = "bloodstream"):
    STORE.record(event.config, event.passed, event.driftGap)
    result = "pass" if event.passed else "fail"
    EXECUTIONS_TOTAL.labels(
        config=event.config,
        traffic_class=event.trafficClass,
        result=result,
        namespace=namespace,
    ).inc()
    return {"recorded": True, "config": event.config}
